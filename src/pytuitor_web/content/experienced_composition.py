"""Build and Repair contracts for python-composition."""

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


def _log_script(logger, call, result, *, traceback=False):
    """Collect one named logger's records during call, and whether the root was configured."""
    extra = ", record.exc_info is not None" if traceback else ""
    return f"""
        import logging

        records = []


        class Collect(logging.Handler):
            def emit(self, record):
                records.append([record.levelname, record.getMessage(){extra}])


        handler = Collect()
        target = logging.getLogger({logger!r})
        target.addHandler(handler)
        target.setLevel(logging.DEBUG)
        root_before = list(logging.getLogger().handlers)
        try:
            value = {call}
        finally:
            target.removeHandler(handler)
        configured = bool(root_before) or list(logging.getLogger().handlers) != root_before
        {result} = [value, records, configured]
    """


LESSONS = (
    unit(
        "callable-tools",
        "python-composition",
        "Callable tools and sorting",
        "Callables, lambdas & partial",
        """
        from functools import partial

        def rank(records, key):
            return sorted(records, key=key)

        def make_scaler(factor):
            return partial(lambda value, factor: value * factor, factor=factor)
        """,
        [
            check("Custom key", "rank(['pear', 'fig', 'apple'], len)", ["fig", "pear", "apple"]),
            check("Stable equal keys", "rank(['bb', 'aa', 'z'], len)", ["z", "bb", "aa"]),
            check("One-pass records", "rank(iter([3, 1, 2]), lambda value: -value)", [3, 2, 1]),
            check("Empty records", "rank([], len)", []),
            check(
                "Reusable bound argument",
                "(lambda scale: [scale(2), scale(-3), scale(0)])(make_scaler(4))",
                [8, -12, 0],
            ),
            check(
                "Keep caller list",
                (
                    "(exec('values = [3, 1]\\nrank(values, lambda x: x)\\nresult = "
                    "values', globals()), result)[1]"
                ),
                [3, 1],
            ),
        ],
        [
            (
                "Pass the supplied key callable to sorted; sorted returns a n"
                "ew list and preserves equal-key order."
            ),
            (
                "Bind factor with a closure or functools.partial so each late"
                "r call multiplies its own value."
            ),
        ],
    ),
    unit(
        "functional-pipelines",
        "python-composition",
        "Map, filter, and folds",
        "Map, filter & reduce",
        """
        from functools import reduce

        def transform_selected(items, predicate, transform):
            return list(map(transform, filter(predicate, items)))

        def fold(items, combine, initial):
            return reduce(combine, items, initial)
        """,
        [
            check(
                "Select before transform",
                "transform_selected([-2, 0, 3], lambda x: x > 0, lambda x: x * 10)",
                [30],
            ),
            check(
                "One-pass transformation",
                "transform_selected(iter([1, 2, 3]), lambda x: x % 2, str)",
                ["1", "3"],
            ),
            check("Empty pipeline", "transform_selected([], bool, str)", []),
            check(
                "Transform only selected values",
                "transform_selected([0, 2], bool, lambda value: 10 / value)",
                [5.0],
            ),
            check("Left fold order", "fold([2, 3], lambda total, x: total - x, 10)", 5),
            check(
                "Generic accumulator",
                "fold(iter(['a', 'b']), lambda acc, x: acc + [x.upper()], [])",
                ["A", "B"],
            ),
            check("Empty fold keeps initial", "fold([], lambda a, b: None, 'seed')", "seed"),
        ],
        [
            (
                "Filter original values before applying the transform; reject"
                "ed values must never reach it."
            ),
            (
                "Start with initial and call combine(accumulator, item) in in"
                "put order, including for nonnumeric accumulators."
            ),
        ],
    ),
    legacy("functions-with-memory", "python-composition"),
    unit(
        "decorator-factories",
        "python-composition",
        "Configure and stack decorators",
        "Decorator factories & stacking",
        """
        from functools import wraps

        def prefixed(prefix):
            def decorate(function):
                @wraps(function)
                def wrapper(*args, **kwargs):
                    return prefix + function(*args, **kwargs)
                return wrapper
            return decorate
        """,
        [
            check(
                "Factory configuration", "prefixed('Hi: ')(lambda name: name)('Lin')", ("Hi: Lin")
            ),
            check(
                "Forward keyword arguments",
                "prefixed('>')(lambda *, name: name)(name='Ada')",
                ">Ada",
            ),
            check("Stack order", "prefixed('A')(prefixed('B')(lambda: 'C'))()", "ABC"),
            check(
                "Preserve function identity metadata",
                (
                    "(exec(\"def greet():\\n    'Greeting documentation.'\\n    return 'hello"
                    "'\\nwrapped = prefixed('!')(greet)\\nresult = [wrapped.__name__, wrapped._"
                    '_doc__, wrapped.__wrapped__ is greet]", globals()), result)[1]'
                ),
                ["greet", "Greeting documentation.", True],
            ),
            check(
                "Evaluate each call",
                (
                    '(exec("calls = []\\ndef greet(value):\\n    calls.append(value)\\n    retu'
                    "rn str(value)\\nf = prefixed('!')(greet)\\nresult = [f(1), f(2), calls]\""
                    ", globals()), result)[1]"
                ),
                ["!1", "!2", [1, 2]],
            ),
        ],
        [
            (
                "Use three nested layers: configuration, original function, then invocation"
                " arguments."
            ),
            (
                "Forward *args and **kwargs, prepend after calling, and use w"
                "raps to preserve metadata and __wrapped__."
            ),
        ],
    ),
    legacy("lazy-by-design", "python-composition"),
    unit(
        "exception-boundaries",
        "python-composition",
        "Exceptions with context",
        "Custom exceptions & chaining",
        """
        class RecordError(ValueError):
            pass

        def parse_record(text):
            try:
                return int(text)
            except ValueError as error:
                raise RecordError("Invalid integer record") from error

        def read_record(stream):
            try:
                return parse_record(stream.read())
            finally:
                stream.close()
        """,
        [
            check("Parse signed integer", "parse_record(' -12 ')", -12),
            check(
                "Custom error retains cause",
                (
                    "(exec(\"try:\\n    parse_record('bad')\\nexcept RecordError as error:\\n "
                    '   result = type(error.__cause__) is ValueError", globals()), result)[1]'
                ),
                True,
            ),
            check(
                "Close on success",
                (
                    "(exec(\"from io import StringIO\\ns = StringIO('5')\\nvalue = read_record"
                    '(s)\\nresult = [value, s.closed]", globals()), result)[1]'
                ),
                [5, True],
            ),
            check(
                "Close on invalid record",
                (
                    "(exec(\"from io import StringIO\\ns = StringIO('x')\\ntry:\\n    read_rec"
                    'ord(s)\\nexcept RecordError:\\n    result = s.closed", globals()), result)'
                    "[1]"
                ),
                True,
            ),
            check(
                "Preserve read errors and close",
                (
                    '(exec("class Broken:\\n    closed = False\\n    def read(self):\\n        '
                    "raise OSError('disk')\\n    def close(self):\\n        self.closed = True"
                    "\\ns = Broken()\\ntry:\\n    read_record(s)\\nexcept OSError as error:\\n "
                    '   result = [str(error), s.closed]", globals()), result)[1]'
                ),
                ["disk", True],
            ),
        ],
        [
            (
                "Catch ValueError around int conversion and raise RecordError"
                " from the caught exception."
            ),
            (
                "Read once in try and close once in finally so conversion and"
                " reading failures both clean up."
            ),
        ],
    ),
    unit(
        "context-practice",
        "python-composition",
        "Restore temporary state",
        "Exception-safe context managers",
        """
        from contextlib import contextmanager

        @contextmanager
        def temporary_value(mapping, key, value):
            existed = key in mapping
            previous = mapping.get(key)
            mapping[key] = value
            try:
                yield mapping
            finally:
                if existed:
                    mapping[key] = previous
                else:
                    del mapping[key]
        """,
        [
            check(
                "Restore after normal exit",
                (
                    "(lambda m: (exec(\"with temporary_value(m, 'x', 9):\\n    assert m["
                    "'x'] == 9\", globals(), {'m': m}), m)[1])({'x':1})"
                ),
                {"x": 1},
            ),
            check(
                "Remove a temporary key",
                (
                    "(lambda m: (exec(\"with temporary_value(m, 'x', 9):\\n    assert m["
                    "'x'] == 9\", globals(), {'m': m}), m)[1])({})"
                ),
                {},
            ),
            check(
                "Restore on exception",
                (
                    "(lambda m: (exec(\"try:\\n    with temporary_value(m, 'x', 9):\\n        "
                    "raise ValueError('stop')\\nexcept ValueError:\\n    pass\", globals(), {"
                    "'m': m}), m)[1])({'x':None})"
                ),
                {"x": None},
            ),
        ],
        [
            "Remember whether the key existed separately from its previous value.",
            "Put restoration inside finally so exceptions cannot skip it.",
        ],
    ),
    unit(
        "managed-contexts",
        "python-composition",
        "Implement the context protocol",
        "Class-based context managers",
        """
        class Closing:
            def __init__(self, resource):
                self.resource = resource
            def __enter__(self):
                return self.resource
            def __exit__(self, exc_type, exc_value, traceback):
                self.resource.close()
                return False

        class IgnoreValueError:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_value, traceback):
                return exc_type is not None and issubclass(exc_type, ValueError)
        """,
        [
            check(
                "Return and close resource",
                (
                    "(exec(\"from io import StringIO\\ns = StringIO('hello')\\nwith Closing(s)"
                    " as value:\\n    same = value is s\\n    text = value.read()\\nresult = [s"
                    'ame, text, s.closed]", globals()), result)[1]'
                ),
                [True, "hello", True],
            ),
            check(
                "Close and propagate failure",
                (
                    "(exec(\"from io import StringIO\\ns = StringIO('')\\ntry:\\n    with Clos"
                    "ing(s):\\n        raise RuntimeError('boom')\\nexcept RuntimeError as erro"
                    'r:\\n    result = [str(error), s.closed]", globals()), result)[1]'
                ),
                ["boom", True],
            ),
            check(
                "Suppress value subclasses",
                (
                    '(exec("class Specific(ValueError):\\n    pass\\nwith IgnoreValueError():\\'
                    "n    raise Specific('bad')\\nresult = True\", globals()), result)[1]"
                ),
                True,
            ),
            check(
                "Propagate unrelated failures",
                (
                    '(exec("result = False\\ntry:\\n    with IgnoreValueError():\\n        rais'
                    "e TypeError('wrong')\\nexcept TypeError:\\n    result = True\", globals()"
                    "), result)[1]"
                ),
                True,
            ),
            check(
                "Normal context exit",
                "(exec('with IgnoreValueError():\\n    result = 3', globals()), result)[1]",
                3,
            ),
        ],
        [
            (
                "Store resource in __init__, return it from __enter__, and close it once in"
                " __exit__."
            ),
            (
                "Only suppress when exc_type is not None and is a subclass of"
                " ValueError; Closing suppresses nothing."
            ),
        ],
    ),
    unit(
        "iterator-tools",
        "python-composition",
        "Consume only what you need",
        "Iterator composition",
        """
        def batches(items, size):
            if size <= 0:
                raise ValueError("Size must be positive")
            batch = []
            for item in items:
                batch.append(item)
                if len(batch) == size:
                    yield batch
                    batch = []
            if batch:
                yield batch
        """,
        [
            check("Keep final partial batch", "list(batches(range(5), 2))", [[0, 1], [2, 3], [4]]),
            check("Empty input", "list(batches([], 3))", []),
            check(
                "Remain lazy",
                (
                    "list(__import__('itertools').islice(batches(__import__('itertools')."
                    "count(), 2), 2))"
                ),
                [[0, 1], [2, 3]],
            ),
            check(
                "Reject zero size",
                "__raises_value_error__(lambda size: list(batches([], size)), 0)",
                True,
            ),
        ],
        [
            "Yield a new list for each batch; do not clear a list already yielded.",
            "After the loop, yield a nonempty partial batch. Validate the size first.",
        ],
    ),
    unit(
        "iterator-recipes",
        "python-composition",
        "Combine and bound iterators",
        "Chain, islice, zip_longest & product",
        """
        from itertools import chain, islice, zip_longest, product

        def preview(groups, limit):
            if limit < 0:
                raise ValueError("Negative limit")
            return list(islice(chain.from_iterable(groups), limit))

        def align(left, right):
            return list(zip_longest(left, right, fillvalue=None))

        def combinations(left, right):
            return list(product(left, right))
        """,
        [
            check("Flatten bounded preview", "preview([[1, 2], [], [3, 4]], 3)", [1, 2, 3]),
            check(
                "Do not read extra input items",
                (
                    "(exec('source = iter([1, 2, 3])\\nvalues = preview([source], 2)\\nresult ="
                    " [values, next(source)]', globals()), result)[1]"
                ),
                [[1, 2], 3],
            ),
            check(
                "Zero consumes nothing",
                (
                    "(exec('source = iter([7])\\nvalues = preview([source], 0)\\nresult = [valu"
                    "es, next(source)]', globals()), result)[1]"
                ),
                [[], 7],
            ),
            check("Negative limit", "__raises_value_error__(lambda n: preview([], n), -1)", True),
            check(
                "Pad either side",
                "(align([1], [2, 3]), align([1, 2], []))",
                [[[1, 2], [None, 3]], [[1, None], [2, None]]],
            ),
            check(
                "All pairs",
                "combinations(iter('ab'), iter([1, 2]))",
                [["a", 1], ["a", 2], ["b", 1], ["b", 2]],
            ),
            check("Empty combinations", "combinations([], [1])", []),
        ],
        [
            (
                "Combine chain.from_iterable with islice to avoid exhausting "
                "input during a bounded preview."
            ),
            (
                "Use zip_longest for padded alignment and product for every p"
                "air; ordinary zip does neither."
            ),
        ],
    ),
    unit(
        "adjacent-groups",
        "python-composition",
        "Group consecutive values",
        "Consecutive grouping with itertools",
        """
        from itertools import groupby

        def runs(items, key):
            for label, group in groupby(items, key=key):
                yield label, list(group)
        """,
        [
            check(
                "Keep separate runs",
                "list(runs('aabba', lambda x: x))",
                [["a", ["a", "a"]], ["b", ["b", "b"]], ["a", ["a"]]],
            ),
            check(
                "Apply key",
                "list(runs(iter(['Ada', 'Al', 'Bo']), lambda name: name[0]))",
                [["A", ["Ada", "Al"]], ["B", ["Bo"]]],
            ),
            check("Empty runs", "list(runs([], str))", []),
            check(
                "Return an iterator",
                "(lambda grouped: iter(grouped) is grouped)(runs('a', str))",
                True,
            ),
            check(
                "Unhashable labels",
                "list(runs([1, 1, 2], lambda x: [x]))",
                [[[1], [1, 1]], [[2], [2]]],
            ),
            check(
                "Groups remain usable",
                (
                    "(exec(\"groups = list(runs('aba', str))\\nresult = [list(group) for label"
                    ', group in groups]", globals()), result)[1]'
                ),
                [["a"], ["b"], ["a"]],
            ),
        ],
        [
            "groupby compares adjacent keys without sorting or requiring dictionary keys.",
            (
                "Copy each group into its own list before advancing the outer"
                " iterator, and yield the label and list."
            ),
        ],
    ),
    unit(
        "logging-basics",
        "python-composition",
        "Record what happened with logging",
        "logging",
        """
        import logging

        logger = logging.getLogger("inventory")


        def load_counts(lines):
            counts = {}
            for number, line in enumerate(lines, start=1):
                if not line.strip():
                    continue
                name, _, amount = line.partition(",")
                try:
                    counts[name.strip()] = int(amount)
                except ValueError:
                    logger.warning("Skipping line %d: bad count %r", number, amount.strip())
            logger.info("Loaded %d items", len(counts))
            return counts
        """,
        [
            probe(
                "Warn about a bad line and report the total",
                _log_script(
                    "inventory",
                    'load_counts(["rope,3", "lamp, many", "", "map,1"])',
                    "__probe_result__",
                ),
                [
                    {"rope": 3, "map": 1},
                    [["WARNING", "Skipping line 2: bad count 'many'"], ["INFO", "Loaded 2 items"]],
                    False,
                ],
                "load_counts(['rope,3', 'lamp, many', '', 'map,1']), collecting the inventory "
                "logger's records",
                "Use the inventory logger with %d and %r arguments; never configure logging.",
            ),
            probe(
                "A missing comma is a bad count",
                _log_script("inventory", 'load_counts(["rope"])', "__probe_result__"),
                [
                    {},
                    [["WARNING", "Skipping line 1: bad count ''"], ["INFO", "Loaded 0 items"]],
                    False,
                ],
                "load_counts(['rope']), collecting the inventory logger's records",
                "Without a comma the count text is empty, which int() rejects.",
            ),
            probe(
                "Nothing to load",
                _log_script("inventory", "load_counts([])", "__probe_result__"),
                [{}, [["INFO", "Loaded 0 items"]], False],
                "load_counts([]), collecting the inventory logger's records",
                "Log the INFO summary even when there are no lines.",
            ),
            check("Logging is not printing", "(load_counts(['tea,2']), __stdout__)[1]", ""),
        ],
        [
            "Create logger = logging.getLogger('inventory') once, at module level.",
            "Inside except ValueError, call logger.warning with the line number and the "
            "stripped count text as arguments.",
        ],
    ),
)

BUILD_INSTRUCTIONS = {
    "callable-tools": (
        "\nWrite `rank(records, key)` to return a new list sorted by the supplied o"
        "ne-argument callable.\nAccept finite one-pass iterables, preserve equal-ke"
        "y order, and leave a caller's list unchanged.\nEmpty input returns `[]`.\n"
        "Write `make_scaler(factor)` to return a reusable callable accepting one nu"
        "meric value and multiplying it by the numeric factor.\nNegative values and"
        " zero are allowed.\nFor example, `make_scaler(3)(4)` returns `12`: the fir"
        "st pair of parentheses creates the callable, and the second calls it with "
        "`4`.\nA closure, partial application, or another equivalent callable is va"
        "lid.\nDo not print or read input.\n"
    ).strip(),
    "functional-pipelines": (
        "\nWrite `transform_selected(items, predicate, transform)` returning a list"
        " of transformed values whose original values satisfy `predicate`.\nTest th"
        "e predicate before transforming; preserve order and accept finite one-pass"
        " iterables.\nWrite `fold(items, combine, initial)` applying `combine(accum"
        "ulator, item)` once per item from left to right.\nReturn the final accumul"
        "ator, or the original initial value for empty input.\nThe accumulator need"
        " not be numeric.\nFor example, `fold([2, 3], lambda acc, x: acc - x, 10)` "
        "returns `5`.\nLoops, comprehensions, and library implementations are all v"
        "alid.\nDo not print or read input.\n"
    ).strip(),
    "functions-with-memory": (
        "\nWrite `def collect(item, bucket=None):` so calls without a bucket get in"
        "dependent lists, while a supplied list is appended to and returned.\nAppen"
        "d `item` to the list using `.append(item)`.\nThen implement `twice(fn)`: i"
        "ts wrapper should call `fn` once and multiply the returned result by two."
        "\nForward positional and keyword arguments and preserve metadata with `@wr"
        "aps(fn)`.\n\nTry wrapping a function that adds two numbers.\nThe check sui"
        "te also verifies that the wrapped function is called only once.\n"
    ).strip(),
    "decorator-factories": (
        "\nWrite the decorator factory `prefixed(prefix)` for functions returning s"
        "trings.\nThe resulting decorated function must call the original once per "
        "call with unchanged positional and keyword arguments, then prepend the str"
        "ing prefix to its result.\nPreserve `__name__`, `__doc__`, and `__wrapped_"
        "_` metadata.\nApplying both prefixes must work together: `prefixed('A')(pr"
        "efixed('B')(lambda: 'C'))()` returns `'ABC'`.\nHere `lambda: 'C'` is a fun"
        "ction with no parameters that returns `'C'`, and the final `()` calls the "
        "fully wrapped function.\nEmpty prefixes are allowed.\nDo not print or read"
        " input.\n"
    ).strip(),
    "lazy-by-design": (
        "\nWrite `def positive_squares(numbers):` as a generator that yields the sq"
        "uare of each strictly positive number in order.\nSkip zero and negative nu"
        "mbers.\nAccept any iterable, including another generator, and do not conve"
        "rt the input or output to a list inside the function.\n\nCheck uses both f"
        "inite input and the first few results from an infinite stream.\n"
    ).strip(),
    "exception-boundaries": (
        "\nDefine `RecordError` as a subclass of `ValueError`.\nWrite `parse_record"
        "(text)` accepting a string and returning its `int` conversion, including w"
        "hitespace, signs, and zero.\nTranslate a conversion `ValueError` into `Rec"
        "ordError` with the original exception as its explicit cause; the message i"
        "s your choice.\nWrite `read_record(stream)` to call `stream.read()` once a"
        "nd pass its result to `parse_record`.\nAlways call `stream.close()` once a"
        "fter attempting the read, whether reading or parsing succeeds or fails.\nR"
        "eturn the parsed integer on success; let reading errors such as `OSError` "
        "propagate unchanged.\nAssume `close()` succeeds.\nThe stream is supplied b"
        "y the caller; do not open files, print, or read console input.\n"
    ).strip(),
    "context-practice": (
        "\nCreate `temporary_value(mapping, key, value)` as a context manager.\nDur"
        "ing `with temporary_value(...) as current`, the mapping must contain the t"
        "emporary value and `current` must be that same mapping object.\nOn exit, r"
        "estore the previous value if the key originally existed; otherwise remove "
        "the newly added key.\nRestore on both normal exit and exceptions, allowing"
        " the original exception to propagate.\nA preexisting value of `None` is a "
        "real value and must be restored.\nThe with-body will not remove the target"
        " key; nested use of your context manager should work.\nFor example, tempor"
        "arily changing `{'mode': 'safe'}` to mode `'fast'` must leave mode `'safe'"
        "` afterward.\nDo not print.\n"
    ).strip(),
    "managed-contexts": (
        "\nDefine `Closing(resource)` as a context manager returning the supplied r"
        "esource from `__enter__`.\nAfter the body, call its `close()` exactly once"
        " on normal and exceptional exits, and suppress no exceptions.\nAssume clos"
        "ing succeeds, and use a manager for only one `with` statement.\nAlso defin"
        "e `IgnoreValueError()` as a context manager suppressing only `ValueError` "
        "and its subclasses.\nIt must permit normal exit and propagate unrelated ex"
        "ceptions.\nDo not print, open files, or read input.\n"
    ).strip(),
    "iterator-tools": (
        "\nWrite the generator `batches(items, size)`.\n`size` is an integer and mu"
        "st be positive; raise `ValueError` for zero or negative sizes when iterati"
        "on starts.\nYield lists containing up to `size` consecutive items.\nYield "
        "a shorter final list if necessary, but never an empty batch.\nFor example,"
        " `list(batches('abcde', 3))` is `[['a', 'b', 'c'], ['d', 'e']]`.\nAccept o"
        "ne-pass and infinite iterables while consuming only enough input for the n"
        "ext requested batch.\nEach yielded batch must be a separate list.\nDo not "
        "print or read input.\n"
    ).strip(),
    "iterator-recipes": (
        "\nWrite `preview(groups, limit)` returning up to `limit` values flattened "
        "from an iterable of iterables.\n`limit` is an integer; reject negative val"
        "ues with `ValueError`, and consume no items for zero.\nNever consume more "
        "inner values than requested, and support one-pass groups and infinite inne"
        "r iterables.\nWrite `align(left, right)` returning a list of pairs padded "
        "with `None` through the longer finite input.\nWrite `combinations(left, ri"
        "ght)` returning all pairs of values from finite inputs, with the left inpu"
        "t changing slowest.\nAn empty input produces no combinations.\nReturn list"
        "s of tuples for pairs; do not print or read input.\nEquivalent implementat"
        "ions are welcome.\n"
    ).strip(),
    "adjacent-groups": (
        "\nWrite `runs(items, key)` returning an iterator of `(label, values)` tupl"
        "es for consecutive equal keys.\n`key` is a one-argument callable, and each"
        " `values` must be a separate list retaining the original items in order.\n"
        "Accept finite one-pass input; empty input yields nothing.\nDo not sort, me"
        "rge nonadjacent groups, or require hashable labels.\nFor example, `list(ru"
        "ns('aba', str))` is `[('a', ['a']), ('b', ['b']), ('a', ['a'])]`.\nSaved l"
        "ists must remain usable after the outer iterator advances.\nDo not print o"
        "r read input.\n"
    ).strip(),
    "logging-basics": (
        "Define `load_counts(lines)`, a reusable function that reads lines such as `rope,3` and "
        "returns a dictionary such as `{'rope': 3}`.\n"
        "The name is the text before the first comma, with surrounding spaces removed, and the "
        "count is the whole number after it.\n"
        "A later line with the same name replaces the earlier count, and blank lines are "
        "skipped silently.\n"
        "When `int()` rejects a count, including a line without a comma, skip the line and log "
        "a WARNING with exactly `Skipping line N: bad count 'TEXT'`.\n"
        "`N` counts lines from 1, including blank lines, and `'TEXT'` is the representation "
        "(`%r`) of the count text with surrounding spaces removed.\n"
        "After the last line, log INFO `Loaded K items`, where `K` is the number of names "
        "returned.\n"
        "Send every record through the logger named `inventory`.\n"
        "This is library code, so do not print, call `logging.basicConfig`, or add handlers."
    ),
}

REPAIR_STAGES = {
    "callable-tools": _repair(
        (
            "Define apply_twice(values, function) returning a new list with function ap"
            "plied two times to each value. Accept one-pass input and never mutate the "
            "source. Call function(function(value)) in input order, exactly twice for e"
            "ach item. Empty input returns []."
        ),
        """
        def apply_twice(values, function):
            result = []
            for value in values:
                result.append(function(function(value)))
            return result
        """,
        """
        def apply_twice(values, function):
            return [function(value) for value in values]
        """,
        [
            _check(
                "Apply twice",
                "apply_twice([1, 2], lambda x: x + 3)",
                [7, 8],
                "Call the supplied function once more on its result.",
            ),
            _check(
                "One-pass input",
                "apply_twice(iter([2]), lambda x: x * 2)",
                [8],
                "Build the output while consuming the iterator once.",
            ),
            _probe(
                "Call order and original input",
                (
                    """
                values = [1, 2]
                calls = []


                def advance(value):
                    calls.append(value)
                    return value + 10


                result = (apply_twice(values, advance), calls, values, apply_twice([], advance))
                """
                ),
                ([21, 22], [1, 11, 2, 12], [1, 2], []),
                "Finish both calls for one item before advancing to the next input.",
            ),
        ],
        [
            "The inner call produces the intermediate value.",
            "The outer call receives that intermediate value.",
        ],
    ),
    "functional-pipelines": _repair(
        (
            "Define partition(items, predicate) returning (matching, rejected) lists in"
            " input order. Call predicate once per item and accept a one-pass iterable."
            " Return a tuple containing two fresh lists. Preserve the original items, i"
            "ncluding duplicates, and return ([], []) for empty input."
        ),
        """
        def partition(items, predicate):
            matching, rejected = [], []
            for item in items:
                (matching if predicate(item) else rejected).append(item)
            return matching, rejected
        """,
        """
        def partition(items, predicate):
            return ([item for item in items if predicate(item)], [])
        """,
        [
            _check(
                "Separate values",
                "partition([1, 2, 3, 4], lambda x: x % 2 == 0)",
                ([2, 4], [1, 3]),
                "Append each item to exactly one output list.",
            ),
            _check(
                "Preserve order",
                "partition(iter([3, 1, 2]), lambda x: x > 1)",
                ([3, 2], [1]),
                "Do not sort either side.",
            ),
            _probe(
                "One predicate call per item",
                (
                    """
                calls = []
                values = [0, 1, 0]


                def choose(value):
                    calls.append(value)
                    return value == 0


                result = (partition(iter(values), choose), calls, values, partition([], choose))
                """
                ),
                (([0, 0], [1]), [0, 1, 0], [0, 1, 0], ([], [])),
                "Evaluate the predicate once and append the original item to exactly one list.",
            ),
        ],
        [
            "Create both result lists before the loop.",
            "The predicate decides which list receives the original item.",
        ],
    ),
    "functions-with-memory": _repair(
        (
            "Define memoize(fn). Return a callable that caches results by arguments, fo"
            "rwards keyword arguments, and calls fn only once for each repeated call. A"
            "ssume arguments and keyword values are hashable. Reordering keyword argume"
            "nts must reuse the cache; positional and keyword spellings may use separat"
            "e entries. Preserve function metadata with wraps. Cache successful results"
            " including None and False, but never cache exceptions. Each decorated func"
            "tion owns a separate cache."
        ),
        """
        from functools import wraps

        def memoize(fn):
            cache = {}

            @wraps(fn)
            def wrapper(*args, **kwargs):
                key = (args, tuple(sorted(kwargs.items())))
                if key not in cache:
                    cache[key] = fn(*args, **kwargs)
                return cache[key]

            return wrapper
        """,
        """
        def memoize(fn):
            def wrapper(*args, **kwargs):
                return fn(*args, **kwargs)
            return wrapper
        """,
        [
            _check(
                "Cache repeated calls",
                _exec(
                    """
                    calls = []

                    def add(value):
                        calls.append(value)
                        return value * 2

                    cached = memoize(add)
                    result = [cached(3), cached(3), calls]
                    """
                ),
                [6, 6, [3]],
                "The same wrapper should call its function once for repeated arguments.",
            ),
            _check(
                "Preserve metadata",
                "(lambda f: [memoize(f).__name__, memoize(f).__wrapped__ is f])(lambda: None)",
                ["<lambda>", True],
                "Use wraps around the returned wrapper.",
            ),
            _probe(
                "Keyword order, falsy results, and separate caches",
                (
                    """
                calls = []


                def function(**kwargs):
                    calls.append(dict(kwargs))
                    return None


                first = memoize(function)
                second = memoize(function)
                result = [first(a=1, b=2), first(b=2, a=1), second(a=1, b=2), len(calls)]
                """
                ),
                [None, None, None, 2],
                (
                    "Cache by stable keyword pairs, test membership rather than truthiness, and"
                    " give each wrapper its own cache."
                ),
            ),
            _probe(
                "Failed calls are retried",
                (
                    """
                calls = []


                def unstable(value):
                    calls.append(value)
                    if len(calls) == 1:
                        raise ValueError("retry")
                    return False


                cached = memoize(unstable)
                try:
                    cached(2)
                except ValueError:
                    pass
                result = (cached(2), cached(2), calls)
                """
                ),
                (False, False, [2, 2]),
                "Store a result only after the wrapped function returns successfully.",
            ),
        ],
        [
            "Keep a cache in the closure created by memoize.",
            "Include both positional and keyword arguments in a stable key.",
        ],
    ),
    "decorator-factories": _repair(
        (
            "Define tagged(label) as a decorator. It must preserve the wrapped function"
            "'s behavior and metadata while adding a label attribute to the wrapper. Re"
            "turn a separate wrapper, leaving the original function unchanged. Forward "
            "all positional and keyword arguments and return its result unchanged."
        ),
        """
        from functools import wraps

        def tagged(label):
            def decorate(function):
                @wraps(function)
                def wrapper(*args, **kwargs):
                    return function(*args, **kwargs)
                wrapper.label = label
                return wrapper
            return decorate
        """,
        """
        def tagged(label):
            def decorate(function):
                def wrapper(value):
                    return function(value)
                return wrapper
            return decorate
        """,
        [
            _check(
                "Attach label",
                "(lambda f: tagged('slow')(f).label)(lambda: 1)",
                "slow",
                "Set the label on the wrapper returned by the decorator.",
            ),
            _check(
                "Forward keywords",
                "tagged('x')(lambda *, value: value)(value=4)",
                4,
                "Forward both argument forms with *args and **kwargs.",
            ),
            _check(
                "Preserve name",
                "(lambda f: tagged('x')(f).__name__)(lambda: None)",
                "<lambda>",
                "Apply functools.wraps to the wrapper.",
            ),
            _probe(
                "Do not modify the original callable",
                (
                    """
                def function(value, *, extra):
                    return value + extra


                wrapped = tagged("audit")(function)
                result = (
                    wrapped is function,
                    hasattr(function, "label"),
                    wrapped(2, extra=4),
                    wrapped.__wrapped__ is function,
                )
                """
                ),
                (False, False, 6, True),
                (
                    "Attach the label to a metadata-preserving wrapper, not to the original cal"
                    "lable."
                ),
            ),
        ],
        [
            "The factory receives the label before the function exists.",
            "The decorator returns a wrapper with the same call contract.",
        ],
    ),
    "lazy-by-design": _repair(
        (
            "Define take_until(values, stop). Yield values in order through the first i"
            "tem for which stop(item) is true, then stop. Keep the function lazy and ac"
            "cept infinite input. If no item matches, yield the entire source. Empty in"
            "put yields nothing. Do not read another item after the matching boundary; "
            "call stop once per consumed item as iteration advances."
        ),
        """
        def take_until(values, stop):
            for value in values:
                yield value
                if stop(value):
                    return
        """,
        """
        def take_until(values, stop):
            return [value for value in values if not stop(value)]
        """,
        [
            _check(
                "Include boundary",
                "list(take_until([1, 2, 3, 4], lambda x: x >= 3))",
                [1, 2, 3],
                "Yield the stopping item before ending.",
            ),
            _check(
                "Remain lazy",
                _exec(
                    "\n                    import itertools\n\n                    def source()"
                    ":\n                        yield 0\n                        yield 1\n     "
                    '                   raise AssertionError("over-consumed")\n\n              '
                    "      try:\n                        result = list(\n                      "
                    "      itertools.islice(take_until(source(), lambda value: value == 1), 2)"
                    "\n                        )\n                    except AssertionError:\n "
                    "                       result = False\n                    "
                ),
                [0, 1],
                "Stop after the boundary without asking the source for another item.",
            ),
            _probe(
                "Stop without reading beyond the boundary",
                (
                    """
                seen = []


                def source():
                    for value in (1, 2):
                        seen.append(value)
                        yield value
                    raise AssertionError("read beyond stop")


                stream = take_until(source(), lambda value: value == 2)
                before = list(seen)
                result = (before, list(stream), seen, list(take_until([], bool)))
                """
                ),
                ([], [1, 2], [1, 2], []),
                (
                    "Creation is lazy; exhaustion after the matching item must not advance the "
                    "source."
                ),
            ),
        ],
        [
            "Yield each value as it arrives.",
            "Return from the generator after yielding the first matching value.",
        ],
    ),
    "exception-boundaries": _repair(
        (
            "Define PairError and parse_pair(text). Parse exactly two comma-separated i"
            "ntegers, translate malformed values to PairError from the original ValueEr"
            "ror, and reject other shapes. PairError subclasses ValueError. Return a tu"
            "ple of two ints. Wrong field counts raise PairError; conversion failures m"
            "ust chain their original ValueError. Whitespace and signed integer text ar"
            "e valid."
        ),
        """
        class PairError(ValueError):
            pass

        def parse_pair(text):
            parts = text.split(',')
            if len(parts) != 2:
                raise PairError("Expected two values")
            try:
                return tuple(int(part.strip()) for part in parts)
            except ValueError as error:
                raise PairError("Invalid pair") from error
        """,
        """
        class PairError(ValueError):
            pass

        def parse_pair(text):
            return tuple(int(part) for part in text.split(','))
        """,
        [
            _check(
                "Parse pair",
                "parse_pair(' 2, -3 ')",
                (2, -3),
                "Split once conceptually into two trimmed integer fields.",
            ),
            _check(
                "Keep cause",
                _exec(
                    """
                    try:
                        parse_pair("x,2")
                    except PairError as error:
                        result = type(error.__cause__) is ValueError
                    """
                ),
                True,
                "Raise PairError from the caught ValueError.",
            ),
            _check(
                "Reject shape",
                "__raises_value_error__(parse_pair, '1,2,3')",
                True,
                "Validate the number of fields before converting.",
            ),
            _probe(
                "Reject every wrong shape with PairError",
                (
                    """
                result = []
                for text in ("", "1", "1,2,3"):
                    try:
                        parse_pair(text)
                    except PairError:
                        result.append(True)
                    else:
                        result.append(False)
                """
                ),
                [True, True, True],
                "All shape failures use the documented domain exception.",
            ),
        ],
        [
            "Validate the comma-separated shape first.",
            "Use raise PairError(...) from error for conversion failures.",
        ],
    ),
    "context-practice": _repair(
        (
            "Define temporary_keys(mapping, updates) as a context manager. Apply all up"
            "dates temporarily, then restore prior values and remove keys that did not "
            "exist, even on errors. Yield the original mapping from __enter__. Only upd"
            "ated keys are restored; unrelated changes in the body remain. Existing Non"
            "e values differ from absent keys. Nested contexts must restore the state o"
            "f their own entry."
        ),
        """
        from contextlib import contextmanager

        @contextmanager
        def temporary_keys(mapping, updates):
            missing = object()
            previous = {key: mapping.get(key, missing) for key in updates}
            mapping.update(updates)
            try:
                yield mapping
            finally:
                for key, value in previous.items():
                    if value is missing:
                        mapping.pop(key, None)
                    else:
                        mapping[key] = value
        """,
        """
        from contextlib import contextmanager

        @contextmanager
        def temporary_keys(mapping, updates):
            mapping.update(updates)
            yield mapping
        """,
        [
            _check(
                "Restore and remove",
                _exec_with(
                    """
                    with temporary_keys(m, {"a": 2, "b": 3}):
                        pass
                    result = m
                    """,
                    "{'m': {'a': 1}}",
                ),
                {"a": 1},
                "Restore existing keys and remove newly introduced keys.",
            ),
            _check(
                "Restore on error",
                _exec_with(
                    """
                    try:
                        with temporary_keys(m, {"a": 2}):
                            raise ValueError
                    except ValueError:
                        pass
                    result = m
                    """,
                    "{'m': {'a': 1}}",
                ),
                {"a": 1},
                "Put restoration in finally.",
            ),
            _probe(
                "Nested contexts preserve None and unrelated edits",
                (
                    """
                mapping = {"a": None}
                with temporary_keys(mapping, {"a": 1, "b": 2}) as entered:
                    same = entered is mapping
                    mapping["keep"] = 4
                    with temporary_keys(mapping, {"a": 3}):
                        pass
                    inner_restored = mapping["a"] == 1
                result = (same, inner_restored, mapping)
                """
                ),
                (True, True, {"a": None, "keep": 4}),
                (
                    "Use a unique missing-key sentinel and restore only the keys owned by this "
                    "context."
                ),
            ),
        ],
        [
            "Remember a sentinel for keys that were absent.",
            "Update first, then restore every remembered key in finally.",
        ],
    ),
    "managed-contexts": _repair(
        (
            "Define Logged(resource, events). On enter append 'enter' and return the re"
            "source; on exit close it, append 'exit', and never suppress the body's exc"
            "eption. Close exactly once per exit, including on body errors. Append exit"
            " even when close raises; that closing error propagates. Yield the exact or"
            "iginal resource from with."
        ),
        """
        class Logged:
            def __init__(self, resource, events):
                self.resource = resource
                self.events = events
            def __enter__(self):
                self.events.append("enter")
                return self.resource
            def __exit__(self, exc_type, exc_value, traceback):
                try:
                    self.resource.close()
                finally:
                    self.events.append("exit")
                return False
        """,
        """
        class Logged:
            def __init__(self, resource, events):
                self.resource = resource
                self.events = events
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_value, traceback):
                self.events.append("enter")
                return True
        """,
        [
            _check(
                "Enter and close",
                "(lambda e, r: (lambda cm: ("
                "cm.__enter__() is r, cm.__exit__(None, None, None), "
                "[e, r.closed]))(Logged(r, e)))([], "
                "__import__('io').StringIO())[2]",
                [["enter", "exit"], True],
                "Return the resource, close it, and record both transitions.",
            ),
            _check(
                "Propagate failure",
                (
                    "(lambda e, r: (lambda cm: (cm.__enter__(), cm.__exit__(RuntimeError, Runti"
                    "meError(), None), [e, r.closed]))(Logged(r, e)))([], __import__('io').Stri"
                    "ngIO())[2]"
                ),
                [["enter", "exit"], True],
                "Return False from __exit__.",
            ),
            _probe(
                "The with statement propagates body errors",
                (
                    """
                events = []


                class Resource:
                    closes = 0

                    def close(self):
                        self.closes += 1


                resource = Resource()
                try:
                    with Logged(resource, events) as entered:
                        same = entered is resource
                        raise RuntimeError("body")
                except RuntimeError as error:
                    propagated = str(error)
                else:
                    propagated = "swallowed"
                result = (same, resource.closes, events, propagated)
                """
                ),
                (True, 1, ["enter", "exit"], "body"),
                (
                    "A truthy __exit__ return suppresses the body exception. Test the actual wi"
                    "th flow."
                ),
            ),
            _probe(
                "Exit is recorded if close fails",
                (
                    """
                events = []


                class Resource:
                    def close(self):
                        raise OSError("close")


                try:
                    with Logged(Resource(), events):
                        pass
                except OSError as error:
                    result = (events, str(error))
                """
                ),
                (["enter", "exit"], "close"),
                "Record exit in finally even when closing the resource raises.",
            ),
        ],
        [
            "__enter__ returns the object used by the with body.",
            "Cleanup belongs in __exit__, and a false return preserves errors.",
        ],
    ),
    "iterator-tools": _repair(
        (
            "Define windowed(items, size) as a lazy generator of overlapping tuples. Re"
            "ject nonpositive sizes. A size-three input 1,2,3,4 yields (1,2,3) then (2,"
            "3,4). Size is an integer. Yield no partial windows. Read at most size item"
            "s for the first window and one more for each subsequent window. Empty or s"
            "horter input yields nothing; size 1 yields singleton tuples."
        ),
        """
        from collections import deque

        def windowed(items, size):
            if size <= 0:
                raise ValueError("Size must be positive")
            window = deque(maxlen=size)
            for item in items:
                window.append(item)
                if len(window) == size:
                    yield tuple(window)
        """,
        """
        def windowed(items, size):
            if size <= 0:
                raise ValueError("Size must be positive")
            batch = []
            for item in items:
                batch.append(item)
                if len(batch) == size:
                    yield tuple(batch)
                    batch = []
        """,
        [
            _check(
                "Overlap windows",
                "list(windowed([1, 2, 3, 4], 3))",
                [(1, 2, 3), (2, 3, 4)],
                "Discard only the oldest item after a full window.",
            ),
            _check(
                "Reject invalid size",
                "__raises_value_error__(lambda n: list(windowed([], n)), 0)",
                True,
                "Validate size before consuming input.",
            ),
            _probe(
                "Bounded reading and short windows",
                (
                    """
                def source():
                    yield 1
                    yield 2
                    yield 3
                    raise AssertionError("eager read")


                stream = windowed(source(), 2)
                result = (
                    next(stream),
                    next(stream),
                    list(windowed([1], 2)),
                    list(windowed([0, 0], 1)),
                )
                """
                ),
                ((1, 2), (2, 3), [], [(0,), (0,)]),
                "Only advance enough to form the next overlapping window.",
            ),
        ],
        [
            "A deque with maxlen keeps the previous items.",
            "Yield only full windows and let the next item overlap.",
        ],
    ),
    "iterator-recipes": _repair(
        (
            "Define interleave(left, right) returning a lazy iterator that alternates v"
            "alues and continues with the longer input after the other ends. Start with"
            " the left input, preserve duplicates and None, and support one-pass or inf"
            "inite sources. Consume at most one item from each side ahead of the yielde"
            "d pair; do not exhaust either input eagerly."
        ),
        """
        from itertools import zip_longest

        _missing = object()

        def interleave(left, right):
            for first, second in zip_longest(left, right, fillvalue=_missing):
                if first is not _missing:
                    yield first
                if second is not _missing:
                    yield second
        """,
        """
        def interleave(left, right):
            return iter(list(left) + list(right))
        """,
        [
            _check(
                "Alternate values",
                "list(interleave([1, 3], [2, 4, 6]))",
                [1, 2, 3, 4, 6],
                "Zip with padding and emit each available side in order.",
            ),
            _check(
                "Stay lazy",
                "next(interleave(iter([1]), iter([2])))",
                1,
                "Return an iterator or generator instead of collecting eagerly.",
            ),
            _probe(
                "Do not exhaust either source",
                (
                    """
                def left():
                    yield None
                    raise AssertionError("eager left")


                def right():
                    yield 2
                    raise AssertionError("eager right")


                stream = interleave(left(), right())
                result = (next(stream), next(stream), list(interleave([], [None, 3])))
                """
                ),
                (None, 2, [None, 3]),
                "Keep the sources lazy and distinguish a missing sentinel from a real None.",
            ),
        ],
        [
            "zip_longest exposes both sides without truncating.",
            "Use a unique sentinel so real None values are retained.",
        ],
    ),
    "adjacent-groups": _repair(
        (
            "Define run_lengths(items, key) yielding (label, count) for each consecutiv"
            "e run. Do not merge later runs and do not require labels to be hashable. K"
            "eep each group lazy until its count is needed; detecting a boundary may re"
            "ad one item ahead. Empty input yields nothing. Return tuples, preserving l"
            "abels even when they are lists."
        ),
        """
        from itertools import groupby

        def run_lengths(items, key):
            for label, group in groupby(items, key=key):
                yield label, sum(1 for _ in group)
        """,
        """
        def run_lengths(items, key):
            counts = {}
            for item in items:
                label = key(item)
                counts[label] = counts.get(label, 0) + 1
            return iter(counts.items())
        """,
        [
            _check(
                "Separate runs",
                "list(run_lengths('aabba', str))",
                [["a", 2], ["b", 2], ["a", 1]],
                "Group only adjacent equal keys.",
            ),
            _check(
                "Unhashable labels",
                "list(run_lengths([1, 1, 2], lambda x: [x]))",
                [[[1], 2], [[2], 1]],
                "Use equality-based grouping rather than a dictionary.",
            ),
            _probe(
                "Empty stream and bounded run consumption",
                (
                    """
                def source():
                    yield "a"
                    yield "a"
                    yield "b"
                    raise AssertionError("eager grouping")


                result = (next(run_lengths(source(), str)), list(run_lengths([], str)))
                """
                ),
                (("a", 2), []),
                "Count one adjacent run at a time; only its boundary needs a lookahead.",
            ),
        ],
        [
            "groupby gives each adjacent run a separate group iterator.",
            "Consume each group to count it before advancing.",
        ],
    ),
    "logging-basics": _repair(
        "Repair `settle(amounts)` in this reusable payments module.\n"
        "`amounts` is a list of strings, and each whole number is added to a running total.\n"
        "For an amount that `int()` rejects, log at ERROR level with the exception attached, "
        "using the message `Payment N failed`, where `N` counts from 1.\n"
        "After processing every amount, log INFO `Total: T` and return the total.\n"
        "Send every record through the logger named `payments`, and do not configure logging in "
        "this module.",
        """
        import logging

        logger = logging.getLogger("payments")


        def settle(amounts):
            total = 0
            for index, amount in enumerate(amounts, start=1):
                try:
                    total += int(amount)
                except ValueError:
                    logger.exception("Payment %d failed", index)
            logger.info("Total: %d", total)
            return total
        """,
        """
        import logging


        def settle(amounts):
            logging.basicConfig(level=logging.DEBUG)
            total = 0
            for index, amount in enumerate(amounts, start=1):
                try:
                    total += int(amount)
                except ValueError:
                    pass
                else:
                    continue
                logging.error("Payment %d failed", index)
            logging.info("Total: %d", total)
            return total
        """,
        [
            _probe(
                "A failed payment keeps its traceback",
                _log_script("payments", 'settle(["5", "x", "7"])', "result", traceback=True),
                [12, [["ERROR", "Payment 2 failed", True], ["INFO", "Total: 12", False]], False],
                "Log through logging.getLogger('payments') and use its exception method inside "
                "except.",
            ),
            _probe(
                "Valid payments only",
                _log_script("payments", 'settle(["1", "2"])', "result", traceback=True),
                [3, [["INFO", "Total: 3", False]], False],
                "A reusable module must not call basicConfig; the application configures logging.",
            ),
            _probe(
                "No payments",
                _log_script("payments", "settle([])", "result", traceback=True),
                [0, [["INFO", "Total: 0", False]], False],
                "Log the total through the payments logger even when nothing was paid.",
            ),
        ],
        (
            "Compare logging.error(...) with a named logger's exception method.",
            "Find the line that configures logging and ask who should own that choice.",
        ),
    ),
}

EXTRA_CHECKS = {
    "exception-boundaries": (
        probe(
            "Read and close exactly once on every exit",
            """
            class CountingStream:
                def __init__(self, text, error=None):
                    self.text = text
                    self.error = error
                    self.reads = self.closes = 0
                def read(self):
                    self.reads += 1
                    if self.error is not None:
                        raise self.error
                    return self.text
                def close(self):
                    self.closes += 1
            results = []
            for text in ["7", "invalid"]:
                stream = CountingStream(text)
                try:
                    value = read_record(stream)
                except RecordError:
                    value = "invalid"
                results.append([value, stream.reads, stream.closes])
            original = OSError("disk")
            stream = CountingStream("", original)
            try:
                read_record(stream)
            except OSError as error:
                results.append([error is original, stream.reads, stream.closes])
            else:
                raise AssertionError("Reading failure was hidden")
            __probe_result__ = results
            """,
            [[7, 1, 1], ["invalid", 1, 1], [True, 1, 1]],
            "Count read and close calls on success, parsing failure, and reading failure; "
            "the original reading exception must propagate unchanged.",
            "Read once inside try, close once in finally, and preserve unrelated exceptions.",
        ),
    ),
    "managed-contexts": (
        probe(
            "Close exactly once on normal and exceptional exits",
            """
            class CountingResource:
                def __init__(self):
                    self.closes = 0
                def close(self):
                    self.closes += 1
            normal = CountingResource()
            with Closing(normal) as value:
                inside = [value is normal, normal.closes]
            failed = CountingResource()
            original = RuntimeError("body failed")
            try:
                with Closing(failed):
                    raise original
            except RuntimeError as error:
                unchanged = error is original
            else:
                raise AssertionError("Body failure was hidden")
            __probe_result__ = [inside, normal.closes, failed.closes, unchanged]
            """,
            [[True, 0], 1, 1, True],
            "The resource stays open inside the body and closes once afterward, "
            "including when the original body exception propagates.",
            "Close in __exit__ once; return a false value to preserve the body exception.",
        ),
    ),
    "context-practice": (
        probe(
            "Nested contexts preserve identity",
            """
            mapping = {"mode": "safe"}
            with temporary_value(mapping, "mode", "fast") as current:
                assert current is mapping
                with temporary_value(mapping, "mode", "test"):
                    assert mapping["mode"] == "test"
                assert mapping["mode"] == "fast"
            __probe_result__ = mapping
            """,
            {"mode": "safe"},
            (
                "Nest temporary modes fast and test over safe; verify the yielded object "
                "is the original mapping and each prior value returns."
            ),
            "Each context call needs its own remembered prior value.",
        ),
    ),
}
