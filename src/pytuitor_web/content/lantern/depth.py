"""Optional game extensions with explicit preparation and independent entry paths."""

from pytuitor_web.content.lantern.authoring import milestone, scenario
from pytuitor_web.content.lantern.core import ARCHIVE_CHECKS, ARCHIVE_FILES, M11, extend
from pytuitor_web.models import Check, code


def feature(base, filename, source, imports, command, expression):
    """Build an authored snapshot with an explicit, visible game integration."""
    files = dict(base)
    files[filename] = code(source)
    module = filename.removesuffix(".py")
    return extend(
        files,
        f"""
        from {module} import {imports}

        _before_{command} = step

        def step(state, command):
            cleaned = command.strip().lower()
            if cleaned == {command!r}:
                return {expression}
            if cleaned == "help":
                return _before_{command}(state, command) + {", " + command!r}
            return _before_{command}(state, command)
    """,
    )


COPY_SOURCE = """
    import copy

    def branch_state(state, **changes):
        branch = copy.deepcopy(state)
        branch.update(copy.deepcopy(changes))
        return branch

    def choose_value(value, fallback):
        return fallback if value is None else value
"""
COPY_FILES = feature(
    ARCHIVE_FILES,
    "branches.py",
    COPY_SOURCE,
    "branch_state, choose_value",
    "branch",
    '"Branch starts at " + branch_state(state)["location"] + "; original preserved."',
)
COPY_CHECKS = ARCHIVE_CHECKS + (
    scenario(
        "Nested branches own their contents and preserve falsy choices",
        """
            original = new_game()
            changes = {"visits": []}
            branch = branch_state(original, notes=changes)
            branch["supplies"]["wood"] = 9
            branch["notes"]["visits"].append("cave")
            result = (
                __expect__(
                    "original['supplies']['wood']",
                    original["supplies"]["wood"],
                    0,
                    "==",
                )
                and __expect__("changes", changes, {"visits": []}, "==")
                and __expect__("choose_value(0, 7)", choose_value(0, 7), 0, "==")
                and __expect__(
                    "choose_value('', 'fallback')",
                    choose_value("", "fallback"),
                    "",
                    "==",
                )
                and __expect__(
                    "choose_value(None, 'fallback')",
                    choose_value(None, "fallback"),
                    "fallback",
                    "==",
                )
                and ("original preserved" in step(original, "branch"))
            )
        """,
        (
            "Deep-copy both the base state and mutable replacement values; only "
            "None requests the fallback."
        ),
    ),
)
M12 = milestone(
    chapter="python-semantics",
    title="Try another route",
    capability="branches",
    requires=M11.provides,
    base=ARCHIVE_FILES,
    reference=COPY_FILES,
    checks=COPY_CHECKS,
    story=(
        "Try an alternate expedition without changing the supplies of the "
        "journey you already completed."
    ),
    teaching="## A new outer dictionary is not a new world\n\n"
    "A shallow copy retains references to nested objects. Use copy.deepcopy when the contract "
    "requires independent nested state. Distinguish a missing choice "
    "from valid zero or empty text; "
    "`value or fallback` replaces all falsy values, not only None.",
    requirements=(
        "Add `branches.py`. `branch_state(state, **changes)` deep-copies state "
        "and applies independently copied keyword replacements, without "
        "mutating state or changes. `choose_value(value, fallback)` returns "
        "fallback only for None, preserving 0, False, '', and []. "
        "Import/re-export these helpers through engine and game. Add a "
        "`branch` command returning `Branch starts at LOCATION; original "
        "preserved.` using an independent branch; it must not change the "
        "active expedition. Include branch in help and keep all previous "
        "commands."
    ),
    repair_instructions="Repair `preview_route(state, location=None)`: return an independent "
    "deep copy with location replaced only when the argument is not None. Preserve an explicitly "
    "empty location string. Editing the preview's nested supplies must not alter the source.",
    repair_reference="""
        import copy
        def preview_route(state, location=None):
            preview = copy.deepcopy(state)
            if location is not None:
                preview["location"] = location
            return preview
    """,
    repair_broken="""
        def preview_route(state, location=None):
            preview = state.copy()
            preview["location"] = location or state["location"]
            return preview
    """,
    repair_checks=(
        scenario(
            "Preview independence and explicit empty choice",
            """
                state = {"location": "outpost", "supplies": {"wood": 2}}
                preview = preview_route(state, "")
                preview["supplies"]["wood"] = 8
                result = (
                    __expect__("preview['location']", preview["location"], "", "==")
                    and __expect__("Wood remaining", state["supplies"]["wood"], 2, "==")
                    and __expect__(
                        "preview_route(state)['location']",
                        preview_route(state)["location"],
                        "outpost",
                        "==",
                    )
                )
            """,
            "A shallow outer copy still shares the nested supplies dictionary.",
        ),
    ),
    hints=(
        "Deep-copy before applying replacements.",
        "Replacement values can contain mutable objects too.",
        "Test None explicitly rather than testing general truthiness.",
    ),
    repair_hints=(
        "Try editing a nested value in the preview.",
        "None means keep the old location; empty text is still an explicit choice.",
    ),
)

ROUTE_SOURCE = """
    def flatten_routes(tree):
        routes = []
        for item in tree:
            if isinstance(item, list):
                routes.extend(flatten_routes(item))
            else:
                routes.append(item)
        return routes

    def rank_routes(routes, key=None, reverse=False):
        return sorted(routes, key=key, reverse=reverse)
"""
ROUTE_FILES = feature(
    COPY_FILES,
    "routes.py",
    ROUTE_SOURCE,
    "flatten_routes, rank_routes",
    "caves",
    '", ".join(flatten_routes(["entrance", ["pool", [], ["crystal chamber"]]]))',
)
ROUTE_CHECKS = COPY_CHECKS + (
    scenario(
        "Nested empty paths and stable callable ranking",
        """
            tree = ["gate", [], ["pool", ["vault"]], "exit"]
            result = (
                __expect__(
                    "flatten_routes(tree)",
                    flatten_routes(tree),
                    ["gate", "pool", "vault", "exit"],
                    "==",
                )
                and __expect__("flatten_routes([])", flatten_routes([]), [], "==")
                and __expect__(
                    "rank_routes(['aa', 'b', 'cc'], key=len)",
                    rank_routes(["aa", "b", "cc"], key=len),
                    ["b", "aa", "cc"],
                    "==",
                )
                and __expect__(
                    "tree", tree, ["gate", [], ["pool", ["vault"]], "exit"], "=="
                )
                and __expect__(
                    "step(new_game(), 'caves')",
                    step(new_game(), "caves"),
                    "entrance, pool, crystal chamber",
                    "==",
                )
            )
        """,
        (
            "An empty nested list contributes no routes; sorted accepts a callable "
            "without mutating its input."
        ),
    ),
)
M13 = milestone(
    chapter="recursion-and-callables",
    title="Explore the cave network",
    capability="caves",
    requires=M12.provides,
    base=COPY_FILES,
    reference=ROUTE_FILES,
    checks=ROUTE_CHECKS,
    story=(
        "Below the ridge, cave branches contain more branches. Follow every "
        "named place without losing the order."
    ),
    teaching="## A smaller version of the same question\n\n"
    "When a route item is a list, explore that smaller list; when it is a name, keep the name. "
    "An empty list is the base case. A sorting key is a function that computes a comparison "
    "value, so key=len orders names by length while retaining ties in their previous order.",
    requirements=(
        "Add `routes.py` with `flatten_routes(tree)` returning all string "
        "leaves of a nested list in depth-first, left-to-right order. Input "
        "contains strings and lists only, including empty lists; never mutate "
        "it. `rank_routes(routes, key=None, reverse=False)` returns a stable "
        "sorted copy using the caller's key function and reverse setting. "
        "Expose both helpers through engine/game. Add `caves` returning "
        "`entrance, pool, crystal chamber` by traversing ['entrance', ['pool', "
        "[], ['crystal chamber']]], and list caves in help."
    ),
    repair_instructions="Repair `count_caches(tree)` to count string leaves in arbitrarily "
    "nested lists, including zero for an empty list. Do not count nested list objects as caches "
    "and do not stop after the first nested branch. Preserve the input.",
    repair_reference="""
        def count_caches(tree):
            total = 0
            for item in tree:
                total += count_caches(item) if isinstance(item, list) else 1
            return total
    """,
    repair_broken="""
        def count_caches(tree):
            total = 0
            for item in tree:
                if isinstance(item, list):
                    return count_caches(item)
                total += 1
            return total
    """,
    repair_checks=(
        Check(
            "All branches contribute",
            "[count_caches([]), count_caches(['a', ['b', [], ['c']], 'd'])]",
            [0, 4],
            "Accumulate recursive results instead of returning before later siblings.",
        ),
    ),
    hints=(
        "Use a result list and extend it with recursive results.",
        "Append a string leaf; extend a list of leaves.",
        "Use sorted rather than list.sort to preserve the caller's sequence.",
    ),
    repair_hints=(
        "A return inside the loop ends the entire traversal.",
        "Add each recursive count to the running total.",
    ),
)

DECORATOR_SOURCE = """
    from functools import wraps

    def record_actions(events, label):
        def decorate(function):
            @wraps(function)
            def wrapped(*args, **kwargs):
                result = function(*args, **kwargs)
                events.append(label)
                return result
            return wrapped
        return decorate

    def preview_recording():
        events = []
        @record_actions(events, "survey")
        def survey(*, place):
            return place
        place = survey(place="ridge")
        return place + ": " + ", ".join(events)
"""
DECORATOR_FILES = feature(
    ROUTE_FILES,
    "actions.py",
    DECORATOR_SOURCE,
    "record_actions, preview_recording",
    "actions",
    "preview_recording()",
)
DECORATOR_CHECKS = ROUTE_CHECKS + (
    scenario(
        "Recording preserves calls, metadata, failures, and stacking order",
        '''
            events = []


            def operation(value=0):
                """Original operation."""
                if value < 0:
                    raise ValueError("negative")
                return value


            wrapped = record_actions(events, "outer")(
                record_actions(events, "inner")(operation)
            )
            value = wrapped(value=0)
            try:
                wrapped(value=-1)
            except ValueError:
                pass
            result = (
                __expect__("value", value, 0, "==")
                and __expect__("events", events, ["inner", "outer"], "==")
                and __expect__("wrapped.__name__", wrapped.__name__, "operation", "==")
                and __expect__(
                    "wrapped.__doc__", wrapped.__doc__, operation.__doc__, "=="
                )
                and __expect__(
                    "step(new_game(), 'actions')",
                    step(new_game(), "actions"),
                    "ridge: survey",
                    "==",
                )
            )
        ''',
        "Append only after successful completion, return falsy results unchanged, and use wraps.",
    ),
)
M14 = milestone(
    chapter="decorators",
    title="Record expedition actions",
    capability="actions",
    requires=M13.provides,
    base=ROUTE_FILES,
    reference=DECORATOR_FILES,
    checks=DECORATOR_CHECKS,
    story="Record completed field operations without copying logging code into every operation.",
    teaching="## Configuration, decoration, and calling happen at different times\n\n"
    "The outer function receives configuration, its inner decorator receives a function, and "
    "the wrapper receives each call's arguments. functools.wraps preserves useful metadata. "
    "Place success recording after the original call so exceptions remain exceptions.",
    requirements="Add `actions.py`: `record_actions(events, label)` returns a decorator. "
    "Its wrapper forwards all arguments unchanged, returns the original result, preserves "
    "name/docstring with wraps, and appends label exactly once after each successful call. "
    "Failed calls propagate their exception without recording success. Stacked decorators "
    "record inner before outer. `preview_recording()` decorates a local keyword-only survey "
    "operation, calls it for ridge, and returns `ridge: survey`. Expose helpers through "
    "engine/game; `actions` returns that preview and appears in help.",
    repair_instructions="Repair decorator `count_successes(fn)`. Its wrapper has a `calls` "
    "attribute initialized to 0, incremented only when fn returns normally. Forward positional "
    "and keyword arguments, preserve fn's metadata, return all results including falsy values, "
    "and propagate exceptions. Each decorated function owns its counter.",
    repair_reference="""
        from functools import wraps
        def count_successes(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                result = fn(*args, **kwargs)
                wrapper.calls += 1
                return result
            wrapper.calls = 0
            return wrapper
    """,
    repair_broken="""
        def count_successes(fn):
            def wrapper(*args, **kwargs):
                wrapper.calls += 1
                return fn(*args) or None
            wrapper.calls = 0
            return wrapper
    """,
    repair_checks=(
        scenario(
            "Counter ignores failed calls and preserves zero",
            """
                def divide(*, value):
                    return 0 // value


                wrapped = count_successes(divide)
                answer = wrapped(value=1)
                try:
                    wrapped(value=0)
                except ZeroDivisionError:
                    pass
                result = (
                    __expect__("answer", answer, 0, "==")
                    and __expect__("wrapped.calls", wrapped.calls, 1, "==")
                    and __expect__("wrapped.__name__", wrapped.__name__, "divide", "==")
                    and __expect__(
                        "count_successes(divide).calls",
                        count_successes(divide).calls,
                        0,
                        "==",
                    )
                )
            """,
            (
                "Success is recorded after the call; keyword arguments and zero must "
                "survive unchanged."
            ),
        ),
    ),
    hints=(
        "Write the three nested functions with distinct responsibilities.",
        "Call first, append second, return the result third.",
        "Use wraps on the innermost function.",
    ),
    repair_hints=(
        "The increment currently happens even when the call raises.",
        "Pass kwargs as well as args and return the exact result.",
    ),
)

STREAM_SOURCE = """
    from itertools import islice

    def matching_events(events, kind):
        for event in events:
            if event["kind"] == kind:
                yield event["text"]

    def chronicle(events, kind, limit):
        if limit < 0:
            raise ValueError("Negative limit")
        return list(islice(matching_events(events, kind), limit))
"""
STREAM_FILES = feature(
    COPY_FILES,
    "chronicle.py",
    STREAM_SOURCE,
    "matching_events, chronicle",
    "chronicle",
    (
        '" | ".join(chronicle(iter([{"kind": "quest", "text": "Mira waits by '
        'the beacon."}, {"kind": "travel", "text": "A trail opens."}]), '
        '"quest", 1))'
    ),
)
STREAM_CHECKS = COPY_CHECKS + (
    scenario(
        "Bounded one-pass consumption including zero",
        """
            seen = []


            def events():
                for event in [
                    {"kind": "travel", "text": "walk"},
                    {"kind": "quest", "text": "help"},
                ]:
                    seen.append(event)
                    yield event
                raise AssertionError("overconsumed")


            first = chronicle(events(), "quest", 1)
            empty = chronicle(events(), "quest", 0)
            result = (
                __expect__("first", first, ["help"], "==")
                and __expect__("empty", empty, [], "==")
                and __expect__("len(seen)", len(seen), 2, "==")
                and __expect__(
                    "step(new_game(), 'chronicle')",
                    step(new_game(), "chronicle"),
                    "Mira waits by the beacon.",
                    "==",
                )
            )
        """,
        "Stop immediately after the requested matching item; limit zero must not touch the source.",
    ),
)
M15 = milestone(
    chapter="iterators-and-streaming",
    title="Read the expedition chronicle",
    capability="chronicle",
    requires=M12.provides,
    base=COPY_FILES,
    reference=STREAM_FILES,
    checks=STREAM_CHECKS,
    story=(
        "A long expedition can produce more events than you want to read. Show "
        "only the requested part."
    ),
    teaching="## A stream is consumed as you ask for values\n\n"
    "Yield matching entries without first building a complete list. itertools.islice can "
    "stop after the requested number. The source may be one-pass or infinite, so reading "
    "an extra item is observable behavior, not merely a performance detail.",
    requirements=(
        "Add `chronicle.py`. `matching_events(events, kind)` lazily yields "
        "each matching event's text in order from a one-pass iterable of "
        "{kind, text} dictionaries. `chronicle(events, kind, limit)` returns "
        "at most limit matching texts, raises ValueError for negative limit, "
        "and never consumes beyond the last needed match. Zero consumes "
        "nothing. Expose both functions from engine/game. Add a `chronicle` "
        "command demonstrating a quest event and a travel event with limit 1, "
        "returning `Mira waits by the beacon.`; list it in help."
    ),
    repair_instructions="Repair generator `windows(events, size)` to yield overlapping tuples "
    "of exactly size consecutive values from a one-pass iterable. Reject size <= 0 with "
    "ValueError when iteration starts. Yield nothing for a shorter source. Never eagerly "
    "consume the entire iterable; requesting the first window consumes exactly size items.",
    repair_reference="""
        from collections import deque
        def windows(events, size):
            if size <= 0:
                raise ValueError("Positive window size required")
            window = deque(maxlen=size)
            for event in events:
                window.append(event)
                if len(window) == size:
                    yield tuple(window)
    """,
    repair_broken="""
        def windows(events, size):
            values = list(events)
            for index in range(0, len(values), size):
                yield tuple(values[index:index + size])
    """,
    repair_checks=(
        scenario(
            "Overlapping windows without eager reads",
            """
                seen = []


                def source():
                    for value in range(5):
                        seen.append(value)
                        yield value


                stream = windows(source(), 2)
                first = next(stream)
                bounded = __expect__("seen", seen, [0, 1], "==")
                result = (
                    __expect__("first", first, (0, 1), "==")
                    and bounded
                    and __expect__(
                        "list(stream)", list(stream), [(1, 2), (2, 3), (3, 4)], "=="
                    )
                    and __expect__(
                        "list(windows(iter([1]), 2))", list(windows(iter([1]), 2)), [], "=="
                    )
                )
            """,
            "Use a fixed-size rolling buffer and yield each full overlapping window.",
        ),
    ),
    hints=(
        "A generator keeps the filtering lazy.",
        "Use islice on matching_events, not on the original input before filtering.",
        "Check the limit before creating a result list.",
    ),
    repair_hints=(
        "Converting events to list consumes everything before the first result.",
        "Slide one event at a time and yield only full buffers.",
    ),
)

CONTEXT_SOURCE = """
    from contextlib import contextmanager

    class StationError(Exception):
        pass

    def read_station_number(text):
        try:
            return int(text)
        except ValueError as error:
            raise StationError("Invalid station number") from error

    @contextmanager
    def temporary_station(state, location):
        previous = state["location"]
        state["location"] = location
        try:
            yield state
        finally:
            state["location"] = previous

    class StationVisit:
        def __init__(self, state, location):
            self.state, self.location = state, location
        def __enter__(self):
            self.previous = self.state["location"]
            self.state["location"] = self.location
            return self.state
        def __exit__(self, exc_type, exc, traceback):
            self.state["location"] = self.previous
            return False

    def station_preview(state):
        with temporary_station(state, "field station") as active:
            return "Visited " + active["location"] + "; return route preserved."
"""
# Both context-manager forms need decorators and generators.
# Their preparation follows capabilities rather than incidental chapter order.
CONTEXT_BASE = dict(DECORATOR_FILES)
CONTEXT_BASE["chronicle.py"] = STREAM_FILES["chronicle.py"]
# Add streaming's public functions and command without replacing any decorator code.
CONTEXT_BASE = feature(
    CONTEXT_BASE,
    "chronicle.py",
    STREAM_SOURCE,
    "matching_events, chronicle",
    "chronicle",
    (
        '" | ".join(chronicle(iter([{"kind": "quest", "text": "Mira waits by '
        'the beacon."}]), "quest", 1))'
    ),
)
CONTEXT_FILES = feature(
    CONTEXT_BASE,
    "stations.py",
    CONTEXT_SOURCE,
    "StationError, read_station_number, temporary_station, StationVisit, station_preview",
    "station",
    "station_preview(state)",
)
CONTEXT_CHECKS = (
    DECORATOR_CHECKS
    + STREAM_CHECKS[len(COPY_CHECKS) :]
    + (
        scenario(
            "Nested contexts restore state and retain the original cause",
            """
                state = new_game()
                raised = False
                try:
                    with temporary_station(state, "ridge") as outer:
                        with StationVisit(state, "forest") as inner:
                            assert inner is state and outer is state
                            raise RuntimeError("storm")
                except RuntimeError:
                    raised = True
                chained = False
                try:
                    read_station_number("bad")
                except StationError as error:
                    chained = isinstance(error.__cause__, ValueError)
                result = (
                    raised
                    and __expect__("state['location']", state["location"], "outpost", "==")
                    and chained
                    and ("return route preserved" in step(state, "station"))
                    and __expect__("state['location']", state["location"], "outpost", "==")
                )
            """,
            (
                "Restore in finally/__exit__, return False to propagate errors, and "
                "use explicit exception chaining."
            ),
        ),
    )
)
M16 = milestone(
    chapter="exceptions-and-contexts",
    title="Recover the field station",
    capability="stations",
    requires=tuple(dict.fromkeys((*M14.provides, *M15.provides))),
    base=CONTEXT_BASE,
    reference=CONTEXT_FILES,
    checks=CONTEXT_CHECKS,
    story=(
        "A field visit may fail during a storm. The explorer still needs a reliable return route."
    ),
    teaching="## A temporary change needs a guaranteed exit\n\n"
    "A context manager restores state even when the body raises. A generator context manager "
    "puts restoration in finally; a class context manager returns False from __exit__ to "
    "avoid suppressing the error. `raise NewError(...) from original` records the useful cause.",
    requirements=(
        "Add `stations.py` with StationError(Exception). "
        "`read_station_number(text)` returns int(text), translating ValueError "
        "into StationError with the original cause. `temporary_station(state, "
        "location)` is a context manager yielding the same state object after "
        "temporarily changing location, then restoring the previous location "
        "on every exit. `StationVisit(state, location)` implements the class "
        "context-manager protocol with the same behavior, including nested "
        "visits and error propagation. `station_preview(state)` uses a "
        "temporary visit to field station and returns `Visited field station; "
        "return route preserved.`. Expose helpers through engine/game and add "
        "`station` to the commands and help."
    ),
    repair_instructions="Repair context manager `temporary_flag(settings, key, value)`: install "
    "the temporary value, yield settings itself, and restore exactly the prior mapping on "
    "exit, even after an exception. If the key was originally absent, remove it rather than "
    "setting None. Preserve errors raised in the with body.",
    repair_reference="""
        from contextlib import contextmanager
        @contextmanager
        def temporary_flag(settings, key, value):
            existed = key in settings
            previous = settings.get(key)
            settings[key] = value
            try:
                yield settings
            finally:
                if existed:
                    settings[key] = previous
                else:
                    del settings[key]
    """,
    repair_broken="""
        from contextlib import contextmanager
        @contextmanager
        def temporary_flag(settings, key, value):
            previous = settings.get(key)
            settings[key] = value
            yield settings
            settings[key] = previous
    """,
    repair_checks=(
        scenario(
            "Absent keys and exceptional exit",
            """
                settings = {'quiet': False}
                caught = False
                try:
                    with temporary_flag(settings, 'new', True) as active:
                        assert active is settings
                        raise RuntimeError('storm')
                except RuntimeError:
                    caught = True
                with temporary_flag(settings, 'quiet', True):
                    pass
                result = caught and __expect__('settings', settings, {'quiet': False}, '==')
            """,
            "Remember whether the key existed, and restore inside a finally block.",
        ),
    ),
    hints=(
        "Capture the previous location before changing it.",
        "Yield the caller's object and restore in finally.",
        "The class form restores in __exit__ and returns False.",
    ),
    repair_hints=(
        "Code after yield is skipped when the body raises unless it is in finally.",
        "Absent and present-with-None are different prior states.",
    ),
)

RECORD_SOURCE = """
    from dataclasses import dataclass, field, replace

    @dataclass
    class FieldRecord:
        name: str
        count: int = 0
        notes: list[str] = field(default_factory=list)

        def __post_init__(self):
            if not self.name.strip() or type(self.count) is not int or self.count < 0:
                raise ValueError("Use a name and nonnegative whole count")
            self.notes = list(self.notes)

        def updated(self, count: int):
            return replace(self, count=count, notes=list(self.notes))
"""
RECORD_FILES = feature(
    COPY_FILES,
    "records.py",
    RECORD_SOURCE,
    "FieldRecord",
    "records",
    'FieldRecord("wood", state["supplies"]["wood"]).name + ": " + str(state["supplies"]["wood"])',
)
RECORD_CHECKS = COPY_CHECKS + (
    scenario(
        "Record validation and independent update/defaults",
        """
            left, right = (FieldRecord("wood"), FieldRecord("rope"))
            left.notes.append("dry")
            updated = left.updated(4)
            updated.notes.append("stored")
            rejected = 0
            for name, count in ((" ", 1), ("wood", -1), ("wood", True)):
                try:
                    FieldRecord(name, count)
                except ValueError:
                    rejected += 1
            result = (
                __expect__("right.notes", right.notes, [], "==")
                and __expect__("left.count", left.count, 0, "==")
                and __expect__("left.notes", left.notes, ["dry"], "==")
                and __expect__("updated.count", updated.count, 4, "==")
                and __expect__("rejected", rejected, 3, "==")
                and __expect__(
                    "step(new_game(), 'records')",
                    step(new_game(), "records"),
                    "wood: 0",
                    "==",
                )
            )
        """,
        (
            "Factories create independent defaults; validate construction and copy "
            "nested notes on updates."
        ),
    ),
)
M17 = milestone(
    chapter="dataclasses-and-types",
    title="Define field records",
    capability="records",
    requires=M12.provides,
    base=COPY_FILES,
    reference=RECORD_FILES,
    checks=RECORD_CHECKS,
    story=(
        "The expedition ledger now has a named, validated record instead of "
        "loosely arranged values."
    ),
    teaching="## Data declarations do not replace validation\n\n"
    "Type annotations describe intended values; __post_init__ enforces the runtime contract. "
    "Use field(default_factory=list) for per-record notes. dataclasses.replace constructs "
    "another instance, but nested mutable values still need an explicit copying policy.",
    requirements="Add `records.py` with dataclass `FieldRecord(name: str, count: int = 0, "
    "notes: list[str] = field(default_factory=list))`. Reject blank/whitespace-only names, "
    "negative or noninteger counts (including bool) with ValueError. Copy supplied notes so "
    "the record owns its list. `updated(count)` returns a separately validated record with "
    "independent notes, leaving the old record unchanged. Expose FieldRecord through engine/game. "
    "Add `records` displaying a wood FieldRecord as `wood: N`, and include the command in help.",
    repair_instructions="Repair dataclass `JournalPage(title, tags)` with title as text and tags "
    "defaulting to a new list for each page. Reject blank titles. Copy a caller-supplied tags "
    "list so later edits to that list cannot change the page. `retitled(title)` returns a new "
    "validated page with independent tags, preserving the original page.",
    repair_reference="""
        from dataclasses import dataclass, field
        @dataclass
        class JournalPage:
            title: str
            tags: list[str] = field(default_factory=list)
            def __post_init__(self):
                if not self.title.strip():
                    raise ValueError("Title required")
                self.tags = list(self.tags)
            def retitled(self, title):
                return JournalPage(title, self.tags)
    """,
    repair_broken="""
        from dataclasses import dataclass, field
        @dataclass
        class JournalPage:
            title: str
            tags: list[str] = field(default_factory=list)
            def retitled(self, title):
                self.title = title
                return self
    """,
    repair_checks=(
        scenario(
            "Retitling is independent and validates the new title",
            """
                tags = ["trail"]
                page = JournalPage("First", tags)
                tags.append("external")
                other = page.retitled("Second")
                other.tags.append("new")
                rejected = False
                try:
                    page.retitled(" ")
                except ValueError:
                    rejected = True
                result = (
                    __expect__("page.title", page.title, "First", "==")
                    and __expect__("page.tags", page.tags, ["trail"], "==")
                    and __expect__("other.title", other.title, "Second", "==")
                    and rejected
                )
            """,
            "Create a new validated object and copy caller-owned nested values.",
        ),
    ),
    hints=(
        "Use a default factory and __post_init__ validation.",
        "Copy notes even when the caller supplies them.",
        "Create a new instance for updated rather than modifying self.",
    ),
    repair_hints=(
        "The current method returns the same object it changed.",
        "Both construction and updates need the same validation and ownership rules.",
    ),
)

STORE_SOURCE = """
    from typing import Protocol

    class SupplyStore(Protocol):
        def items(self) -> list[tuple[str, int]]: ...

    class MemoryStore:
        def __init__(self, values):
            self._values = dict(values)
        @classmethod
        def from_pairs(cls, pairs):
            return cls(dict(pairs))
        @property
        def total(self):
            return sum(self._values.values())
        def items(self):
            return list(self._values.items())
        def __len__(self):
            return len(self._values)
        def __iter__(self):
            return iter(self._values)

    def stock_report(store: SupplyStore, write):
        lines = [name + ": " + str(count) for name, count in store.items()]
        for line in lines:
            write(line)
        return len(lines)
"""
STORE_BASE = dict(RECORD_FILES)
# Decorators are advisory preparation for the chapter, not a runtime dependency of this feature.
STORE_FILES = feature(
    STORE_BASE,
    "stores.py",
    STORE_SOURCE,
    "SupplyStore, MemoryStore, stock_report",
    "stores",
    '"Total stock: " + str(MemoryStore(state["supplies"]).total)',
)
STORE_FILES["test_stores.py"] = code("""
    import unittest
    from stores import stock_report

    class StoreTests(unittest.TestCase):
        def test_report_uses_injected_writer(self):
            class FakeStore:
                def items(self):
                    return [("wood", 0), ("rope", 2)]
            written = []
            self.assertEqual(stock_report(FakeStore(), written.append), 2)
            self.assertEqual(written, ["wood: 0", "rope: 2"])

    if __name__ == "__main__":
        unittest.main()
""")
STORE_CHECKS = RECORD_CHECKS + (
    scenario(
        "Structural stores, subclass factories, and injected writes",
        """
            class CustomStore(MemoryStore):
                pass


            owned = {"wood": 0, "rope": 2}
            store = CustomStore.from_pairs(owned.items())
            owned["wood"] = 9
            output = []


            class Fake:
                def items(self):
                    return [("lamp", 1)]


            result = (
                type(store) is CustomStore
                and __expect__("len(store)", len(store), 2, "==")
                and __expect__("list(store)", list(store), ["wood", "rope"], "==")
                and __expect__("store.total", store.total, 2, "==")
                and __expect__(
                    "stock_report(Fake(), output.append)",
                    stock_report(Fake(), output.append),
                    1,
                    "==",
                )
                and __expect__("output", output, ["lamp: 1"], "==")
                and __expect__(
                    "step(new_game(), 'stores')",
                    step(new_game(), "stores"),
                    "Total stock: 3",
                    "==",
                )
            )
        """,
        (
            "Accept any object with the required method, preserve subclass "
            "factories, and inject output."
        ),
    ),
    scenario(
        "Learner reporting test rejects a dropped zero-count row",
        """
            import io, unittest, test_stores

            original = test_stores.stock_report


            def run_tests():
                suite = unittest.defaultTestLoader.loadTestsFromModule(test_stores)
                report = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
                return (
                    __expect__("report.testsRun", report.testsRun, 0, ">")
                    and report.wasSuccessful()
                )


            passed = run_tests()


            def mutant(store, write):
                values = [(name, n) for name, n in store.items() if n]
                for name, n in values:
                    write(f"{name}: {n}")
                return len(values)


            test_stores.stock_report = mutant
            try:
                rejected = not run_tests()
            finally:
                test_stores.stock_report = original
            result = passed and rejected
        """,
        "Assert that a zero-count row is written, not only positive counts.",
    ),
)
M18 = milestone(
    chapter="object-protocols-and-testing",
    title="Connect supply stores",
    capability="stores",
    requires=M17.provides,
    base=STORE_BASE,
    reference=STORE_FILES,
    checks=STORE_CHECKS,
    story=(
        "A report should work with your real depot or a tiny test double that "
        "follows the same contract."
    ),
    teaching="## Depend on behavior at the boundary\n\n"
    "A Protocol describes a needed method without requiring inheritance. Inject a writer "
    "such as list.append to test output without printing. A classmethod factory should use "
    "cls so subclasses remain subclasses. Special methods let your store fit len and iteration.",
    requirements="Add `stores.py`: SupplyStore is a Protocol with items() returning a list of "
    "(name, count) pairs. MemoryStore(values) owns a copy of the mapping; items() returns "
    "a fresh list in insertion order. from_pairs is a classmethod preserving subclasses; "
    "total is a read-only property summing counts; len gives distinct keys and iteration "
    "yields names. `stock_report(store, write)` accepts structural stores, calls write once "
    "per item with `NAME: COUNT` (including zero), and returns the number of lines. "
    "Expose the API from engine/game and add `stores` returning `Total stock: N`, plus help.\n\n"
    "Add test_stores.py with a unittest using a fake store and injected writer. Import "
    "stock_report into the test module. Assert a zero-count and a positive row; the tests "
    "must reject a version that silently drops zero-count rows.",
    repair_instructions="Repair `render_inventory(store, emit)` using only the store.items() "
    "contract. Call emit once for each `(name, count)` in the returned order, including zero, "
    "with `name=count`. Return the emitted line count. Propagate writer errors; do not fall "
    "back to print, require concrete store classes, or access private attributes.",
    repair_reference="""
        def render_inventory(store, emit):
            count = 0
            for name, amount in store.items():
                emit(f"{name}={amount}")
                count += 1
            return count
    """,
    repair_broken="""
        def render_inventory(store, emit):
            count = 0
            for name, amount in store.items():
                if amount:
                    print(f"{name}={amount}")
                    count += 1
            return count
    """,
    repair_checks=(
        scenario(
            "Structural input and exact injected output",
            """
                class Store:
                    def items(self):
                        return [("wood", 0), ("rope", 2)]


                output = []
                count = render_inventory(Store(), output.append)
                result = __expect__("count", count, 2, "==") and __expect__(
                    "output", output, ["wood=0", "rope=2"], "=="
                )
            """,
            "The injected writer is the output boundary, and zero still belongs in the report.",
        ),
    ),
    hints=(
        "Keep MemoryStore's dictionary private and return copies of its items.",
        "Use cls in the factory and properties for computed values.",
        "The fake store does not need to inherit from MemoryStore.",
    ),
    repair_hints=(
        "Printing bypasses the caller's chosen output destination.",
        "Do not filter out legitimate zero counts.",
    ),
    minutes=35,
)
DEPTH = (M12, M13, M14, M15, M16, M17, M18)
