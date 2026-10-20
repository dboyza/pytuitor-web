"""Optional depth reviews: one prediction, one repair, one small implementation."""

from pytuitor_web.content.reviews.authoring import chapter, prediction, task

DEPTH = {
    "python-semantics": chapter(
        "python-semantics",
        prediction(
            "An alias",
            """
                a = [1]
                b = a
                b.append(2)
                print(a)
            """,
            ("[1]", "[1, 2]", "[2]"),
            1,
            "Both names refer to the same list.",
        ),
        task(
            "Repair a shared default",
            "collect(value, items=None) appends value and returns "
            "items. When omitted, each call gets a fresh list. A "
            "supplied list is updated in place.",
            """
                def collect(value, items=None):
                    if items is None:
                        items = []
                    items.append(value)
                    return items
            """,
            [
                ("Independent defaults", "[collect(1), collect(2)]", [[1], [2]]),
                (
                    "Supplied list",
                    "(exec('items = [0]\\nresult = collect(3, items)', "
                    "globals()), [items, result is items])[1]",
                    [[0, 3], True],
                ),
            ],
            broken="""
                def collect(value, items=[]):
                    items.append(value)
                    return items
            """,
            hint="Create a list inside the call when the argument is omitted.",
        ),
        task(
            "Copy before editing",
            "without_first(items) returns a new list containing all "
            "but the first item. Preserve the input. Empty input gives [].",
            """
                def without_first(items):
                    return items[1:]
            """,
            [
                ("Suffix", "without_first([1, 2, 3])", [2, 3]),
                ("Empty", "without_first([])", []),
                (
                    "Input preserved",
                    "(exec('a = [1, 2]\\nb = without_first(a)', globals()), [a, b is a])[1]",
                    [[1, 2], False],
                ),
            ],
            hint="A slice produces a separate list.",
        ),
    ),
    "recursion-and-callables": chapter(
        "recursion-and-callables",
        prediction(
            "A recursive sum",
            """
                def total(n):
                    return 0 if n == 0 else n + total(n - 1)


                print(total(3))
            """,
            ("3", "6", "0"),
            1,
            "The calls contribute 3 + 2 + 1 + 0.",
        ),
        task(
            "Repair a base case",
            "factorial(n) returns n! for nonnegative integers, including factorial(0) == 1.",
            """
                def factorial(n):
                    if n == 0:
                        return 1
                    return n * factorial(n - 1)
            """,
            [("Zero", "factorial(0)", 1), ("Four", "factorial(4)", 24)],
            broken="""
                def factorial(n):
                    if n == 0:
                        return 0
                    return n * factorial(n - 1)
            """,
            hint="The multiplicative identity is 1.",
        ),
        task(
            "Make a multiplier",
            "multiplier(factor) returns a callable that multiplies its "
            "argument by factor. Callables created with different "
            "factors stay independent.",
            """
                def multiplier(factor):
                    def apply(value):
                        return value * factor

                    return apply
            """,
            [
                ("Two factors", "[multiplier(2)(5), multiplier(3)(5)]", [10, 15]),
                ("Zero", "multiplier(0)(7)", 0),
            ],
            hint="The inner function can retain the enclosing factor.",
        ),
    ),
    "decorators": chapter(
        "decorators",
        prediction(
            "Wrapping a result",
            """
                def twice(fn):
                    def wrapped():
                        return fn() * 2

                    return wrapped


                @twice
                def value():
                    return 3


                print(value())
            """,
            ("3", "6", "None"),
            1,
            "The decorated name refers to wrapped, which doubles the returned value.",
        ),
        task(
            "Repair argument forwarding",
            "logged(fn) decorates any callable, forwards positional "
            "and keyword arguments, preserves metadata with wraps, and "
            "returns its result. No logging output is required.",
            """
                from functools import wraps


                def logged(fn):
                    @wraps(fn)
                    def wrapper(*args, **kwargs):
                        return fn(*args, **kwargs)

                    return wrapper
            """,
            [
                ("Arguments and result", "logged(lambda a, b=0: a + b)(2, b=4)", 6),
                ("Metadata", "logged(sum).__name__", "sum"),
            ],
            broken="""
                from functools import wraps


                def logged(fn):
                    @wraps(fn)
                    def wrapper(*args, **kwargs):
                        fn(*args, **kwargs)

                    return wrapper
            """,
            hint="Forward the return value as well as the arguments.",
        ),
        task(
            "Decorate a text result",
            "uppercase(fn) preserves metadata, forwards all arguments, "
            "and uppercases the text returned by fn.",
            """
                from functools import wraps


                def uppercase(fn):
                    @wraps(fn)
                    def wrapper(*args, **kwargs):
                        return fn(*args, **kwargs).upper()

                    return wrapper
            """,
            [
                (
                    "Keyword forwarding",
                    'uppercase(lambda name="A": "hi " + name)(name="Bo")',
                    "HI BO",
                ),
                ("Metadata", "uppercase(str).__name__", "str"),
            ],
            hint="Change the result inside the wrapper, after calling the original.",
        ),
    ),
    "iterators-and-streaming": chapter(
        "iterators-and-streaming",
        prediction(
            "A consumed iterator",
            """
                it = iter([1, 2, 3])
                print(next(it), list(it))
            """,
            ("1 [1, 2, 3]", "1 [2, 3]", "3 []"),
            1,
            "next consumes the first item; list consumes only those remaining.",
        ),
        task(
            "Repair a streaming filter",
            "positives(values) yields positive numbers in order. "
            "Accept any iterable, including a one-use iterator. Zero "
            "is excluded.",
            """
                def positives(values):
                    for value in values:
                        if value > 0:
                            yield value
            """,
            [
                ("Boundary and order", "list(positives(iter([0, 2, -1, 4])))", [2, 4]),
                ("Empty", "list(positives(iter([])))", []),
            ],
            broken="""
                def positives(values):
                    for value in values:
                        if value >= 0:
                            yield value
            """,
            hint="Keep zero outside the positive branch.",
        ),
        task(
            "Yield running totals",
            "running(values) yields the total so far after each value. "
            "Accept a one-use iterable. Empty input yields nothing.",
            """
                def running(values):
                    total = 0
                    for value in values:
                        total += value
                        yield total
            """,
            [
                ("Totals", "list(running(iter([2, -1, 4])))", [2, 1, 5]),
                ("Empty", "list(running([]))", []),
            ],
            hint="Keep the accumulator outside the loop and yield inside it.",
        ),
    ),
    "exceptions-and-contexts": chapter(
        "exceptions-and-contexts",
        prediction(
            "Cleanup on return",
            """
                def example():
                    try:
                        return 2
                    finally:
                        print("close")


                print(example())
            """,
            ("2\nclose", "close\n2", "2"),
            1,
            "finally runs before the pending return completes.",
        ),
        task(
            "Repair exception scope",
            "parse(text) returns int(text), or None on ValueError "
            "only. Other exceptions must propagate.",
            """
                def parse(text):
                    try:
                        return int(text)
                    except ValueError:
                        return None
            """,
            [
                ("Bad text", 'parse("no")', None),
                ("Valid text", 'parse("3")', 3),
                (
                    "TypeError propagates",
                    "(exec('try:\\n    parse(None)\\nexcept TypeError:\\n "
                    "   propagated = True\\nelse:\\n    propagated = "
                    "False', globals()), propagated)[1]",
                    True,
                ),
            ],
            broken="""
                def parse(text):
                    try:
                        return int(text)
                    except Exception:
                        return None
            """,
            hint="Catch only the error the contract promises to handle.",
        ),
        task(
            "Guarantee cleanup",
            "using(resource, action) calls action(resource), returns "
            "its result, and always calls resource.close(), even when "
            "action raises. Preserve the original action exception if "
            "close succeeds.",
            """
                def using(resource, action):
                    try:
                        return action(resource)
                    finally:
                        resource.close()
            """,
            [
                (
                    "Success closes",
                    '(exec("from io import StringIO\\nr = '
                    "StringIO('hi')\\nanswer = using(r, lambda s: "
                    's.read())", globals()), [answer, r.closed])[1]',
                    ["hi", True],
                ),
                (
                    "Failure closes",
                    "(exec('from io import StringIO\\nr = "
                    "StringIO()\\ntry:\\n    using(r, lambda s: 1 / "
                    "0)\\nexcept ZeroDivisionError:\\n    caught = "
                    "True\\nelse:\\n    caught = False', globals()), "
                    "[caught, r.closed])[1]",
                    [True, True],
                ),
            ],
            hint="A finally block runs on both success and failure.",
        ),
    ),
    "dataclasses-and-types": chapter(
        "dataclasses-and-types",
        prediction(
            "Generated equality",
            """
                from dataclasses import dataclass


                @dataclass
                class Point:
                    x: int


                print(Point(2) == Point(2))
            """,
            ("True", "False", "Error"),
            0,
            "Dataclasses compare the values of their fields by default.",
        ),
        task(
            "Repair a field factory",
            "Define dataclass Basket with items: list[str], a fresh "
            "empty list by default. A supplied list must remain usable.",
            """
                from dataclasses import dataclass, field


                @dataclass
                class Basket:
                    items: list[str] = field(default_factory=list)
            """,
            [
                (
                    "Independent baskets",
                    '(exec("a = Basket()\\nb = '
                    "Basket()\\na.items.append('map')\", globals()), "
                    "[a.items, b.items])[1]",
                    [["map"], []],
                ),
                ("Supplied items", 'Basket(["rope"]).items', ["rope"]),
            ],
            broken="""
                from dataclasses import dataclass


                @dataclass
                class Basket:
                    items: list[str] = []
            """,
            hint="A factory creates a default value for each new instance.",
        ),
        task(
            "Define an immutable record",
            "Define frozen dataclass Reading with station: str and "
            "value: float. Construction and equality should use both "
            "fields; assigning a field after construction must fail.",
            """
                from dataclasses import dataclass


                @dataclass(frozen=True)
                class Reading:
                    station: str
                    value: float
            """,
            [
                ("Fields", '[Reading("A", 2.5).station, Reading("A", 2.5).value]', ["A", 2.5]),
                ("Equality", 'Reading("A", 2.5) == Reading("A", 2.5)', True),
                (
                    "Frozen",
                    "(exec(\"r = Reading('A', 1.0)\\ntry:\\n    r.value = "
                    "2.0\\nexcept AttributeError:\\n    frozen = "
                    'True\\nelse:\\n    frozen = False", globals()), frozen)[1]',
                    True,
                ),
            ],
            hint="The frozen option rejects later field assignment.",
        ),
    ),
    "object-protocols-and-testing": chapter(
        "object-protocols-and-testing",
        prediction(
            "A sized object",
            """
                class Group:
                    def __len__(self):
                        return 0


                print(bool(Group()))
            """,
            ("True", "False", "0"),
            1,
            "Without __bool__, a zero length makes the object false in a condition.",
        ),
        task(
            "Repair containment",
            "Shelf(items) copies items. The in operator tests values "
            "in that copy, not numeric positions. len returns the "
            "number of items.",
            """
                class Shelf:
                    def __init__(self, items):
                        self.items = list(items)

                    def __contains__(self, value):
                        return value in self.items

                    def __len__(self):
                        return len(self.items)
            """,
            [
                (
                    "Values and length",
                    "(exec(\"s = Shelf(['map', 'rope'])\", globals()), "
                    '["map" in s, 0 in s, len(s)])[1]',
                    [True, False, 2],
                )
            ],
            broken="""
                class Shelf:
                    def __init__(self, items):
                        self.items = list(items)

                    def __contains__(self, value):
                        return value in range(len(self.items))

                    def __len__(self):
                        return len(self.items)
            """,
            hint="Containment should consult stored values.",
        ),
        task(
            "Make a repeatable iterable",
            "Labels(items) copies the iterable. Each iteration over a "
            "Labels instance must start from the beginning, preserving "
            "order and repeats.",
            """
                class Labels:
                    def __init__(self, items):
                        self.items = list(items)

                    def __iter__(self):
                        return iter(self.items)
            """,
            [
                (
                    "Repeat iteration",
                    "(exec(\"labels = Labels(iter(['A', 'A']))\", "
                    "globals()), [list(labels), list(labels)])[1]",
                    [["A", "A"], ["A", "A"]],
                ),
                ("Empty", "list(Labels([]))", []),
            ],
            hint="Return a fresh iterator for every __iter__ call.",
        ),
    ),
    "async-work": chapter(
        "async-work",
        prediction(
            "Await a result",
            """
                import asyncio


                async def value():
                    return 4


                print(asyncio.run(value()))
            """,
            ("4", "None", "A coroutine object"),
            0,
            "asyncio.run executes the coroutine and returns its result.",
        ),
        task(
            "Repair a missing await",
            "double(fetch) is async. fetch is an async no-argument "
            "callable. Await its result and return twice that number.",
            """
                async def double(fetch):
                    return 2 * await fetch()
            """,
            [
                (
                    "Awaited result",
                    "(exec('import asyncio\\nasync def fetch():\\n    "
                    "return 3', globals()), asyncio.run(double(fetch)))[1]",
                    6,
                )
            ],
            broken="""
                async def double(fetch):
                    return 2 * fetch()
            """,
            hint="Calling an async function creates a coroutine; await obtains its value.",
        ),
        task(
            "Gather in input order",
            "async collect(fetchers) calls each no-argument async "
            "callable and returns their results in input order using "
            "asyncio.gather. Empty input returns [].",
            """
                import asyncio


                async def collect(fetchers):
                    return list(await asyncio.gather(*(fetch() for fetch in fetchers)))
            """,
            [
                (
                    "Ordered results",
                    "(exec('import asyncio\\nasync def a():\\n    await "
                    "asyncio.sleep(0.01)\\n    return 1\\nasync def "
                    "b():\\n    return 2', globals()), "
                    "asyncio.run(collect([a, b])))[1]",
                    [1, 2],
                ),
                ("Empty", '__import__("asyncio").run(collect([]))', []),
            ],
            hint="gather preserves argument order even if completion order differs.",
        ),
    ),
    "distributable-tools": chapter(
        "distributable-tools",
        prediction(
            "Explicit arguments",
            """
                import argparse

                p = argparse.ArgumentParser()
                p.add_argument("--count", type=int, default=2)
                print(p.parse_args([]).count)
            """,
            ("2", "None", '"2"'),
            0,
            "An empty argument list selects the integer default.",
        ),
        task(
            "Repair a command default",
            "parse_args(argv) uses argparse and returns a Namespace "
            "with count. --count is an integer with default 2. Parse "
            "argv, not the process command line.",
            """
                import argparse


                def parse_args(argv):
                    parser = argparse.ArgumentParser()
                    parser.add_argument("--count", type=int, default=2)
                    return parser.parse_args(argv)
            """,
            [
                ("Default", "parse_args([]).count", 2),
                ("Explicit value", 'parse_args(["--count", "4"]).count', 4),
            ],
            broken="""
                import argparse


                def parse_args(argv):
                    parser = argparse.ArgumentParser()
                    parser.add_argument("--count", default=2)
                    return parser.parse_args(argv)
            """,
            hint="Command-line strings need an explicit conversion.",
        ),
        task(
            "Write a testable entry function",
            "main(argv) parses optional --name (default traveler), "
            "prints exactly Hello, NAME! and returns 0. Do not call "
            "main at import time.",
            """
                import argparse


                def main(argv):
                    parser = argparse.ArgumentParser()
                    parser.add_argument("--name", default="traveler")
                    args = parser.parse_args(argv)
                    print(f"Hello, {args.name}!")
                    return 0
            """,
            [
                (
                    "Default greeting",
                    "(exec('import io\\nfrom contextlib import "
                    "redirect_stdout\\ns = io.StringIO()\\nwith "
                    "redirect_stdout(s):\\n    result = main([])', "
                    "globals()), [result, s.getvalue()])[1]",
                    [0, "Hello, traveler!\n"],
                ),
                (
                    "Named greeting",
                    '(exec("import io\\nfrom contextlib import '
                    "redirect_stdout\\ns = io.StringIO()\\nwith "
                    "redirect_stdout(s):\\n    result = main(['--name', "
                    "'Ari'])\", globals()), [result, s.getvalue()])[1]",
                    [0, "Hello, Ari!\n"],
                ),
            ],
            hint="Accept the argument list explicitly so callers can test the entry function.",
        ),
    ),
    "python-machinery": chapter(
        "python-machinery",
        prediction(
            "Attribute fallback",
            """
                class Record:
                    def __getattr__(self, name):
                        return "missing"


                r = Record()
                r.name = "A"
                print(r.name, r.other)
            """,
            ("missing missing", "A missing", "A other"),
            1,
            "__getattr__ runs only after normal lookup fails.",
        ),
        task(
            "Repair a descriptor lookup",
            "Label is a descriptor. Label.__get__(instance, "
            "owner=None) returns itself on class access and "
            "instance._label.upper() on instance access.",
            """
                class Label:
                    def __get__(self, instance, owner=None):
                        if instance is None:
                            return self
                        return instance._label.upper()
            """,
            [
                (
                    "Instance lookup",
                    '(exec("class Item:\\n    label = Label()\\n    '
                    "_label = 'map'\", globals()), Item().label)[1]",
                    "MAP",
                ),
                (
                    "Class lookup",
                    "(exec('class Item:\\n    label = Label()', "
                    "globals()), isinstance(Item.label, Label))[1]",
                    True,
                ),
            ],
            broken="""
                class Label:
                    def __get__(self, instance, owner=None):
                        return instance._label.upper()
            """,
            hint="Class access supplies None as the instance.",
        ),
        task(
            "Implement a narrow fallback",
            "Record(data) copies a dictionary. Missing normal "
            "attributes are looked up in data; absent keys must raise "
            "AttributeError, so hasattr works correctly.",
            """
                class Record:
                    def __init__(self, data):
                        self.data = dict(data)

                    def __getattr__(self, name):
                        try:
                            return self.data[name]
                        except KeyError:
                            raise AttributeError(name) from None
            """,
            [
                ("Stored field", 'Record({"name": "A"}).name', "A"),
                ("Absent field", 'hasattr(Record({}), "missing")', False),
            ],
            hint="Translate a missing dictionary key into the exception attribute lookup expects.",
        ),
    ),
}
