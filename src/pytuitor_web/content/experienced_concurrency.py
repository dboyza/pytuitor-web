"""Build and Repair contracts for python-concurrency."""

from pytuitor_web.experienced_authoring import (
    _check,
    _exec,
    _exec_with,
    _probe,
    _repair,
    check,
    legacy,
    probe,
    unit,
)

LESSONS = (
    unit(
        "coroutine-basics",
        "python-concurrency",
        "Await cooperative work",
        "Coroutines & event loops",
        """
        import asyncio

        async def delayed_total(values):
            total = 0
            for value in values:
                await asyncio.sleep(0)
                total += value
            return total
        """,
        [
            check("Await a result", "__import__('asyncio').run(delayed_total([2, -1, 4]))", 5),
            check("Empty input", "__import__('asyncio').run(delayed_total([]))", 0),
            check("One-pass input", "__import__('asyncio').run(delayed_total(iter([3, 2])))", 5),
        ],
        [
            ("Use async def for the coroutine; calling it alone does not produce the final value."),
            "Await asyncio.sleep(0) in each iteration to offer other tasks a turn.",
        ],
    ),
    legacy("clean-exits", "python-concurrency"),
    unit(
        "task-groups",
        "python-concurrency",
        "Give tasks a shared lifetime",
        "Task groups & cancellation",
        """
        import asyncio

        async def collect_jobs(jobs):
            async with asyncio.TaskGroup() as group:
                tasks = [group.create_task(job()) for job in jobs]
            return [task.result() for task in tasks]
        """,
        [
            check(
                "Preserve input order",
                (
                    "__import__('asyncio').run(collect_jobs([lambda: __import__('asyncio').slee"
                    "p(0, result=3), lambda: __import__('asyncio').sleep(0, result=1)]))"
                ),
                [3, 1],
            ),
            check("Empty group", "__import__('asyncio').run(collect_jobs([]))", []),
            check(
                "Group failures",
                (
                    "(lambda: exec(\"async def broken():\\n    raise ValueError('job')\\ntry:"
                    "\\n    __import__('asyncio').run(collect_jobs([broken]))\\nexcept Exceptio"
                    "nGroup as errors:\\n    assert any(isinstance(e, ValueError) for e in erro"
                    "rs.exceptions)\\nelse:\\n    raise AssertionError('failure was hidden')\""
                    ", globals()))()"
                ),
                None,
            ),
        ],
        [
            (
                "Call each job factory once, schedule its coroutine, and keep the task li"
                "st in input order."
            ),
            (
                "TaskGroup waits on exit and groups failures. Read results only after succe"
                "ssful exit."
            ),
        ],
    ),
    unit(
        "async-streams",
        "python-concurrency",
        "Consume an async stream",
        "Async iteration",
        """
        async def collect_nonempty(source):
            result = []
            async for text in source:
                cleaned = text.strip()
                if cleaned:
                    result.append(cleaned)
            return result
        """,
        [
            check(
                "Trim and filter",
                (
                    "(lambda: (exec(\"async def source():\\n    for text in [' a ', '', '  "
                    "', 'b']:\\n        yield text\", globals()), __import__('asyncio').run"
                    "(collect_nonempty(source())))[1])()"
                ),
                ["a", "b"],
            ),
            check(
                "Empty stream",
                (
                    '(lambda: (exec("async def source():\\n    for text in []:\\n        yield '
                    "text\", globals()), __import__('asyncio').run(collect_nonempty(source()))"
                    ")[1])()"
                ),
                [],
            ),
        ],
        [
            "An async iterable is consumed with async for inside an async function.",
            "Strip each string once and append only nonempty results.",
        ],
    ),
)

BUILD_INSTRUCTIONS = {
    "coroutine-basics": (
        "\nWrite `async def delayed_total(values)`.\nAccept a finite iterable of nu"
        "mbers, await `asyncio.sleep(0)` once per value, and return their sum.\nAn "
        "empty iterable returns zero.\nAccept a one-pass iterator and negative valu"
        "es.\nDo not modify input, print, create your own event loop inside the fun"
        "ction, or use `time.sleep`.\nFor `[4, -2, 6]`, awaiting the function produ"
        "ces eight.\nThe checks call `asyncio.run` for you; Run may use your own te"
        "mporary script-level demonstration.\n"
    ).strip(),
    "clean-exits": (
        "\nImport `contextmanager` from `contextlib`, then write `def session(event"
        's):` with `@contextmanager` directly above it so it appends `"open"` on en'
        'try, yields the events list, and always appends `"close"` on exit.\nUse `t'
        "ry`/`finally` so cleanup also happens when the caller raises an error.\n\n"
        "Next, write `import asyncio`.\nDefine `async def double(value):` with `awa"
        "it asyncio.sleep(0)` followed by `return value * 2`.\nThe sleep yields con"
        "trol so other scheduled coroutines can run.\nThen define `async def double"
        "_all(values):` using `await asyncio.gather(...)` to call `double` for ever"
        "y value.\nReturn results in input order, including an empty list for empty"
        " input.\nSchedule all operations together rather than awaiting each one in"
        " a loop.\n"
    ).strip(),
    "task-groups": (
        "\nDefine `async def collect_jobs(jobs)`.\n`jobs` is a finite iterable of f"
        "unctions or other callable objects that accept no arguments.\nCalling each"
        " one creates a new coroutine object; such a function is sometimes called a"
        " **factory** because it creates another object.\nCall each factory once an"
        "d schedule all jobs in a TaskGroup.\nReturn their results in input order, "
        "regardless of completion order.\nEmpty input returns `[]`.\nOn failure, al"
        "low the TaskGroup's exception group to reach the caller after the other ta"
        "sks in that group finish cleanup.\nDo not suppress errors or create a nest"
        "ed event loop.\nFor factories returning 8 then 3, return `[8, 3]`.\nNo pri"
        "nting is required.\n"
    ).strip(),
    "async-streams": (
        "\nWrite `async def collect_nonempty(source)`.\nThe source is a finite asyn"
        "c iterable of strings.\nStrip surrounding whitespace from each string, dis"
        "card empty results, and return a list of the remaining strings in source o"
        "rder.\nPreserve duplicates and internal whitespace.\nEmpty input returns `"
        "[]`.\nFor an async source yielding `'  east '`, `' '`, and `'west'`, retur"
        "n `['east', 'west']`.\nAllow source exceptions to propagate.\nDo not print"
        ", modify the source, or run a new event loop inside the function.\n"
    ).strip(),
}

REPAIR_STAGES = {
    "coroutine-basics": _repair(
        (
            "Define async collect_ready(values). Await asyncio.sleep(0) once per value "
            "and return a list of values greater than zero in input order, preserving c"
            "ooperative scheduling. Values are finite numeric values from a finite one-"
            "pass iterable. Sleep for every item, including rejected items; return [] f"
            "or empty input."
        ),
        """
        import asyncio

        async def collect_ready(values):
            result = []
            for value in values:
                await asyncio.sleep(0)
                if value > 0:
                    result.append(value)
            return result
        """,
        """
        async def collect_ready(values):
            return [value for value in values if value >= 0]
        """,
        [
            _check(
                "Filter asynchronously",
                "__import__('asyncio').run(collect_ready([-1, 2, 0, 3]))",
                [2, 3],
                "Await once per input and retain positive values.",
            ),
            _check(
                "Empty input",
                "__import__('asyncio').run(collect_ready([]))",
                [],
                "Return an empty list for empty input.",
            ),
            _probe(
                "Every item cooperatively yields",
                (
                    """
                import asyncio
                from unittest.mock import patch


                async def probe():
                    calls = []

                    async def sleep(delay):
                        calls.append(delay)

                    with patch.object(asyncio, "sleep", sleep):
                        values = await collect_ready(iter([-1, 0, 2]))
                    return values, calls


                result = asyncio.run(asyncio.wait_for(probe(), 1))
                """
                ),
                ([2], [0, 0, 0]),
                "Await sleep(0) for rejected values as well as retained ones.",
            ),
        ],
        [
            "The await belongs inside the loop.",
            "Append only after the awaited operation for a positive value.",
        ],
    ),
    "clean-exits": _repair(
        (
            "Define temporary_events(events, label) with contextmanager. Append '<label"
            ">:start' on entry and '<label>:stop' in finally, including when the body r"
            "aises. Yield the exact events list to the with body, propagate its errors,"
            " and record only one start and one stop per entry. Nested contexts close i"
            "n reverse entry order."
        ),
        """
        from contextlib import contextmanager

        @contextmanager
        def temporary_events(events, label):
            events.append(f'{label}:start')
            try:
                yield events
            finally:
                events.append(f'{label}:stop')
        """,
        """
        from contextlib import contextmanager

        @contextmanager
        def temporary_events(events, label):
            events.append(f'{label}:start')
            yield events
            events.append(f'{label}:stop')
        """,
        [
            _check(
                "Normal cleanup",
                _exec_with(
                    """
                    with temporary_events(e, "job"):
                        pass
                    result = e
                    """,
                    "{'e': []}",
                ),
                ["job:start", "job:stop"],
                "Record the stop event after normal exit.",
            ),
            _check(
                "Exceptional cleanup",
                _exec_with(
                    """
                    try:
                        with temporary_events(e, "job"):
                            raise ValueError
                    except ValueError:
                        pass
                    result = e
                    """,
                    "{'e': []}",
                ),
                ["job:start", "job:stop"],
                "Put the closing event in finally.",
            ),
            _probe(
                "Nested context order and yielded object",
                (
                    """
                events = []
                with temporary_events(events, "outer") as value:
                    same = value is events
                    with temporary_events(events, "inner"):
                        pass
                result = (same, events)
                """
                ),
                (True, ["outer:start", "inner:start", "inner:stop", "outer:stop"]),
                "Yield the caller list and let nested contexts close in reverse order.",
            ),
        ],
        ["Code before yield is entry.", "Only finally guarantees cleanup when the body fails."],
    ),
    "task-groups": _repair(
        (
            "Define async collect_named(jobs), where jobs maps names to no-argument cor"
            "outine factories. Schedule all factories in one TaskGroup and return a nam"
            "e-to-result dict. Call each factory once, preserve input mapping order, re"
            "turn {} for empty input, and propagate failures after cancelling and await"
            "ing siblings. Assume factory calls themselves return coroutines without ra"
            "ising."
        ),
        (
            "\n        import asyncio\n\n        async def collect_named(jobs):\n      "
            "      async with asyncio.TaskGroup() as group:\n                tasks = {n"
            "ame: group.create_task(factory()) for name, factory in jobs.items()}\n    "
            "        return {name: task.result() for name, task in tasks.items()}\n    "
            "    "
        ),
        """
        import asyncio

        async def collect_named(jobs):
            result = {}
            for name, factory in jobs.items():
                result[name] = await factory()
            return result
        """,
        [
            _check(
                "Collect named results",
                "__import__('asyncio').run(collect_named({"
                "'slow': lambda: __import__('asyncio').sleep(0, result=2), "
                "'fast': lambda: __import__('asyncio').sleep(0, result=1)}))",
                {"slow": 2, "fast": 1},
                "Create every task before leaving the group.",
            ),
            _check(
                "Input order",
                "list(__import__('asyncio').run(collect_named({"
                "'slow': lambda: __import__('asyncio').sleep(0, result=2), "
                "'fast': lambda: __import__('asyncio').sleep(0, result=1)})))",
                ["slow", "fast"],
                "Keep the input mapping's order in the returned mapping.",
            ),
            _check(
                "Jobs overlap",
                _exec(
                    (
                        "\n                    import asyncio\n\n                    async def prob"
                        "e():\n                        started = []\n                        observ"
                        "ations = []\n\n                        async def job(value):\n            "
                        "                started.append(value)\n                            await a"
                        "syncio.sleep(0)\n                            observations.append(len(start"
                        "ed))\n                            return value\n\n                        "
                        'result = await collect_named(\n                            {"a": lambda: j'
                        'ob(1), "b": lambda: job(2)}\n                        )\n                  '
                        '      return result == {"a": 1, "b": 2} and observations == [2, 2]\n\n    '
                        "                __probe_result__ = asyncio.run(asyncio.wait_for(probe(), 1"
                        "))\n                    "
                    ),
                    "__probe_result__",
                ),
                True,
                "Schedule every job before any job resumes after its first await.",
            ),
            _check(
                "Empty mapping",
                "__import__('asyncio').run(collect_named({}))",
                {},
                "An empty TaskGroup returns an empty mapping.",
            ),
            _probe(
                "Failure cancels and joins siblings",
                (
                    """
                import asyncio


                async def probe():
                    existing = set(asyncio.all_tasks())
                    started = asyncio.Event()
                    cleaned = []

                    async def slow():
                        try:
                            started.set()
                            await asyncio.Event().wait()
                        finally:
                            cleaned.append("closed")

                    async def fail():
                        await started.wait()
                        raise ValueError("failed")

                    caught = False
                    try:
                        await collect_named({"slow": slow, "fail": fail})
                    except ExceptionGroup:
                        caught = True
                    return caught, cleaned, len(set(asyncio.all_tasks()) - existing)


                result = asyncio.run(asyncio.wait_for(probe(), 1))
                """
                ),
                (True, ["closed"], 0),
                ("A TaskGroup joins cancelled siblings before it propagates the grouped failure."),
            ),
        ],
        ["Store tasks by their input name.", ("Read task results only after the TaskGroup exits.")],
    ),
    "async-streams": _repair(
        (
            "Define async chunked(source, size), yielding lists of up to size items fro"
            "m an async iterable. Reject nonpositive size and yield a final partial chu"
            "nk. Size is an integer. Each chunk is a fresh list. Read only enough sourc"
            "e items to fill the next requested chunk, support infinite sources, and pr"
            "opagate source errors. Empty input yields no chunks."
        ),
        """
        async def chunked(source, size):
            if size <= 0:
                raise ValueError('Size must be positive')
            chunk = []
            async for item in source:
                chunk.append(item)
                if len(chunk) == size:
                    yield chunk
                    chunk = []
            if chunk:
                yield chunk
        """,
        """
        async def chunked(source, size):
            values = [item async for item in source]
            yield values[:size]
        """,
        [
            _check(
                "Chunk stream",
                _exec(
                    """
                    import asyncio

                    async def source():
                        for value in (1, 2, 3):
                            yield value

                    async def consume():
                        result = []
                        async for chunk in chunked(source(), 2):
                            result.append(chunk)
                        return result

                    __probe_result__ = asyncio.run(consume())
                    """,
                    "__probe_result__",
                ),
                [[1, 2], [3]],
                "Use async iteration to yield full and final partial chunks.",
            ),
            _check(
                "Reject size",
                _exec(
                    """
                    import asyncio

                    async def source():
                        if False:
                            yield 1

                    async def consume():
                        async for _ in chunked(source(), 0):
                            pass

                    try:
                        asyncio.run(consume())
                    except ValueError:
                        result = True
                    else:
                        result = False
                    """
                ),
                True,
                "Validate size before reading the source.",
            ),
            _probe(
                "Chunks are produced before source exhaustion",
                (
                    """
                import asyncio


                async def source():
                    yield 1
                    yield 2
                    raise AssertionError("eager read")


                async def probe():
                    stream = chunked(source(), 2)
                    try:
                        return await anext(stream)
                    finally:
                        await stream.aclose()


                result = asyncio.run(asyncio.wait_for(probe(), 1))
                """
                ),
                [1, 2],
                "Yield a full chunk immediately, without collecting the remaining source.",
            ),
        ],
        [
            "This stage needs an async source for direct checking.",
            "Yield full chunks as soon as they fill and then flush a partial chunk.",
        ],
    ),
}

EXTRA_CHECKS = {
    "async-streams": (
        probe(
            "Preserve duplicates and internal spaces",
            """
            import asyncio
            async def source():
                for text in [" same ", "same", " two  words "]:
                    yield text
            __probe_result__ = asyncio.run(collect_nonempty(source()))
            """,
            ["same", "same", "two  words"],
            (
                "Read repeated strings and a string with two internal spaces; preserve both"
                " features."
            ),
            "strip removes surrounding whitespace only; do not deduplicate the result.",
        ),
        probe(
            "Source errors remain visible",
            """
            import asyncio
            async def source():
                yield "first"
                raise ValueError("source failed")
            try:
                asyncio.run(collect_nonempty(source()))
            except ValueError:
                __probe_result__ = True
            else:
                __probe_result__ = False
            """,
            True,
            ("Read one value before the source raises ValueError; expect the error to propagate."),
            "Do not replace a source failure with a partial success result.",
        ),
    ),
    "coroutine-basics": (
        probe(
            "Give another task a turn",
            """
            import asyncio
            async def probe_cooperation():
                progress = []
                observations = []
                def values():
                    for value in range(4):
                        progress.append(value)
                        yield value
                task = asyncio.create_task(delayed_total(values()))
                while not task.done():
                    observations.append(len(progress))
                    await asyncio.sleep(0)
                assert await task == 6
                return all(index in observations for index in (1, 2, 3))
            __probe_result__ = asyncio.run(probe_cooperation())
            """,
            True,
            (
                "Run delayed_total over four values beside an observer; verify the observ"
                "er can run between input values."
            ),
            "Await asyncio.sleep(0) once per value so the loop remains cooperative.",
        ),
    ),
    "task-groups": (
        probe(
            "Jobs start concurrently",
            """
            import asyncio
            async def probe_concurrency():
                started = []
                ready = asyncio.Event()
                async def job(value):
                    started.append(value)
                    if len(started) == 3:
                        ready.set()
                    await ready.wait()
                    return value
                factories = [lambda: job(1), lambda: job(2), lambda: job(3)]
                result = await asyncio.wait_for(collect_jobs(factories), 0.5)
                return result
            __probe_result__ = asyncio.run(probe_concurrency())
            """,
            [1, 2, 3],
            (
                "Three jobs wait until all have started; collect_jobs must schedule all t"
                "hree and preserve their order."
            ),
            "Create tasks for every job before awaiting group completion.",
        ),
    ),
}
