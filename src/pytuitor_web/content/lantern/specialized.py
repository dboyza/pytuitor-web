"""Offline concurrency, portable distribution, and optional game extension machinery."""

from pytuitor_web.content.lantern.authoring import api_import, milestone, public_names, scenario
from pytuitor_web.content.lantern.core import ARCHIVE_CHECKS, ARCHIVE_FILES, M11
from pytuitor_web.content.lantern.depth import (
    CONTEXT_CHECKS,
    CONTEXT_FILES,
    M16,
    M18,
    STORE_CHECKS,
    STORE_FILES,
    feature,
)
from pytuitor_web.models import code

ASYNC_SOURCE = """
    import asyncio
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def scout_station(events):
        events.append("open")
        try:
            yield events
        finally:
            events.append("closed")

    async def scout_all(sites, probe, limit=2):
        if limit < 1:
            raise ValueError("Positive concurrency limit required")
        gate = asyncio.Semaphore(limit)
        async def visit(site):
            async with gate:
                return await probe(site)
        async with asyncio.TaskGroup() as group:
            tasks = [group.create_task(visit(site)) for site in sites]
        return [task.result() for task in tasks]

    async def scout_events(sites):
        for site in sites:
            await asyncio.sleep(0)
            yield "Scout: " + site

    async def scout_preview():
        events = []
        async with scout_station(events):
            async def observe(site):
                await asyncio.sleep(0)
                return site + " clear"
            return ", ".join(await scout_all(["forest", "ridge"], observe, 2))
"""
ASYNC_FILES = feature(
    CONTEXT_FILES,
    "scouts.py",
    ASYNC_SOURCE,
    "scout_station, scout_all, scout_events, scout_preview",
    "scouts",
    '__import__("asyncio").run(scout_preview())',
)
ASYNC_CHECKS = CONTEXT_CHECKS + (
    scenario(
        "Bounded overlapping scouts preserve input order",
        """
            import asyncio


            async def exercise():
                active = 0
                peak = 0
                two_started = asyncio.Event()

                async def probe(site):
                    nonlocal active, peak
                    active += 1
                    peak = max(peak, active)
                    if active == 2:
                        two_started.set()
                    try:
                        await two_started.wait()
                        return site.upper()
                    finally:
                        active -= 1

                values = await asyncio.wait_for(scout_all(["a", "b", "c"], probe, 2), 1)
                events = [event async for event in scout_events(["forest", "ridge"])]
                return (
                    __expect__("values", values, ["A", "B", "C"], "==")
                    and __expect__("peak", peak, 2, "==")
                    and __expect__("active", active, 0, "==")
                    and __expect__(
                        "events", events, ["Scout: forest", "Scout: ridge"], "=="
                    )
                )


            result = asyncio.run(exercise()) and __expect__(
                "step(new_game(), 'scouts')",
                step(new_game(), "scouts"),
                "forest clear, ridge clear",
                "==",
            )
        """,
        "Create owned tasks under a TaskGroup and acquire a semaphore before starting each probe.",
    ),
    scenario(
        "Cancellation joins scouts and closes their station",
        """
            import asyncio


            async def exercise():
                started = asyncio.Event()
                finished = []
                log = []

                async def probe(site):
                    started.set()
                    try:
                        await asyncio.Event().wait()
                    finally:
                        finished.append(site)

                async def operation():
                    async with scout_station(log):
                        return await scout_all(["forest", "ridge"], probe, 1)

                task = asyncio.create_task(operation())
                await started.wait()
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                return __expect__(
                    "finished", finished, ["forest"], "=="
                ) and __expect__("log", log, ["open", "closed"], "==")


            result = asyncio.run(exercise())
        """,
        "Cancellation must finish child cleanup before the parent scope exits.",
    ),
)
M19 = milestone(
    chapter="async-work",
    title="Coordinate scout teams",
    capability="scouts",
    requires=M16.provides,
    base=CONTEXT_FILES,
    reference=ASYNC_FILES,
    checks=ASYNC_CHECKS,
    story=(
        "Independent scouts explore local simulated trails. Their reports must "
        "arrive safely even when the expedition is cancelled."
    ),
    teaching="## Own concurrent work for its entire lifetime\n\n"
    "TaskGroup joins owned tasks and cancels siblings on failure. A semaphore bounds active "
    "probes, not merely the number of results you keep. Use finally for cleanup and let "
    "CancelledError propagate. The sources here are offline coroutines; no network is needed. "
    "The synchronous command loop can call asyncio.run to enter the async preview.",
    requirements=(
        "Add `scouts.py`. Async context manager `scout_station(events)` "
        "appends open, yields events itself, and appends closed on every exit. "
        "`scout_all(sites, probe, limit=2)` awaits probe(site) for each site, "
        "with at most limit overlapping probes, returns results in input "
        "order, and raises ValueError for limit<1 even for empty input. Empty "
        "input returns []. Failures/cancellation must cancel and join "
        "unfinished children before returning/raising. `scout_events(sites)` "
        "is an async generator yielding `Scout: SITE` in input order. "
        "`scout_preview()` uses scout_station and scout_all with local async "
        "probes for forest/ridge, returning `forest clear, ridge clear`. "
        "Expose helpers through engine/game and add scouts to step/help using "
        "asyncio.run for the preview. Keep all prior selected capabilities."
    ),
    repair_instructions="Repair async `deliver_all(items, deliver)`: schedule all deliver(item) "
    "calls concurrently, return their results in input order, and own every task until it "
    "finishes. If one fails, cancel and join siblings before propagating failure. Parent "
    "cancellation must also join children. Empty input returns []. Use TaskGroup.",
    repair_reference="""
        import asyncio
        async def deliver_all(items, deliver):
            async with asyncio.TaskGroup() as group:
                tasks = [group.create_task(deliver(item)) for item in items]
            return [task.result() for task in tasks]
    """,
    repair_broken="""
        import asyncio
        async def deliver_all(items, deliver):
            tasks = [asyncio.create_task(deliver(item)) for item in items]
            return [await task for task in tasks]
    """,
    repair_checks=(
        scenario(
            "A failed delivery joins the waiting sibling",
            """
                import asyncio

                async def exercise():
                    gate = asyncio.Event()
                    closed = []

                    async def deliver(item):
                        if item == 'fail':
                            await gate.wait()
                            raise ValueError('blocked trail')
                        gate.set()
                        try:
                            await asyncio.Event().wait()
                        finally:
                            closed.append(item)
                    try:
                        await deliver_all(['fail', 'wait'], deliver)
                    except (ValueError, ExceptionGroup):
                        return __expect__('closed', closed, ['wait'], '==')
                    return False
                result = asyncio.run(exercise())
            """,
            (
                "A list of tasks alone does not provide failure cleanup; use "
                "structured task ownership."
            ),
        ),
    ),
    hints=(
        "Create tasks inside TaskGroup and protect each probe with a semaphore.",
        "Read task results after leaving the group so all are complete.",
        "Use try/finally inside the async context manager and keep CancelledError visible.",
    ),
    repair_hints=(
        "Observe whether a waiting sibling has cleaned up when the failure reaches its caller.",
        "TaskGroup owns cancellation and joining for all child tasks.",
    ),
    minutes=40,
)

PACKAGE_FILES = {
    **ARCHIVE_FILES,
    "lantern_reach/__init__.py": '"""An offline expedition through Lantern Reach."""\n',
    "lantern_reach/engine.py": ARCHIVE_FILES["engine.py"],
    "lantern_reach/cli.py": code("""
        import argparse
        from pathlib import Path
        from . import engine


        def read_story(path):
            return Path(path).read_text(encoding="utf-8")


        def main(argv=None):
            parser = argparse.ArgumentParser(
                description="Explore Lantern Reach offline."
            )
            parser.add_argument("--name", default="Explorer")
            parser.add_argument("--seed", type=int, default=0)
            parser.add_argument(
                "--story", metavar="PATH", help="Print a UTF-8 story file and exit"
            )
            args = parser.parse_args(argv)
            if args.story is not None:
                try:
                    print(read_story(args.story))
                except OSError as error:
                    parser.exit(1, "Cannot read story: " + str(error) + "\\n")
                return 0
            engine.main(["--name", args.name, "--seed", str(args.seed)])
            return 0
    """),
    "lantern_reach/__main__.py": code("""
        from .cli import main

        raise SystemExit(main())
    """),
    "pyproject.toml": """[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "lantern-reach"
version = "1.0.0"
description = "An offline expedition and settlement game"
requires-python = ">=3.11"

[project.scripts]
lantern-reach = "lantern_reach.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["lantern_reach"]
""",
    ("README.md"): "# Lantern Reach\n\nRun `python game.py` or `python -m "
    "lantern_reach`.\nUse `help` to discover game commands.\nThe source "
    "runs offline with Python 3.11 or newer and no third-party runtime "
    "packages.\nBuild/install tooling may need an explicitly requested "
    "download.\n",
}
PACKAGE_FILES["engine.py"] = api_import(
    "lantern_reach.engine", public_names(ARCHIVE_FILES["engine.py"])
)
PACKAGE_FILES["game.py"] = (
    api_import(
        "lantern_reach.engine",
        tuple(name for name in public_names(ARCHIVE_FILES["engine.py"]) if name != "main"),
    )
    + 'from lantern_reach.cli import main\n\nif __name__ == "__main__":\n    main()\n'
)
PACKAGE_CHECKS = ARCHIVE_CHECKS + (
    scenario(
        "Package metadata and quiet reusable entrypoints",
        """
            import contextlib, importlib, io, tomllib
            from pathlib import Path

            metadata = tomllib.loads(Path("pyproject.toml").read_text())
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                importlib.import_module("lantern_reach")
                cli = importlib.import_module("lantern_reach.cli")
            Path("story space.txt").write_text("The beacon shines.", encoding="utf-8")
            with contextlib.redirect_stdout(capture):
                status = cli.main(["--story", "story space.txt"])
            result = (
                __expect__(
                    "metadata['project']['scripts']['lantern-reach']",
                    metadata["project"]["scripts"]["lantern-reach"],
                    "lantern_reach.cli:main",
                    "==",
                )
                and __expect__(
                    "metadata['project']['requires-python']",
                    metadata["project"]["requires-python"],
                    ">=3.11",
                    "==",
                )
                and __expect__("status", status, 0, "==")
                and __expect__(
                    "capture.getvalue()",
                    capture.getvalue(),
                    "The beacon shines.\\n",
                    "==",
                )
            )
        """,
        (
            "Keep imports quiet, declare the CLI entrypoint, and read the explicit "
            "path supplied by the caller."
        ),
    ),
    scenario(
        "CLI errors remain visible and help exits successfully",
        """
            import contextlib, io
            from lantern_reach.cli import main as cli_main

            codes = []
            with (
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                for args in (
                    ["--help"],
                    ["--not-an-option"],
                    ["--story", "missing-story.txt"],
                ):
                    try:
                        cli_main(args)
                    except SystemExit as error:
                        codes.append(error.code)
            result = __expect__("codes", codes, [0, 2, 1], "==")
        """,
        "Use argparse's help/error behavior and a distinct nonzero status for missing files.",
    ),
)
M20 = milestone(
    chapter="distributable-tools",
    title="Share the expedition",
    capability="package",
    requires=M11.provides,
    base=ARCHIVE_FILES,
    reference=PACKAGE_FILES,
    checks=PACKAGE_CHECKS,
    story="Your game is ready to leave the tutor. Give another player a predictable way to run it.",
    teaching="## A package has a public entrance\n\n"
    "Move your engine into a lantern_reach package and use relative imports inside that package. "
    "Keep game.py as a source launcher and engine.py as a compatibility re-export for earlier "
    "tests. A console-script declaration points to a callable, not a script path. "
    "Hatchling is build tooling, not a runtime dependency; building may require an explicit "
    "tool download, while the exported source remains runnable offline. "
    "This chapter does not require the async extension.",
    requirements="Create package files `lantern_reach/__init__.py`, `engine.py`, "
    "`cli.py`, and `__main__.py`. "
    "Move your core game engine into the package; imports must stay quiet. Root `engine.py` "
    "re-exports the packaged API for existing tests; root `game.py` "
    "re-exports it and runs cli.main "
    "under its `__name__` guard. Keep all previous game behavior.\n\n"
    "`cli.main(argv=None)` supports --name and integer --seed, "
    "delegates normal play to the engine, "
    "and returns 0. --story PATH reads UTF-8 using `read_story(path)`, prints it, and returns 0. "
    "A missing story exits 1 with a useful stderr message; argparse "
    "errors exit 2 and help exits 0. "
    "`python -m lantern_reach` must run the same CLI. Paths are "
    "caller-supplied, including spaces.\n\n"
    "Write `pyproject.toml` for project lantern-reach version 1.0.0, requires-python >=3.11, "
    "no third-party runtime dependencies, Hatchling build backend, wheel package lantern_reach, "
    "and script lantern-reach = 'lantern_reach.cli:main'. Add a README with source-run and "
    "package-run instructions and explicit build-tool requirements. If carrying extra extension "
    "modules, move them into the package too and update their relative imports deliberately.",
    repair_instructions="Repair `main(argv=None)` for a trail-report CLI. argparse must require "
    "--count as an integer, accept --label defaulting to trail, print `LABEL: COUNT`, and return "
    "0 on success. Preserve argparse's exit 2 on missing/invalid arguments and exit 0 on help. "
    "Importing the module must not run main. Option order must not matter.",
    repair_reference="""
        import argparse
        def main(argv=None):
            parser = argparse.ArgumentParser()
            parser.add_argument("--count", type=int, required=True)
            parser.add_argument("--label", default="trail")
            args = parser.parse_args(argv)
            print(f"{args.label}: {args.count}")
            return 0
    """,
    repair_broken="""
        import argparse
        def main(argv=None):
            parser = argparse.ArgumentParser()
            parser.add_argument("--count", default=0)
            parser.add_argument("--label", default="trail")
            try:
                args = parser.parse_args(argv)
            except SystemExit:
                return 0
            print(f"{args.label}: {args.count}")
            return 0
    """,
    repair_checks=(
        scenario(
            "Parser failures and option order",
            """
                import io, contextlib

                capture = io.StringIO()
                codes = []
                with (
                    contextlib.redirect_stdout(capture),
                    contextlib.redirect_stderr(io.StringIO()),
                ):
                    ok = main(["--label", "ridge", "--count", "2"])
                    for args in ([], ["--count", "bad"]):
                        try:
                            main(args)
                        except SystemExit as error:
                            codes.append(error.code)
                result = (
                    __expect__("ok", ok, 0, "==")
                    and capture.getvalue().startswith("ridge: 2\\n")
                    and __expect__("codes", codes, [2, 2], "==")
                )
            """,
            "Declare required and integer constraints on the parser; do not swallow SystemExit.",
        ),
    ),
    hints=(
        "Move your source rather than copying an author's new engine over it.",
        "Keep the root compatibility module small and guard only entrypoint execution.",
        "Let argparse report argument errors; handle missing story files with exit 1.",
    ),
    repair_hints=(
        "A default value is not the same as a required option.",
        "Let argparse raise its documented exit code instead of converting errors into success.",
    ),
    minutes=40,
)

FORMAT_SOURCE = """
    import inspect

    class Nonnegative:
        def __set_name__(self, owner, name):
            self.storage = "_" + name
        def __get__(self, instance, owner=None):
            if instance is None:
                return self
            return instance.__dict__.get(self.storage, 0)
        def __set__(self, instance, value):
            if type(value) is not int or value < 0:
                raise ValueError("Nonnegative integer required")
            instance.__dict__[self.storage] = value

    class FormatterMeta(type):
        registry = {}
        def __new__(metaclass, name, bases, namespace):
            key = namespace.get("format_name")
            if key is not None and key in metaclass.registry:
                raise ValueError("Duplicate formatter: " + key)
            created = super().__new__(metaclass, name, bases, namespace)
            if key is not None:
                metaclass.registry[key] = created
            return created

    class Formatter(metaclass=FormatterMeta):
        format_name = None
        uses = Nonnegative()
        def render(self, text):
            self.uses += 1
            return text

    class PlainFormatter(Formatter):
        format_name = "plain"

    class TrailPrefix:
        def render(self, text):
            return "Trail: " + super().render(text)

    class TrailFormatter(TrailPrefix, Formatter):
        format_name = "trail"

    def formatter_parameters(formatter):
        return list(inspect.signature(formatter.render).parameters)

    def render_with(name, text):
        return FormatterMeta.registry[name]().render(text)
"""
FORMAT_FILES = feature(
    STORE_FILES,
    "formatters.py",
    FORMAT_SOURCE,
    (
        "Nonnegative, FormatterMeta, Formatter, PlainFormatter, TrailPrefix, "
        "TrailFormatter, formatter_parameters, render_with"
    ),
    "formatters",
    'render_with("trail", "The beacon shines.")',
)
FORMAT_CHECKS = STORE_CHECKS + (
    scenario(
        "Per-instance descriptor validation and cooperative formatting",
        """
            left, right = (TrailFormatter(), TrailFormatter())
            message = left.render("home")
            rejected = False
            try:
                left.uses = -1
            except ValueError:
                rejected = True


            class Loud(Formatter):
                def render(self, text):
                    return super().render(text.upper())


            class LoudTrail(TrailPrefix, Loud):
                pass


            result = (
                __expect__("message", message, "Trail: home", "==")
                and __expect__("left.uses", left.uses, 1, "==")
                and __expect__("right.uses", right.uses, 0, "==")
                and rejected
                and isinstance(Formatter.uses, Nonnegative)
                and __expect__(
                    "LoudTrail().render('home')",
                    LoudTrail().render("home"),
                    "Trail: HOME",
                    "==",
                )
                and __expect__(
                    "step(new_game(), 'formatters')",
                    step(new_game(), "formatters"),
                    "Trail: The beacon shines.",
                    "==",
                )
            )
        """,
        (
            "Store descriptor values on the instance and use super so the current "
            "MRO determines the next method."
        ),
    ),
    scenario(
        "Dynamic registration, duplicate protection, and inert inspection",
        """
            before = dict(FormatterMeta.registry)
            duplicate = False
            try:

                class Duplicate(Formatter):
                    format_name = "plain"
            except ValueError:
                duplicate = True
            preserved = __expect__(
                "FormatterMeta.registry", FormatterMeta.registry, before, "=="
            )


            class Brackets(Formatter):
                format_name = "brackets"

                def render(self, text):
                    return "[" + super().render(text) + "]"


            instance = Brackets()
            parameters = formatter_parameters(instance)
            result = (
                duplicate
                and preserved
                and __expect__(
                    "render_with('brackets', 'home')",
                    render_with("brackets", "home"),
                    "[home]",
                    "==",
                )
                and __expect__("parameters", parameters, ["text"], "==")
                and __expect__("instance.uses", instance.uses, 0, "==")
            )
        """,
        (
            "Reject duplicates before changing the registry and inspect signatures "
            "without calling render."
        ),
    ),
)
M21 = milestone(
    chapter="python-machinery",
    title="Add journal formatters",
    capability="formatters",
    requires=M18.provides,
    base=STORE_FILES,
    reference=FORMAT_FILES,
    checks=FORMAT_CHECKS,
    story=(
        "Give expedition journals new formats through explicit Python "
        "extension classes, without changing the reporting core."
    ),
    teaching="## Optional machinery with visible contracts\n\n"
    "A descriptor stores validated values per instance. A metaclass can register newly created "
    "formatter classes; reject duplicates before updating the registry. A mixin's super call "
    "follows the current method resolution order, including classes added later. "
    "inspect.signature describes an operation without executing it. This is optional depth, "
    "not a requirement for writing a small game.",
    requirements=(
        "Add formatters.py. Descriptor Nonnegative defaults to 0 per instance, "
        "accepts only nonnegative integers (not bool), and returns itself on "
        "class access. FormatterMeta.registry maps explicit non-None "
        "format_name values from newly declared classes to those classes; "
        "reject duplicates with ValueError without modifying the registry. "
        "Formatter has format_name=None, uses=Nonnegative(), and render(text) "
        "increments uses and returns text. PlainFormatter registers plain. "
        "TrailPrefix.render prefixes `Trail: ` to super().render(text). "
        "TrailFormatter(TrailPrefix, Formatter) registers trail. "
        "`formatter_parameters(instance)` returns parameter names of its bound "
        "render method without calling it. `render_with(name, text)` creates "
        "the currently registered class and renders text. Dynamic subclasses "
        "must work. Expose the API through engine/game, and add formatters "
        "returning `Trail: The beacon shines.` plus a help entry. Packaging is "
        "not required."
    ),
    repair_instructions="Repair descriptor `PositiveCount` and class `Cache` using it as count. "
    "Each instance defaults to zero and owns its value. Allow nonnegative integers only, "
    "reject bool and negatives with ValueError before mutation, and return the descriptor "
    "itself when accessed on Cache. Use __set_name__ to derive an instance storage key.",
    repair_reference="""
        class PositiveCount:
            def __set_name__(self, owner, name):
                self.key = "_" + name
            def __get__(self, instance, owner=None):
                return self if instance is None else instance.__dict__.get(self.key, 0)
            def __set__(self, instance, value):
                if type(value) is not int or value < 0:
                    raise ValueError("Nonnegative integer required")
                instance.__dict__[self.key] = value
        class Cache:
            count = PositiveCount()
    """,
    repair_broken="""
        class PositiveCount:
            value = 0
            def __get__(self, instance, owner=None):
                return self.value
            def __set__(self, instance, value):
                self.value = abs(value)
        class Cache:
            count = PositiveCount()
    """,
    repair_checks=(
        scenario(
            "Descriptor ownership and class access",
            """
                left, right = (Cache(), Cache())
                left.count = 3
                rejected = 0
                for value in (-1, True):
                    try:
                        left.count = value
                    except ValueError:
                        rejected += 1
                result = (
                    __expect__("left.count", left.count, 3, "==")
                    and __expect__("right.count", right.count, 0, "==")
                    and __expect__("rejected", rejected, 2, "==")
                    and isinstance(Cache.count, PositiveCount)
                )
            """,
            (
                "The descriptor object is shared, so actual values belong in each "
                "instance's dictionary."
            ),
        ),
    ),
    hints=(
        "Implement descriptor class access before instance access.",
        "Register only names explicitly declared in the new class namespace.",
        "Use super instead of directly calling Formatter.render in the mixin.",
    ),
    repair_hints=(
        "A value stored on the descriptor is shared by every Cache.",
        "Validate first and store under an instance-specific dictionary key.",
    ),
    minutes=40,
)
SPECIALIZED = (M19, M20, M21)
