"""Original exercises retained for profile continuity."""

from pytuitor_web.models import Check, Lesson, code, lesson_text

LESSONS = (
    Lesson(
        "first-light",
        "beginner",
        "Your first program",
        "Strings, integers, and output",
        8,
        ("Values & output",),
        lesson_text("first-light"),
        'print("Hello, explorer!")\nprint("6 * 7")\n',
        (
            Check(
                "Two lines of output",
                "__stdout__.strip().splitlines()",
                ["Hello, explorer!", "42"],
                "Check the greeting exactly, then multiply 6 by 7.",
                expected_output="Hello, explorer!\n42",
                description="Run the program and compare its two printed lines.",
            ),
        ),
        ("Put the greeting inside quotes.", "Use print(6 * 7) for the second line."),
        'What does print("2" + "3") display?',
        ("5", "23", "An error"),
        1,
        "Both values are strings. Adding strings joins their text; adding numbers does arithmetic.",
        'print("Hello, explorer!")\nprint(6 * 7)\n',
    ),
    Lesson(
        "names-and-voices",
        "beginner",
        "Variables and input",
        "Store values and ask the user a question",
        10,
        ("Variables & strings",),
        lesson_text("names-and-voices"),
        (
            'student = input("What is your name? ")\n'
            'greeting = "Welcome, {student}!"\n'
            "print(greeting)\n"
        ),
        tuple(
            Check(
                f"Greeting for {student}",
                "greeting",
                f"Welcome, {student}!",
                "Use the student variable in an f-string, then print greeting.",
                stdin=student + "\n",
                expected_output=f"Welcome, {student}!",
            )
            for student in ("Ada", "Lin", "Alex Chen")
        ),
        (
            "First store the answer from input() in student.",
            'Write greeting = f"Welcome, {student}!", then print(greeting).',
        ),
        'student = "Ada"; student = "Lin". What does print(student) display?',
        ("Ada", "Lin", "AdaLin"),
        1,
        "student first holds Ada, then Lin. The second assignment changes the variable's value.",
        (
            'student = input("What is your name? ")\n'
            'greeting = f"Welcome, {student}!"\n'
            "print(greeting)\n"
        ),
        revision=3,
    ),
    Lesson(
        "choose-a-door",
        "beginner",
        "Making decisions",
        "Comparisons, booleans, if, elif, and else",
        12,
        ("Conditions",),
        lesson_text("choose-a-door"),
        (
            'key = input("Which key? ")\n'
            'if key == "gold":\n'
            '    destination = "treasure"\n'
            'if key == "green":\n'
            '    destination = "garden"\n'
            "else:\n"
            '    destination = "locked"\n'
            "print(destination)\n"
        ),
        tuple(
            Check(
                f"Key: {key}",
                "destination",
                destination,
                "Compare key using == and assign destination in each branch.",
                stdin=key + "\n",
                expected_output=destination,
            )
            for key, destination in (("gold", "treasure"), ("green", "garden"), ("blue", "locked"))
        ),
        (
            'Start with if key == "gold": and indent destination = "treasure" beneath it.',
            'Use elif key == "green": for the second case, then else: for all other keys.',
        ),
        "Which comparison is true?",
        ("3 > 3", "3 >= 3", '3 == "3"'),
        1,
        ">= includes equality. The string '3' and the number 3 are different values.",
        (
            'key = input("Which key? ")\n'
            'if key == "gold":\n'
            '    destination = "treasure"\n'
            'elif key == "green":\n'
            '    destination = "garden"\n'
            "else:\n"
            '    destination = "locked"\n'
            "print(destination)\n"
        ),
        revision=3,
    ),
    Lesson(
        "pack-your-bag",
        "beginner",
        "Lists and loops",
        "Work through a collection and calculate a total",
        12,
        ("Loops & collections",),
        lesson_text("pack-your-bag"),
        (
            "pouches = []\n"
            'for amount in input("Coins in each pouch: ").split():\n'
            "    pouches.append(int(amount))\n"
            "total = 0\n"
            "for coins in pouches:\n"
            "    total = 0\n"
            "    total = total + coins\n"
            "print(total)\n"
        ),
        tuple(
            Check(
                f"Pouches: {amounts or 'empty'}",
                "total",
                expected,
                "Start total at zero before the loop, add each pouch, then print after the loop.",
                stdin=amounts + "\n",
                expected_output=str(expected),
            )
            for amounts, expected in (("2 5 1", 8), ("", 0), ("7", 7))
        ),
        (
            "After total = 0, add for coins in pouches: on a new line.",
            "Indent total = total + coins under that loop. Keep print(total) outside the loop.",
        ),
        "How many times does for item in [] run its body?",
        ("Zero", "Once", "Forever"),
        0,
        "An empty collection has no values to visit, so the loop body never runs.",
        (
            "pouches = []\n"
            'for amount in input("Coins in each pouch: ").split():\n'
            "    pouches.append(int(amount))\n"
            "\n"
            "total = 0\n"
            "for coins in pouches:\n"
            "    total = total + coins\n"
            "print(total)\n"
        ),
        revision=3,
    ),
    Lesson(
        "small-superpowers",
        "beginner",
        "Writing functions",
        "Parameters, return values, and debugging",
        12,
        ("Functions & debugging",),
        lesson_text("small-superpowers"),
        (
            "def heal(health, potion):\n"
            "    new_health = health + potion\n"
            "    if new_health > 100:\n"
            "        return 100\n"
            "    print(new_health)\n"
            "\n"
            "print(heal(90, 25))\n"
        ),
        tuple(
            Check(
                f"heal({health}, {potion})",
                f"heal({health}, {potion})",
                value,
                "Return the result, and make sure it cannot exceed 100.",
            )
            for health, potion, value in [(20, 10, 30), (90, 25, 100), (100, 0, 100)]
        ),
        (
            "Replace print inside the function with a returned value.",
            (
                "Calculate new_health = health + potion. If new_health > 100, "
                "return 100; otherwise return new_health."
            ),
        ),
        "A function reaches its end without return. What does it return?",
        ("0", "None", "An error"),
        1,
        (
            "Python returns None automatically. That often explains a failing "
            "check after a print statement."
        ),
        (
            "def heal(health, potion):\n"
            "    new_health = health + potion\n"
            "    if new_health > 100:\n"
            "        return 100\n"
            "    return new_health\n"
            "\n"
            "print(heal(90, 25))\n"
        ),
    ),
    Lesson(
        "objects-not-boxes",
        "experienced",
        "Objects and copying",
        "Identity, aliasing, and mutability",
        12,
        ("Identity & mutability",),
        lesson_text("objects-not-boxes"),
        (
            "from copy import deepcopy\n"
            "\n"
            "def add_tag(record, tag):\n"
            "    result = record.copy()\n"
            '    result["tags"].append(tag)\n'
            "    return result\n"
        ),
        (
            Check(
                "New tag and preserved fields",
                "add_tag({'name': 'Ada', 'tags': ['py']}, 'cli')",
                {"name": "Ada", "tags": ["py", "cli"]},
                "Preserve all fields and append the new tag.",
            ),
            Check(
                "Original remains unchanged",
                "(lambda r: (add_tag(r, 'new'), r)[1])({'tags': ['old']})",
                {"tags": ["old"]},
                "A shallow copy still shares the nested list.",
                description=(
                    "Call add_tag with {'tags': ['old']} and 'new'; inspect the original record."
                ),
            ),
            Check(
                "Independent nested metadata",
                "(lambda r: add_tag(r, 'x')['meta'] is r['meta'])({'tags': [], 'meta': {}})",
                False,
                "The returned record must be an independent deep copy.",
                description=(
                    "Call add_tag with {'tags': [], 'meta': {}} and 'x'; check "
                    "whether metadata is still shared (expected False)."
                ),
            ),
        ),
        (
            "The outer dictionary is copied, but the tags list is shared.",
            "Import deepcopy from copy and use it instead of record.copy().",
        ),
        "a = [1]; b = a; b += [2]. What is a?",
        ("[1]", "[1, 2]", "An error"),
        1,
        "For a list, += mutates in place. Both names still refer to the same list.",
        (
            "from copy import deepcopy\n"
            "\n"
            "def add_tag(record, tag):\n"
            "    result = deepcopy(record)\n"
            '    result["tags"].append(tag)\n'
            "    return result\n"
        ),
    ),
    Lesson(
        "functions-with-memory",
        "experienced",
        "Arguments and decorators",
        "Scope, defaults, and decorators",
        15,
        ("Scope & arguments", "Decorators"),
        lesson_text("functions-with-memory"),
        (
            "from functools import wraps\n"
            "\n"
            "def collect(item, bucket=[]):\n"
            "    if bucket is None:\n"
            "        bucket = []\n"
            "    bucket.append(item)\n"
            "    return bucket\n"
            "\n"
            "def twice(fn):\n"
            "    @wraps(fn)\n"
            "    def wrapper(*args, **kwargs):\n"
            "        return fn(*args, **kwargs) * 2\n"
            "    return wrapper\n"
        ),
        (
            Check(
                "Independent default buckets",
                "[collect(1), collect(2)]",
                [[1], [2]],
                "Replace the list default with None and create the list per call.",
            ),
            Check(
                "Explicit bucket",
                "(lambda b: collect(3, b) is b)([])",
                True,
                "Only create a bucket when the argument is None, not when it is empty.",
                description=(
                    "Call collect(3, bucket) with an empty list; verify the returned "
                    "object is that same list."
                ),
            ),
            Check(
                "Keyword arguments",
                "twice(lambda x, y=1: x + y)(3, y=4)",
                14,
                "Forward *args and **kwargs, then multiply the return value by 2.",
            ),
            Check(
                "One call only",
                "(lambda seen: (twice(lambda: seen.append(1) or 5)(), len(seen)))([])",
                [10, 1],
                "Call fn once; double its result rather than calling it twice.",
                description=(
                    "Wrap a function that records each call and returns 5. Expect "
                    "result 10 and exactly 1 call."
                ),
            ),
            Check("Preserve metadata", "twice(collect).__name__", "collect", "Use @wraps(fn)."),
        ),
        (
            "Use if bucket is None, not if not bucket, to preserve a supplied empty list.",
            (
                "Define wrapper(*args, **kwargs) inside twice, decorate with "
                "@wraps(fn), and return it."
            ),
        ),
        "When is a default argument expression evaluated?",
        ("At every call", "When def executes", "On first use"),
        1,
        (
            "The default object belongs to the function object and is reused "
            "for calls that omit that argument."
        ),
        code("""
        from functools import wraps

        def collect(item, bucket=None):
            if bucket is None:
                bucket = []
            bucket.append(item)
            return bucket

        def twice(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                return fn(*args, **kwargs) * 2
            return wrapper
        """),
    ),
    Lesson(
        "lazy-by-design",
        "experienced",
        "Iterators and generators",
        "Comprehensions and generator protocols",
        12,
        ("Iteration & generators",),
        lesson_text("lazy-by-design"),
        (
            "def positive_squares(numbers):\n"
            "    for n in numbers:\n"
            "        if n > 0:\n"
            "            return n * n\n"
        ),
        (
            Check(
                "Filter and transform",
                "list(positive_squares([-2, 0, 3, 2]))",
                [9, 4],
                "Yield n * n only when n > 0.",
            ),
            Check(
                "Return an iterator",
                "(lambda result: iter(result) is result)(positive_squares([2]))",
                True,
                "Use yield rather than returning a list.",
                description="Call positive_squares([2]); check that iter(result) is result.",
            ),
            Check(
                "Consume a generator",
                "list(positive_squares(n for n in [1, -1, 4]))",
                [1, 16],
                "Loop over the iterable directly.",
            ),
            Check(
                "Infinite stream stays lazy",
                (
                    "list(__import__('itertools').islice(positive_squares(__import__('"
                    "itertools').count(1)), 3))"
                ),
                [1, 4, 9],
                "Yield each result as requested; do not exhaust the input first.",
                description=(
                    "Supply the infinite sequence 1, 2, 3, ... and request only the "
                    "first three squares."
                ),
            ),
        ),
        (
            "Loop directly over numbers and filter using an if statement.",
            "Use yield n * n inside the positive branch.",
        ),
        "g = (n for n in [1, 2]); list(g); list(g). What is the second list?",
        ("[1, 2]", "[]", "An error"),
        1,
        "The first conversion exhausts the generator. Iterating again produces no values.",
        (
            "def positive_squares(numbers):\n"
            "    for n in numbers:\n"
            "        if n > 0:\n"
            "            yield n * n\n"
        ),
    ),
    Lesson(
        "clean-exits",
        "experienced",
        "Context managers and async",
        "Resources, exceptions, and async",
        15,
        ("Context managers", "Async fundamentals"),
        lesson_text("clean-exits"),
        (
            "import asyncio\n"
            "from contextlib import contextmanager\n"
            "\n"
            "@contextmanager\n"
            "def session(events):\n"
            '    events.append("open")\n'
            "    yield events\n"
            '    events.append("close")\n'
            "\n"
            "async def double(value):\n"
            "    await asyncio.sleep(0)\n"
            "    return value * 2\n"
            "\n"
            "async def double_all(values):\n"
            "    return await asyncio.gather(*(double(value) for value in "
            "values))\n"
        ),
        (
            Check(
                "Normal cleanup",
                "__session_check__(session, False)",
                ["open", "close"],
                "Place cleanup after yield in a finally block.",
                description="Enter and exit with session(events), starting with events = [].",
            ),
            Check(
                "Cleanup after an exception",
                "__session_check__(session, True)",
                ["open", "close"],
                "A finally block runs even when the with body raises.",
                description=(
                    "Raise ValueError inside with session(events), starting with events = []."
                ),
            ),
            Check(
                "Async results",
                "asyncio.run(double_all([3, 1, 2]))",
                [6, 2, 4],
                "Await asyncio.gather over double(value) for each value.",
            ),
            Check(
                "Empty input", "asyncio.run(double_all([]))", [], "gather can handle no awaitables."
            ),
            Check(
                "Schedule concurrently",
                "__concurrency_check__(double_all)",
                True,
                "Await gather once; do not await each operation sequentially.",
                description=(
                    "Supply [1, 2, 3] and verify all three double operations start "
                    "before any finishes."
                ),
            ),
        ),
        (
            "Put yield events inside try and append close inside finally.",
            "return await asyncio.gather(*(double(value) for value in values))",
        ),
        "Calling an async def function without awaiting it returns...",
        ("Its final value", "A coroutine", "A new thread"),
        1,
        "Calling creates a coroutine object. Scheduling or awaiting it is what executes its body.",
        code("""
        import asyncio
        from contextlib import contextmanager

        @contextmanager
        def session(events):
            events.append("open")
            try:
                yield events
            finally:
                events.append("close")

        async def double(value):
            await asyncio.sleep(0)
            return value * 2

        async def double_all(values):
            return await asyncio.gather(*(double(value) for value in values))
        """),
    ),
    Lesson(
        "ready-to-ship",
        "experienced",
        "Types and tests",
        "Types, tests, and project boundaries",
        15,
        ("Typing & testing",),
        lesson_text("ready-to-ship"),
        (
            "def parse_count(text: str) -> int:\n"
            "    count = int(text)\n"
            "    if count <= 0:\n"
            '        raise ValueError("Count must be nonnegative")\n'
            "    return count\n"
            "\n"
            "def test_parse_count():\n"
            '    assert parse_count("0") == 0\n'
            '    assert parse_count(" 12 ") == 12\n'
            '    for invalid in ("-1", "2.5"):\n'
            "        try:\n"
            "            parse_count(invalid)\n"
            "        except ValueError:\n"
            "            pass\n"
            "        else:\n"
            '            raise AssertionError("Invalid count accepted")\n'
        ),
        (
            Check("Whitespace", "parse_count(' 12 ')", 12, "int(text) already accepts whitespace."),
            Check("Zero", "parse_count('0')", 0, "Zero is a valid nonnegative count."),
            Check(
                "Reject negative",
                "__raises_value_error__(parse_count, '-2')",
                True,
                "Raise ValueError when the parsed result is negative.",
                description="Call parse_count('-2'); expect ValueError (True means it was raised).",
            ),
            Check(
                "Reject non-integer",
                "__raises_value_error__(parse_count, '2.5')",
                True,
                "Do not round or coerce floats; use int on the string.",
                description=(
                    "Call parse_count('2.5'); expect ValueError (True means it was raised)."
                ),
            ),
            Check("Your regression test", "test_parse_count()", None, "Your assertions must pass."),
            Check(
                "Your test catches broken implementations",
                "__mutation_check__(test_parse_count)",
                True,
                "Test 0, whitespace, and invalid input with assertions and an exception check.",
                description=(
                    "Run your tests against three broken parsers: always 0, always "
                    "12, and accepting negatives. True means your tests reject all "
                    "three."
                ),
            ),
        ),
        (
            "Convert with int, reject a result below zero, then return it.",
            (
                "In your test: assert parse_count(' 12 ') == 12. For '-1', catch "
                "ValueError; else raise AssertionError."
            ),
        ),
        "Does a str annotation prevent passing an integer at runtime?",
        ("Yes", "No", "Only inside a function"),
        1,
        (
            "Annotations describe expected types. A type checker can flag mismatches, but "
            "runtime validation is still your responsibility."
        ),
        code("""
        def parse_count(text: str) -> int:
            count = int(text)
            if count < 0:
                raise ValueError("Count must be nonnegative")
            return count

        def test_parse_count():
            assert parse_count("0") == 0
            assert parse_count(" 12 ") == 12
            for invalid in ("-1", "2.5"):
                try:
                    parse_count(invalid)
                except ValueError:
                    pass
                else:
                    raise AssertionError("Invalid count accepted")
        """),
    ),
)

BY_ID = {lesson.id: lesson for lesson in LESSONS}
CONCEPTS = tuple(dict.fromkeys(c for lesson in LESSONS for c in lesson.concepts))
TRACKS = {
    "beginner": "Beginner",
    "experienced": "Experienced",
    "custom": "Custom",
}


def track_lessons(track: str) -> list[Lesson]:
    return [lesson for lesson in LESSONS if track == "custom" or lesson.track == track]


def default_input(lesson: Lesson) -> str:
    return {
        "names-and-voices": "Ada\n",
        "choose-a-door": "gold\n",
        "pack-your-bag": "2 5 1\n",
    }.get(lesson.id, "")
