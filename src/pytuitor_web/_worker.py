"""Standalone standard-library learner process, launched with Python isolated mode."""

import asyncio
import contextlib
import importlib
import io
import json
import os
import shutil
import sys
import traceback
from pathlib import Path


@contextlib.contextmanager
def symlink_fixtures(links):
    """Check link behavior without requiring Windows Developer Mode or elevation.

    Prefer real links. If the OS denies their creation, use ordinary entries and
    scoped Path probes matching their link, existence, and file-kind behavior.
    The fallback affects authored checks only, never a learner's Run operation.
    """
    from unittest.mock import patch

    simulated = {}
    for name, target in links.items():
        path = Path(name)
        try:
            path.symlink_to(target)
        except PermissionError:
            path.touch(exist_ok=False)
            simulated[path.absolute()] = (path.parent / target).absolute()
    original_link, original_exists, original_file = Path.is_symlink, Path.exists, Path.is_file
    with contextlib.ExitStack() as stack:
        if simulated:
            stack.enter_context(
                patch.object(
                    Path,
                    "is_symlink",
                    lambda path: path.absolute() in simulated or original_link(path),
                )
            )
            stack.enter_context(
                patch.object(
                    Path,
                    "exists",
                    lambda path, **kwargs: original_exists(
                        simulated.get(path.absolute(), path), **kwargs
                    ),
                )
            )
            stack.enter_context(
                patch.object(
                    Path,
                    "is_file",
                    lambda path, **kwargs: original_file(
                        simulated.get(path.absolute(), path), **kwargs
                    ),
                )
            )
        yield


def session_check(factory, fail):
    events = []
    try:
        with factory(events) as active:
            if active is not events:
                return ["The context manager must yield events"]
            if fail:
                raise ValueError("Practice failure")
    except ValueError:
        if not fail:
            raise
    return events


def raises_value_error(fn, argument):
    try:
        fn(argument)
    except ValueError:
        return True
    return False


def mutation_check(test):
    namespace = test.__globals__
    original = namespace["parse_count"]
    mutants = (lambda _: 0, lambda _: 12, lambda text: abs(int(text)))
    try:
        for mutant in mutants:
            namespace["parse_count"] = mutant
            try:
                test()
            except AssertionError:
                continue
            return False
        return True
    finally:
        namespace["parse_count"] = original


def concurrency_check(fn):
    namespace = fn.__globals__
    original = namespace["double"]

    async def exercise():
        started = 0
        gate = asyncio.Event()

        async def probe(value):
            nonlocal started
            started += 1
            if started == 3:
                gate.set()
            await gate.wait()
            return value * 2

        namespace["double"] = probe
        try:
            return await asyncio.wait_for(fn([1, 2, 3]), 0.5) == [2, 4, 6]
        except TimeoutError:
            return False

    try:
        return asyncio.run(exercise())
    finally:
        namespace["double"] = original


def cli_check(fn, text):
    original = sys.stdin
    output = io.StringIO()
    try:
        sys.stdin = io.StringIO(text)
        with contextlib.redirect_stdout(output):
            fn()
        return json.loads(output.getvalue())
    finally:
        sys.stdin = original


@contextlib.contextmanager
def practice_server(respond):
    """Serve JSON on 127.0.0.1 so web checks never need the internet.

    respond(method, path, query, body) returns (status, data); yields (base_url, requests).
    """
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from urllib.parse import parse_qs, urlsplit

    seen = []

    class Handler(BaseHTTPRequestHandler):
        def answer(self):
            parts = urlsplit(self.path)
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
            try:
                body = json.loads(raw) if raw else None
            except ValueError:
                body = raw.decode("utf-8", "replace")
            query = {key: values[-1] for key, values in parse_qs(parts.query).items()}
            seen.append({"method": self.command, "path": parts.path, "query": query, "body": body})
            status, data = respond(self.command, parts.path, query, body)
            payload = json.dumps(data).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        do_GET = do_POST = do_PUT = do_DELETE = answer

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}", seen
    finally:
        server.shutdown()
        server.server_close()


def pytest_run(*paths):
    """Run learner test files with pytest; return (exit code, collected count, report)."""
    import pytest

    # Re-import learner tests each run so a check can swap in a deliberately broken module.
    for name in [name for name in sys.modules if name.split(".")[0].startswith("test_")]:
        del sys.modules[name]
    os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

    class Counter:
        collected = 0

        def pytest_collection_modifyitems(self, items):
            self.collected = len(items)

    counter = Counter()
    report = io.StringIO()
    with contextlib.redirect_stdout(report):
        code = pytest.main(["-q", "-p", "no:cacheprovider", *paths], plugins=[counter])
    return int(code), counter.collected, report.getvalue()


class Tee:
    def __init__(self, target, limit):
        self.target = target
        self.limit = limit
        self.captured = ""

    def write(self, text):
        self.target.write(text)
        self.target.flush()
        self.captured = (self.captured + text)[: self.limit]
        return len(text)

    def flush(self):
        self.target.flush()


class KeyboardInput:
    """Signal actual stdin reads so time spent typing is not execution time."""

    def __init__(self, stream, waiting_path):
        self.stream = stream
        self.waiting_path = waiting_path

    def readline(self, size=-1):
        self.waiting_path.touch()
        try:
            return self.stream.readline(size)
        finally:
            self.waiting_path.unlink(missing_ok=True)

    def read(self, size=-1):
        self.waiting_path.touch()
        try:
            return self.stream.read(size)
        finally:
            self.waiting_path.unlink(missing_ok=True)

    def __iter__(self):
        return self

    def __next__(self):
        line = self.readline()
        if not line:
            raise StopIteration
        return line

    def isatty(self):
        return False


def main():
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    sys.stderr.reconfigure(encoding="utf-8", newline="\n")
    root = Path(sys.argv[1])
    request = json.loads((root / "request.json").read_text())
    limits = request["limits"]
    if os.name != "nt":
        import resource

        resource.setrlimit(resource.RLIMIT_CPU, (limits["cpu_seconds"],) * 2)
        resource.setrlimit(resource.RLIMIT_FSIZE, (limits["file_bytes"],) * 2)
        if sys.platform == "linux":
            resource.setrlimit(resource.RLIMIT_AS, (limits["memory_bytes"],) * 2)
    result = {"error": "", "checks": []}

    workspace = root / "workspace"
    entrypoint = request["entrypoint"]
    initial_path = list(sys.path)
    initial_modules = set(sys.modules)

    def prepare():
        os.chdir(root)
        if workspace.exists():
            shutil.rmtree(workspace)
        workspace.mkdir()
        for name, source in request["files"].items():
            path = workspace / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(source, encoding="utf-8")
        for name in set(sys.modules) - initial_modules:
            del sys.modules[name]
        sys.path[:] = [str(workspace / Path(entrypoint).parent), str(workspace), *initial_path]
        sys.argv[:] = [entrypoint]
        importlib.invalidate_caches()
        os.chdir(workspace)

    def program():
        return compile((workspace / entrypoint).read_text(encoding="utf-8"), entrypoint, "exec")

    def describe_error(exc):
        frames = [
            f
            for f in traceback.extract_tb(exc.__traceback__)
            if f.filename in request["files"] or str(workspace) in f.filename
        ]
        locations = "".join(
            f"  {Path(f.filename).name}, line {f.lineno}, in {f.name}\n" for f in frames
        )
        message = locations + "".join(traceback.format_exception_only(exc))
        if isinstance(exc, EOFError):
            message += (
                "\nThe program expected another answer. Run again and type it in the console.\n"
            )
        return message

    observations = []

    def expect(label, actual, expected, comparison="=="):
        """Capture an authored assertion without rerunning the learner's operation."""
        import operator

        operations = {
            "==": operator.eq,
            "!=": operator.ne,
            "<": operator.lt,
            "<=": operator.le,
            ">": operator.gt,
            ">=": operator.ge,
        }
        passed = bool(operations[comparison](actual, expected))
        observation = {
            "label": str(label)[:240],
            "actual": repr(actual)[:1000],
            "expected": repr(expected)[:1000],
            "comparison": comparison,
            "passed": passed,
        }
        if len(observations) < 16:
            observations.append(observation)
        elif not passed and all(item["passed"] for item in observations):
            observations[-1] = observation
        return passed

    def namespace():
        return {
            "__name__": "__main__",
            "__file__": str(workspace / entrypoint),
            "__session_check__": session_check,
            "__symlink_fixtures__": symlink_fixtures,
            "__raises_value_error__": raises_value_error,
            "__mutation_check__": mutation_check,
            "__cli_check__": cli_check,
            "__concurrency_check__": concurrency_check,
            "__expect__": expect,
            "__practice_server__": practice_server,
            "__pytest_run__": pytest_run,
        }

    if not request["checks"]:
        prepare()
        sys.stdin = (
            KeyboardInput(sys.stdin, root / "waiting-for-input")
            if request.get("interactive")
            else io.StringIO(request["stdin"])
        )
        try:
            with contextlib.redirect_stdout(Tee(sys.stdout, limits["output_bytes"])):
                exec(program(), namespace())
        except BaseException as exc:
            result["error"] = describe_error(exc)
    else:
        with (root / "checks.jsonl").open("w", encoding="utf-8", newline="\n") as events:

            def emit(event):
                events.write(json.dumps(event) + "\n")
                events.flush()

            for index, check in enumerate(request["checks"], 1):
                observations.clear()
                supplied = check.get("stdin")
                supplied = request["stdin"] if supplied is None else supplied
                case = {
                    "number": index,
                    "label": check["label"],
                    "input": supplied,
                    "operation": check.get("description") or check["expression"],
                    "expected": repr(check["expected"]),
                    "expected_output": check.get("expected_output"),
                    "nudge": check["nudge"],
                    "status": "running",
                }
                emit(case)
                capture = Tee(sys.stdout, limits["output_bytes"])
                expected = check["expected"]
                prepare()
                scope = namespace()
                try:
                    sys.stdin = io.StringIO(supplied)
                    with contextlib.redirect_stdout(capture):
                        exec(program(), scope)
                        scope["__stdout__"] = capture.captured
                        if isinstance(expected, dict) and set(expected) == {"expr"}:
                            expected = eval(expected["expr"], scope)
                        actual = eval(check["expression"], scope)
                        actual = json.loads(json.dumps(actual))
                    case["passed"] = actual == expected
                    if check.get("expected_output") is not None:
                        case["passed"] &= capture.captured.rstrip().endswith(
                            check["expected_output"]
                        )
                    case["actual"] = repr(actual)[:1000]
                except BaseException as exc:
                    case["passed"] = False
                    case["actual"] = describe_error(exc)
                    # Preserve a top-level error for syntax and program startup failures.
                    if isinstance(exc, (SyntaxError, EOFError)):
                        result["error"] = case["actual"]
                case.update(
                    status="finished",
                    observations=list(observations),
                    output=capture.captured[: limits["output_bytes"]],
                    expected=repr(expected)[:1000],
                )
                result["checks"].append(case)
                emit(case)
    (root / "result.json").write_text(json.dumps(result))


if __name__ == "__main__":
    main()
