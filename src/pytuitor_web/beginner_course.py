"""The beginner course: small programs and dependable tools."""

from dataclasses import replace

from pytuitor_web.beginner_extensions import INSERT_AFTER
from pytuitor_web.beginner_extensions import LESSONS as EXTRA_LESSONS
from pytuitor_web.beginner_stage_refresh import BUILD_INSTRUCTIONS, REPAIR_STAGES
from pytuitor_web.checkpoints import apply_checkpoints
from pytuitor_web.legacy import LESSONS as LEGACY
from pytuitor_web.models import (
    Chapter,
    Check,
    Lesson,
    StageContract,
    code,
    lesson_text,
)

CHAPTERS = (
    Chapter(
        "b-foundations",
        "beginner",
        "First programs",
        "Read input, calculate, and choose what happens.",
    ),
    Chapter(
        "b-collections",
        "beginner",
        "Working with collections",
        "Process ordered items, unique values, and dictionaries.",
    ),
    Chapter(
        "b-functions",
        "beginner",
        "Reusable programs",
        "Organize behavior into functions and handle invalid input.",
    ),
    Chapter(
        "b-data",
        "beginner",
        "Files and structured data",
        "Read, transform, and save text, JSON, and CSV.",
    ),
    Chapter(
        "b-tools",
        "beginner",
        "Tools you can maintain",
        "Build modules, command-line interfaces, classes, and tests.",
    ),
    Chapter(
        "b-automation",
        "beginner",
        "Dependable automation",
        "Combine data, dates, validation, and safe file operations.",
    ),
)


def exercise(
    identifier,
    title,
    subtitle,
    chapter,
    solution,
    repair,
    checks,
    hints,
    *,
    files=None,
    entrypoint="lesson.py",
    stdin="",
):
    return Lesson(
        identifier,
        "beginner",
        title,
        subtitle,
        15,
        (title,),
        lesson_text(identifier),
        repair,
        checks,
        hints,
        "",
        (),
        0,
        "",
        solution,
        revision=4,
        chapter_id=chapter,
        files=tuple(files[0]) if files else ("lesson.py",),
        entrypoint=entrypoint,
        solution_files=files[0] if files else None,
        repair_files=files[1] if files and len(files) > 1 else None,
        stdin=stdin,
    )


def case(
    label,
    expression,
    expected,
    *,
    stdin=None,
    output=None,
    nudge="Compare the actual and expected results for this input.",
):
    return Check(label, expression, expected, nudge, stdin=stdin, expected_output=output)


def stage_contract(instructions, reference, starter, checks, hints, stdin=""):
    return StageContract(
        instructions=instructions,
        checks=tuple(checks),
        hints=tuple(hints),
        stdin=stdin,
        starter_files={"lesson.py": code(starter) if starter else ""},
        reference_files={"lesson.py": code(reference)},
    )


_units = []


def add(*args, **kwargs):
    _units.append(exercise(*args, **kwargs))


def reuse(identifier, chapter, *, stdin=""):
    old = next(lesson for lesson in LEGACY if lesson.id == identifier)
    _units.append(replace(old, revision=4, chapter_id=chapter, stdin=stdin))


reuse("pack-your-bag", "b-collections", stdin="2 5 1\n")

add(
    "list-positions",
    "Finding items in a list",
    "Indexes, length, and empty collections",
    "b-collections",
    (
        code("""
            items = input("Items: ").split()
            if len(items) == 0:
                first = "empty"
                last = "empty"
            else:
                first = items[0]
                last = items[-1]
            print(first)
            print(last)
        """)
    ),
    (""),
    tuple(
        case(
            f"Words: {text or 'empty'}",
            "[first, last]",
            expected,
            stdin=text + "\n",
            output="\n".join(expected),
        )
        for text, expected in (
            ("sun moon star", ["sun", "star"]),
            ("solo", ["solo", "solo"]),
            ("", ["empty", "empty"]),
        )
    ),
    ("Check len(items) before indexing.", "The first index is 0; -1 asks for the last item."),
)

add(
    "tuples-and-sets",
    "Tuples, sets, and unpacking",
    "Group a fixed pair and recognize unique items",
    "b-collections",
    code("""
        pair = tuple(input("Two names: ").split())
        first, second = pair
        seen = set(input("Visitors: ").split())
        print(first in seen)
        print(second in seen)
        print(len(seen))
    """),
    "",
    tuple(
        case(
            label,
            (
                "[list(pair), isinstance(pair, tuple), first, second, "
                "sorted(seen), isinstance(seen, set)]"
            ),
            [names.split(), True, *names.split(), sorted(set(visitors.split())), True],
            stdin=names + "\n" + visitors + "\n",
            output=output,
        )
        for label, names, visitors, output in (
            ("Repeated visitors", "Ada Lin", "Ada Ada Bo", "True\nFalse\n2"),
            ("Second name only", "Ada Lin", "Lin", "False\nTrue\n1"),
            ("No visitors", "Ada Lin", "", "False\nFalse\n0"),
            ("Case matters", "Ada ada", "ada Bo", "False\nTrue\n2"),
            ("Both names present", "Ada Lin", "Lin Ada", "True\nTrue\n2"),
        )
    ),
    (
        "Convert the first split input with tuple(), then unpack in the original order.",
        "Use set() for the visitors, in for membership, and len() for the distinct count.",
    ),
    stdin="Ada Lin\nAda Ada Bo\n",
)

add(
    "loop-helpers",
    "Numbering and pairing items",
    "Use range, enumerate, and zip to organize loops",
    "b-collections",
    code("""
        count = int(input("Number of slots: "))
        names = input("Names: ").split()
        colors = input("Colors: ").split()
        slots = []
        for number in range(1, count + 1):
            slots.append(number)
        numbered = []
        for number, name in enumerate(names, start=1):
            numbered.append((number, name))
        pairs = []
        for name, color in zip(names, colors):
            pairs.append((name, color))
        print(slots)
        print(numbered)
        print(pairs)
    """),
    "",
    tuple(
        case(
            label,
            "[slots, numbered, pairs, all(isinstance(item, tuple) for item in numbered + pairs)]",
            [
                list(range(1, count + 1)),
                list(enumerate(names.split(), 1)),
                list(zip(names.split(), colors.split(), strict=False)),
                True,
            ],
            stdin=f"{count}\n{names}\n{colors}\n",
        )
        for label, count, names, colors in (
            ("Matching lists", 3, "Ada Lin", "blue gold"),
            ("Preserve repeated entries", 2, "Ada Ada Bo", "blue gold blue"),
            ("More names than colors", 1, "Ada Lin Bo", "blue"),
            ("More colors than names", 2, "Ada", "blue gold green"),
            ("Empty lists and zero slots", 0, "", ""),
            ("Empty names", 0, "", "blue"),
            ("Empty colors", 2, "Ada", ""),
        )
    ),
    (
        "range stops before its end; range(1, count + 1) includes count.",
        "Use enumerate(names, start=1) for numbering and zip(names, colors) for matched pairs.",
        "Start each result as [] and append a tuple such as (number, name) inside its loop.",
    ),
    stdin="3\nAda Lin\nblue gold\n",
)

add(
    "word-counts",
    "Dictionaries and counts",
    "Associate keys with values",
    "b-collections",
    (
        code("""
            counts = {}
            for word in input("Words: ").split():
                counts[word] = counts.get(word, 0) + 1
            print(counts)
        """)
    ),
    "",
    tuple(
        case(f"Count {words!r}", "counts", result, stdin=words + "\n")
        for words, result in (
            ("bee ant bee", {"bee": 2, "ant": 1}),
            ("", {}),
            ("Cat cat Cat", {"Cat": 2, "cat": 1}),
        )
    ),
    (
        "Begin with an empty dictionary outside the loop.",
        "Assign counts[word] = counts.get(word, 0) + 1 on each visit.",
    ),
)

add(
    "repeat-until-done",
    "Repeating until done",
    "While loops and stopping conditions",
    "b-collections",
    (
        code("""
            total = 0
            while True:
                number = int(input("Number (0 to finish): "))
                if number == 0:
                    break
                total = total + number
            print(total)
        """)
    ),
    (""),
    tuple(
        case(label, "total", result, stdin=text, output=str(result))
        for label, text, result in (
            (
                "Several entries",
                code("""
                5
                -2
                0
            """),
                3,
            ),
            ("Stop immediately", "0\n", 0),
            (
                "Negative total",
                code("""
                -8
                2
                0
            """),
                -6,
            ),
        )
    ),
    (
        "Put total = 0 before the loop, not inside it.",
        "Read number, break if number == 0, otherwise add it to total.",
    ),
    stdin=code("""
        5
        -2
        0
    """),
)

reuse("small-superpowers", "b-functions")

add(
    "clean-labels",
    "Cleaning strings",
    "Methods, whitespace, and reusable transformations",
    "b-functions",
    code("""
        def slug(text):
            return "-".join(text.lower().split())
    """),
    "",
    tuple(
        case(f"slug({text!r})", f"slug({text!r})", result)
        for text, result in (("  Blue   Moon ", "blue-moon"), ("", ""), ("A\tB!", "a-b!"))
    ),
    (
        "lower() returns a new string, so use that result.",
        'Split without an argument, then join the words using "-".',
    ),
)

add(
    "function-options",
    "Function options",
    "Default arguments, keyword calls, and local variables",
    "b-functions",
    (
        code("""
            def subtotal(prices, discount=0):
                total = 0
                for price in prices:
                    total = total + price
                total = total - discount
                if total < 0:
                    return 0
                return total
        """)
    ),
    (""),
    (
        case("Default discount", "subtotal([6, 4])", 10),
        case("One order discount", "subtotal([6, 4], discount=3)", 7),
        case("Discount exceeds total", "subtotal([2], discount=9)", 0),
        case("Empty basket", "subtotal([])", 0),
    ),
    (
        "Add every price first, then subtract discount after the loop.",
        "If the resulting total is below zero, return zero; otherwise return total.",
    ),
)

add(
    "recursion-basics",
    "Recursion and base cases",
    "Solve a smaller version of the same problem",
    "b-functions",
    code(
        """
        def digit_sum(number):
            if number < 10:
                return number
            return number % 10 + digit_sum(number // 10)
        """
    ),
    "",
    (
        case("Digits of 0", "digit_sum(0)", 0),
        case("Digits of 7", "digit_sum(7)", 7),
        case("Digits of 10", "digit_sum(10)", 1),
        case("Digits of 204", "digit_sum(204)", 6),
        case("Digits of 9999", "digit_sum(9999)", 36),
        case("Digits of 100000", "digit_sum(100000)", 1),
    ),
    (
        "Return the last remaining digit in the base case.",
        "number // 10 removes the last digit; number % 10 reads it.",
    ),
)

add(
    "recursive-collections",
    "Nested lists with recursion",
    "Traverse collections at different depths",
    "b-functions",
    code(
        """
        def sum_nested(items):
            total = 0
            for item in items:
                if isinstance(item, list):
                    total += sum_nested(item)
                else:
                    total += item
            return total
        """
    ),
    "",
    (
        case("Nested total 1", "sum_nested([])", 0),
        case("Nested total 2", "sum_nested([3, -2])", 1),
        case("Nested total 3", "sum_nested([1, [2, [3]], 4])", 10),
        case("Nested total 4", "sum_nested([[[], []]])", 0),
        case("Nested total 5", "sum_nested([[-8], [2, [0, 5]]])", -1),
        case(
            "Input stays unchanged",
            "(lambda items: (sum_nested(items), items))([1, [2, [3]]])",
            (6, [1, [2, [3]]]),
        ),
    ),
    (
        "isinstance(item, list) distinguishes nested lists from integers.",
        "The empty list naturally totals zero; add a recursive subtotal for each inner list.",
    ),
)

add(
    "handle-invalid-input",
    "Handling invalid input",
    "Exceptions and deliberate recovery",
    "b-functions",
    (
        code("""
            def parse_quantity(text):
                try:
                    number = int(text)
                except ValueError:
                    return None
                if number < 0:
                    return None
                return number
        """)
    ),
    "",
    tuple(
        case(f"Parse {text!r}", f"parse_quantity({text!r})", result)
        for text, result in (
            (" +12 ", 12),
            ("0", 0),
            ("-1", None),
            ("oops", None),
            ("3.5", None),
            ("", None),
        )
    ),
    (
        "Catch ValueError around the int() conversion.",
        "After successful conversion, reject numbers smaller than zero.",
    ),
)

add(
    "text-files",
    "Reading and writing files",
    "Open files and close them reliably",
    "b-data",
    (
        code("""
            def line_total(path):
                with open(path, "r", encoding="utf-8") as handle:
                    lines = handle.read().splitlines()
                total = 0
                for line in lines:
                    if line.strip() != "":
                        total = total + int(line)
                return total
        """)
    ),
    (""),
    tuple(
        case(
            label,
            (
                f"(__import__('pathlib').Path('numbers.txt').write_text({text!r}, "
                "encoding='utf-8'), line_total('numbers.txt'))[1]"
            ),
            result,
        )
        for label, text, result in (
            (
                "Blank lines and negatives",
                "4\n \t \n-1\n",
                3,
            ),
            ("Empty file", "", 0),
            ("Single number", "7", 7),
        )
    ),
    (
        "Use a with block to read the file, then loop over splitlines().",
        "Only call int(line) when line.strip() is not empty.",
    ),
)

add(
    "paths-and-folders",
    "Paths and folders",
    "Build file paths without joining strings by hand",
    "b-data",
    (
        code("""
            from pathlib import Path

            def save_note(folder, text):
                directory = Path(folder)
                directory.mkdir(parents=True, exist_ok=True)
                target = directory / "note.txt"
                target.write_text(text, encoding="utf-8")
                return target
        """)
    ),
    (""),
    (
        case(
            "Create nested folder",
            (
                "(lambda p: [p.as_posix(), p.read_text(encoding='utf-8')])(save_no"
                "te('notes/deep', 'café'))"
            ),
            ["notes/deep/note.txt", "café"],
        ),
        case(
            "Replace deliberately",
            "(save_note('notes', 'old'), save_note('notes', 'new').read_text(encoding='utf-8'))[1]",
            "new",
        ),
    ),
    (
        "Create Path(folder), then call mkdir with parents=True and exist_ok=True.",
        "Join the directory and filename with / before calling write_text.",
    ),
)

add(
    "json-records",
    "Saving structured data",
    "JSON, dictionaries, and lists on disk",
    "b-data",
    (
        code("""
            import json

            def save_scores(path, scores):
                with open(path, "w", encoding="utf-8") as handle:
                    json.dump(scores, handle)
                total = 0
                for score in scores.values():
                    total = total + score
                return total
        """)
    ),
    (""),
    tuple(
        case(
            label,
            (
                "(lambda total: [total, __import__('json').loads("
                "__import__('pathlib').Path('scores.json').read_text(encoding='utf-8'))])"
                f"(save_scores('scores.json', {scores!r}))"
            ),
            [total, scores],
        )
        for label, scores, total in (
            ("Unicode names", {"Zoë": 4, "Lin": 7}, 11),
            ("Empty scores", {}, 0),
        )
    ),
    (
        "Use json.dump inside a writing with block.",
        "Loop over scores.values() to compute the returned total separately from saving.",
    ),
)

add(
    "csv-tables",
    "Working with CSV tables",
    "Read headers and quoted fields correctly",
    "b-data",
    (
        code("""
            import csv

            def csv_total(path):
                total = 0
                with open(path, newline="", encoding="utf-8") as handle:
                    for row in csv.DictReader(handle):
                        total = total + int(row["quantity"]) * int(row["price"])
                return total
        """)
    ),
    (""),
    tuple(
        case(
            label,
            (
                f"(__import__('pathlib').Path('table.csv').write_text({text!r}, "
                "encoding='utf-8'), csv_total('table.csv'))[1]"
            ),
            result,
        )
        for label, text, result in (
            (
                "Quoted comma",
                code("""
                item,quantity,price
                "pen, blue",2,3
                book,1,8
            """),
                14,
            ),
            ("Header only", "item,quantity,price\n", 0),
            (
                "Zero quantity",
                code("""
                item,quantity,price
                box,0,9
            """),
                0,
            ),
        )
    ),
    (
        "DictReader gives strings; convert both numeric columns with int().",
        "Add quantity multiplied by price to the total for each row.",
    ),
)

add(
    "regex-validation",
    "Matching text patterns",
    "Validate complete text with regular expressions",
    "b-data",
    code(
        """
        import re

        def valid_code(text):
            return re.fullmatch(r"[A-Z]{2}-[0-9]{3}", text) is not None
        """
    ),
    "",
    (
        case("Validate 'AB-123'", "valid_code('AB-123')", True),
        case("Validate 'ZZ-000'", "valid_code('ZZ-000')", True),
        case("Validate 'ab-123'", "valid_code('ab-123')", False),
        case("Validate 'XAB-123Y'", "valid_code('XAB-123Y')", False),
        case("Validate 'AB-123\\n'", "valid_code('AB-123\\n')", False),
        case("Validate 'AB-１２３'", "valid_code('AB-１２３')", False),
        case("Validate ''", "valid_code('')", False),
        case("Validate 'A-123'", "valid_code('A-123')", False),
        case("Validate 'AB-12'", "valid_code('AB-12')", False),
    ),
    (
        "fullmatch requires the entire string to match.",
        "Use [0-9] for the required digits 0 through 9; \\d also includes other digit characters.",
    ),
)

add(
    "regex-transformations",
    "Extracting and replacing text",
    "Find values and replace matching text",
    "b-data",
    code(
        """
        import re

        def redact_tags(text):
            pattern = r"\\[user:([a-z]+)\\]"
            names = re.findall(pattern, text)
            return names, re.sub(pattern, "[user:hidden]", text)
        """
    ),
    "",
    (
        case("Redact sample 1", "redact_tags('')", ([], "")),
        case("Redact sample 2", "redact_tags('hello')", ([], "hello")),
        case("Redact sample 3", "redact_tags('[user:ada]')", (["ada"], "[user:hidden]")),
        case(
            "Redact sample 4",
            "redact_tags('[user:ada] met [user:bob] [user:ada]')",
            (["ada", "bob", "ada"], "[user:hidden] met [user:hidden] [user:hidden]"),
        ),
        case(
            "Redact sample 5",
            "redact_tags('[user:Ada] [user:] [user:ab2]')",
            ([], "[user:Ada] [user:] [user:ab2]"),
        ),
        case("Redact sample 6", "redact_tags('x[user:zoe]\\ny')", (["zoe"], "x[user:hidden]\ny")),
    ),
    (
        "A single capture group makes findall return just the captured names.",
        "sub replaces every match by default; count=1 limits it to the first.",
    ),
)

add(
    "your-own-modules",
    "Writing your own modules",
    "Share functions across Python files",
    "b-tools",
    "from conversions import minutes_to_seconds\n",
    "",
    (
        case("One minute", "minutes_to_seconds(1)", 60),
        case("No minutes", "minutes_to_seconds(0)", 0),
        case(
            "Call the function from the imported module",
            "__import__('conversions').minutes_to_seconds(7)",
            420,
        ),
        case("Imports produce no output", "__stdout__", ""),
    ),
    (
        "Put the function definition in conversions.py.",
        "In lesson.py use from conversions import minutes_to_seconds.",
    ),
    files=(
        {
            "lesson.py": "from conversions import minutes_to_seconds\n",
            "conversions.py": code("""
                def minutes_to_seconds(minutes):
                    return minutes * 60
            """),
        },
    ),
)

add(
    "command-line-options",
    "Command-line arguments",
    "Give a tool a predictable interface",
    "b-tools",
    (
        code("""
            import argparse

            def make_parser():
                parser = argparse.ArgumentParser()
                parser.add_argument("name")
                parser.add_argument("--count", type=int, default=1)
                return parser
        """)
    ),
    (""),
    (
        case("Defaults", "vars(make_parser().parse_args(['Ada']))", {"name": "Ada", "count": 1}),
        case(
            "Explicit integer",
            "vars(make_parser().parse_args(['Lin', '--count', '3']))",
            {"name": "Lin", "count": 3},
        ),
    ),
    (
        "Create the parser, add both arguments, then return the parser object.",
        "Use type=int and default=1 for --count.",
    ),
)

add(
    "your-first-class",
    "Your first class",
    "Keep state and related operations together",
    "b-tools",
    (
        code("""
            class Wallet:
                def __init__(self):
                    self.balance = 0

                def deposit(self, amount):
                    self.balance = self.balance + amount
                    return self.balance

                def spend(self, amount):
                    if amount > self.balance:
                        return False
                    self.balance = self.balance - amount
                    return True
        """)
    ),
    (""),
    (
        case(
            "Successful and refused spending",
            "(lambda w: [w.deposit(8), w.spend(3), w.spend(10), w.balance])(Wallet())",
            [8, True, False, 5],
        ),
        case(
            "Independent wallets",
            "(lambda a,b: (a.deposit(5), b.balance)[1])(Wallet(), Wallet())",
            0,
        ),
        case("Spend zero", "Wallet().spend(0)", True),
        case(
            "Spend the complete balance",
            "(lambda w: [w.deposit(6), w.spend(6), w.balance])(Wallet())",
            [6, True, 0],
        ),
    ),
    (
        "Store balance in __init__ using self.balance.",
        "Check amount > self.balance before subtracting anything.",
    ),
)

add(
    "named-states",
    "Named states with enums",
    "Represent a fixed set of meaningful values",
    "b-tools",
    code(
        """
        from enum import Enum

        class Status(Enum):
            TODO = "todo"
            DOING = "doing"
            DONE = "done"

        def next_status(status):
            if status is Status.TODO:
                return Status.DOING
            return Status.DONE
        """
    ),
    "",
    (
        case(
            "Defined members",
            "[(s.name, s.value) for s in Status]",
            [("TODO", "todo"), ("DOING", "doing"), ("DONE", "done")],
        ),
        case("Start work", "next_status(Status.TODO) is Status.DOING", True),
        case("Finish work", "next_status(Status.DOING) is Status.DONE", True),
        case("Finished stays finished", "next_status(Status.DONE) is Status.DONE", True),
        case("Look up by stored value", "Status('doing') is Status.DOING", True),
        case("Real Enum type", "issubclass(Status, __import__('enum').Enum)", True),
    ),
    (
        "Subclass Enum and assign the three string values inside the class.",
        "Treat DONE as a final state that cannot move backward.",
    ),
)

add(
    "tests-for-your-code",
    "Writing automated tests",
    "Use unittest to check expected results",
    "b-tools",
    (
        code("""
            import unittest

            def clamp(value, low, high):
                if value < low:
                    return low
                if value > high:
                    return high
                return value

            class ClampTests(unittest.TestCase):
                def test_below(self):
                    self.assertEqual(clamp(-2, 0, 10), 0)

                def test_inside(self):
                    self.assertEqual(clamp(5, 0, 10), 5)

                def test_above(self):
                    self.assertEqual(clamp(12, 0, 10), 10)
        """)
    ),
    (""),
    (
        case("Lower boundary", "clamp(-2, 0, 10)", 0),
        case("Upper boundary", "clamp(12, 0, 10)", 10),
        case("Inside the range", "clamp(5, 0, 10)", 5),
        case("Equal boundaries", "clamp(9, 4, 4)", 4),
        case(
            "Your test suite passes",
            (
                "(lambda result: [result.testsRun >= 3, result.wasSuccessful()])(__impo"
                "rt__('unittest').defaultTestLoader.loadTestsFromTestCase(ClampTes"
                "ts).run(__import__('unittest').TestResult()))"
            ),
            [True, True],
        ),
        *tuple(
            case(
                "Your tests reject a function always returning " + stub,
                "(ClampTests.test_below.__globals__.__setitem__('clamp', "
                f"lambda value, low, high: {stub}), "
                "__import__('unittest').defaultTestLoader.loadTestsFromTestCase(ClampTests)"
                ".run(__import__('unittest').TestResult()).wasSuccessful())[1]",
                False,
                nudge="Your tests should fail when clamp is replaced with this incorrect stub.",
            )
            for stub in ("low", "value", "high")
        ),
        case(
            "Tests cover all three cases",
            "set(['test_below', 'test_inside', 'test_above']).issubset(dir(ClampTests))",
            True,
        ),
    ),
    (
        "Implement the three return cases before writing tests for each one.",
        "Use assertEqual with an input below, inside, and above a 0 to 10 range.",
    ),
)

add(
    "comprehensions",
    "Readable comprehensions",
    "Transform and filter without hiding the intent",
    "b-automation",
    (
        code("""
            def positive_squares(numbers):
                return sorted([number * number for number in numbers if number > 0])
        """)
    ),
    (""),
    (
        case("Filter, order, retain duplicates", "positive_squares([3, -2, 1, 3, 0])", [1, 9, 9]),
        case("No positives", "positive_squares([-2, 0])", []),
        case("Empty collection", "positive_squares([])", []),
        case(
            "Input unchanged",
            "(lambda values: (positive_squares(values), values)[1])([3, 1])",
            [3, 1],
        ),
    ),
    (
        "Filter with number > 0, not >= 0.",
        "Use a list rather than a set so repeated inputs remain repeated outputs.",
    ),
)

add(
    "counting-and-grouping",
    "Counting and grouping",
    "Use Counter and defaultdict for collections",
    "b-automation",
    code(
        """
        from collections import Counter, defaultdict

        def summarize_visits(visits):
            counts = Counter()
            pages = defaultdict(list)
            for user, page in visits:
                counts[user] += 1
                pages[user].append(page)
            return dict(counts), dict(pages)
        """
    ),
    "",
    (
        case("Visit summary 1", "summarize_visits([])", ({}, {})),
        case(
            "Visit summary 2",
            "summarize_visits([('ada', 'home')])",
            ({"ada": 1}, {"ada": ["home"]}),
        ),
        case(
            "Visit summary 3",
            "summarize_visits([('ada', 'home'), ('bob', 'help'), ('ada', 'home"
            "'), ('ada', 'about')])",
            ({"ada": 3, "bob": 1}, {"ada": ["home", "home", "about"], "bob": ["help"]}),
        ),
        case("Visit summary 4", "summarize_visits([('', '')])", ({"": 1}, {"": [""]})),
        case(
            "Input stays unchanged",
            "(lambda visits: (summarize_visits(visits), visits))([('a', 'x'), ('a', 'y')])",
            (({"a": 2}, {"a": ["x", "y"]}), [("a", "x"), ("a", "y")]),
        ),
    ),
    (
        "Counter starts an unseen key at zero; defaultdict(list) creates a"
        "n independent list for each new key.",
        "Append each page instead of replacing earlier pages.",
    ),
)

add(
    "queues-with-deque",
    "Queues with deque",
    "Process work in arrival order",
    "b-automation",
    code(
        """
        from collections import deque

        def process_queue(waiting, arrivals, limit):
            queue = deque(waiting)
            queue.extend(arrivals)
            served = []
            while queue and len(served) < limit:
                served.append(queue.popleft())
            return served, list(queue)
        """
    ),
    "",
    (
        case("Arrival order", "process_queue(['a', 'b'], ['c'], 2)", (["a", "b"], ["c"])),
        case("No capacity", "process_queue(['a'], ['b'], 0)", ([], ["a", "b"])),
        case("More capacity than work", "process_queue([], ['a', 'b'], 8)", (["a", "b"], [])),
        case("Empty queues", "process_queue([], [], 2)", ([], [])),
        case("Repeated names", "process_queue(['x', 'x'], ['x'], 2)", (["x", "x"], ["x"])),
        case(
            "Inputs stay unchanged",
            "(lambda waiting, arrivals: (process_queue(waiting, arrivals, 1), "
            "waiting, arrivals))(['a'], ['b'])",
            ((["a"], ["b"]), ["a"], ["b"]),
        ),
    ),
    (
        "Append arrivals at the right and remove waiting work from the left.",
        "popleft serves the oldest item; pop serves the newest item.",
    ),
)

add(
    "dates-and-deadlines",
    "Dates and deadlines",
    "Use date arithmetic instead of counting calendar days yourself",
    "b-automation",
    (
        code("""
            from datetime import date, timedelta

            def due_date(start, days):
                return (date.fromisoformat(start) + timedelta(days=days)).isoformat()
        """)
    ),
    (""),
    tuple(
        case(f"{start} plus {days} days", f"due_date({start!r}, {days})", expected)
        for start, days, expected in (
            ("2023-12-31", 1, "2024-01-01"),
            ("2024-02-28", 2, "2024-03-01"),
            ("2024-05-10", 0, "2024-05-10"),
        )
    ),
    (
        "Parse the start with date.fromisoformat.",
        "Add timedelta(days=days), then call isoformat() on the resulting date.",
    ),
)

add(
    "validate-boundaries",
    "Validating a tool’s inputs",
    "State acceptable inputs before touching files",
    "b-automation",
    (
        code("""
            def valid_filename(name):
                if name == "" or name == "." or name == "..":
                    return False
                if "/" in name or "\\\\" in name:
                    return False
                return name == name.strip()
        """)
    ),
    "",
    tuple(
        case(f"Validate {name!r}", f"valid_filename({name!r})", expected)
        for name, expected in (
            ("meeting notes.txt", True),
            ("café.txt", True),
            ("", False),
            (".", False),
            ("..", False),
            ("../notes.txt", False),
            ("a\\b", False),
            (" notes.txt", False),
            ("notes.txt ", False),
        )
    ),
    (
        "Reject the three special names, then either separator.",
        "The last check can compare name with name.strip() to detect outer whitespace.",
    ),
)

add(
    "copy-with-care",
    "Copying without overwriting",
    "Preview work and protect existing data",
    "b-automation",
    (
        code("""
            import shutil

            def copy_new(source, destination):
                with open(source, "rb") as input_file:
                    try:
                        with open(destination, "xb") as output_file:
                            shutil.copyfileobj(input_file, output_file)
                    except FileExistsError:
                        return False
                return True
        """)
    ),
    (""),
    (
        case(
            "Copy new bytes",
            (
                "(__import__('pathlib').Path('original.bin').write_bytes(bytes([0,255,97,98,99]))"
                ", (lambda result: [result, list(__import__('pathlib').Path('new.b"
                "in').read_bytes())])(copy_new('original.bin', 'new.bin')))[1]"
            ),
            [True, [0, 255, 97, 98, 99]],
        ),
        case(
            "Keep existing destination",
            (
                "(__import__('pathlib').Path('source.txt').write_text('new'), __im"
                "port__('pathlib').Path('dest.txt').write_text('keep'), (lambda re"
                "sult: [result, __import__('pathlib').Path('dest.txt').read_text()"
                ", __import__('pathlib').Path('source.txt').read_text()])(copy_new"
                "('source.txt', 'dest.txt')))[2]"
            ),
            [False, "keep", "new"],
        ),
    ),
    (
        "Open the destination with xb, not wb.",
        "Catch FileExistsError and return False; return True only after copying finishes.",
    ),
)

_FOUNDATION_STAGES = {
    "first-light": (
        stage_contract(
            "Build a two-line display. Print the exact text `Hello, world!` first. "
            "Print the result of `8 + 5` second. Keep text quoted and arithmetic unquoted.",
            """
            print("Hello, world!")
            print(8 + 5)
            """,
            "",
            (
                case(
                    "Welcome display",
                    "__stdout__.strip().splitlines()",
                    ["Hello, world!", "13"],
                    output="Hello, world!\n13",
                    nudge="Check the quotes around the greeting and leave 8 + 5 outside quotes.",
                ),
            ),
            (
                "Use one print call for the text and one for the arithmetic expression.",
                "The second line should evaluate 8 + 5, not print those characters as text.",
            ),
        ),
        stage_contract(
            "Repair a three-line event sign. It must print `Today's plan`, then `Bring water`, "
            "then `Start at 9`. Run the supplied program to investigate the mistake before "
            "changing it.",
            """
            print("Today's plan")
            print("Bring water")
            print("Start at 9")
            """,
            """
            print("Today's plan")
            print("Bring water)
            print("Start at 9")
            """,
            (
                case(
                    "Event sign",
                    "__stdout__.strip().splitlines()",
                    ["Today's plan", "Bring water", "Start at 9"],
                    output="Today's plan\nBring water\nStart at 9",
                    nudge=(
                        "Read the syntax error and compare the punctuation around each text value."
                    ),
                ),
            ),
            (
                "Read the error output first and inspect the line it identifies.",
                "Compare the opening and closing punctuation on each printed text value.",
            ),
        ),
    ),
    "names-and-voices": (
        stage_contract(
            "Ask for a name and store it in `student`. Build `greeting` with an f-string "
            "containing `Welcome, `, the name, and `!`, then print it.",
            """
            student = input("What is your name? ")
            greeting = f"Welcome, {student}!"
            print(greeting)
            """,
            "",
            tuple(
                case(
                    f"Greeting for {student}",
                    "greeting",
                    f"Welcome, {student}!",
                    stdin=student + "\n",
                    output=f"Welcome, {student}!",
                    nudge=(
                        "Check that input is stored in student and the f-string uses that variable."
                    ),
                )
                for student in ("Ada", "Lin", "Alex Chen")
            ),
            (
                "Store input(...) in student before constructing the greeting.",
                "Start the greeting with f and put {student} inside the quotes.",
            ),
            "Ada\n",
        ),
        stage_contract(
            "Repair a mailing label. Read a given name, then a city, store the complete label in "
            "`label`, and print `Given lives in City.` with the supplied values.",
            """
            given = input("Given name: ")
            city = input("City: ")
            label = f"{given} lives in {city}."
            print(label)
            """,
            """
            given = input("Given name: ")
            city = input("City: ")
            label = "given lives in city."
            print(label)
            """,
            tuple(
                case(
                    f"Label for {given} in {city}",
                    "label",
                    f"{given} lives in {city}.",
                    stdin=f"{given}\n{city}\n",
                    output=f"{given} lives in {city}.",
                    nudge=(
                        "Use both input variables in the f-string; literal words cannot adapt "
                        "to new answers."
                    ),
                )
                for given, city in (("Ada", "Boston"), ("Lin", "Oslo"), ("Mina", "Lima"))
            ),
            (
                "Read two answers, storing them in given and city.",
                'Write label = f"{given} lives in {city}." before printing label.',
            ),
            "Ada\nBoston\n",
        ),
    ),
    "numbers-from-input": (
        stage_contract(
            "Read a nonnegative whole number of minutes into `minutes`. Store complete hours "
            "in `hours` with `//`, leftover minutes in `remaining` with `%`, and print both "
            "values on separate lines.",
            """
            minutes = int(input("Minutes: "))
            hours = minutes // 60
            remaining = minutes % 60
            print(hours)
            print(remaining)
            """,
            "",
            tuple(
                case(
                    f"Convert {n} minutes",
                    "[hours, remaining]",
                    [h, r],
                    stdin=f"{n}\n",
                    output=f"{h}\n{r}",
                    nudge="Use // for complete groups of 60 and % for the leftover minutes.",
                )
                for n, h, r in ((125, 2, 5), (0, 0, 0), (59, 0, 59), (60, 1, 0))
            ),
            (
                "Convert input text with int(input(...)) before doing arithmetic.",
                "Use // for hours and % for the remainder, then print hours followed by remaining.",
            ),
            "125\n",
        ),
        stage_contract(
            "Repair a study-time summary. Read morning minutes and afternoon minutes, add them "
            "into `total`, calculate complete `hours` and leftover `minutes`, and print "
            "`H h M min`. At a total of exactly 60 minutes, print `1 h 0 min`.",
            """
            morning = int(input("Morning minutes: "))
            afternoon = int(input("Afternoon minutes: "))
            total = morning + afternoon
            hours = total // 60
            minutes = total % 60
            print(f"{hours} h {minutes} min")
            """,
            """
            morning = int(input("Morning minutes: "))
            afternoon = int(input("Afternoon minutes: "))
            total = morning + afternoon
            hours = total // 60
            minutes = morning % 60
            print(f"{hours} h {minutes} min")
            """,
            tuple(
                case(
                    f"Study total {morning} + {afternoon}",
                    "[hours, minutes]",
                    [hours, minutes],
                    stdin=f"{morning}\n{afternoon}\n",
                    output=f"{hours} h {minutes} min",
                    nudge=(
                        "Add both inputs before splitting total; the remainder belongs to total, "
                        "not one session."
                    ),
                )
                for morning, afternoon, hours, minutes in (
                    (30, 30, 1, 0),
                    (0, 0, 0, 0),
                    (20, 39, 0, 59),
                    (75, 60, 2, 15),
                )
            ),
            (
                "Convert both answers with int(input(...)) and add them into total.",
                "Apply // 60 and % 60 to total after the addition, not to just one input.",
            ),
            "30\n30\n",
        ),
    ),
    "decimal-measurements": (
        stage_contract(
            "Read a decimal number of centimeters into `centimeters`. Store the unrounded "
            "meter value in `meters` by dividing by 100, then print it with two decimal places "
            "and the suffix ` m`.",
            """
            centimeters = float(input("Centimeters: "))
            meters = centimeters / 100
            print(f"{meters:.2f} m")
            """,
            "",
            tuple(
                case(
                    label,
                    f"abs(meters - {expected!r}) < 0.000000001",
                    True,
                    stdin=text + "\n",
                    output=output,
                    nudge=(
                        "Keep the fractional value with / and apply .2f only in the printed text."
                    ),
                )
                for label, text, expected, output in (
                    ("Fractional centimeters", "172.4", 1.724, "1.72 m"),
                    ("Zero length", "0", 0.0, "0.00 m"),
                    ("Small length", "1.2", 0.012, "0.01 m"),
                    ("Exact meter", "100", 1.0, "1.00 m"),
                    ("Keep the unrounded value", "234.56", 2.3456, "2.35 m"),
                )
            ),
            (
                "Read with float(input(...)) so a decimal fraction is not discarded.",
                'Divide by 100 with / and use f"{meters:.2f} m" only when printing.',
            ),
            "172.4\n",
        ),
        stage_contract(
            "Repair a temperature display. Read Fahrenheit into `fahrenheit`, calculate the "
            "unrounded Celsius value in `celsius` with `(fahrenheit - 32) / 1.8`, and print "
            "one line with one decimal place followed by ` C`.",
            """
            fahrenheit = float(input("Fahrenheit: "))
            celsius = (fahrenheit - 32) / 1.8
            print(f"{celsius:.1f} C")
            """,
            """
            fahrenheit = float(input("Fahrenheit: "))
            celsius = fahrenheit - 32 / 1.8
            print(f"{celsius} C")
            """,
            tuple(
                case(
                    f"{fahrenheit} F",
                    f"abs(celsius - {expected!r}) < 0.000000001",
                    True,
                    stdin=f"{fahrenheit}\n",
                    output=f"{display} C",
                    nudge=(
                        "Use parentheses around Fahrenheit minus 32, then format celsius at print "
                        "time."
                    ),
                )
                for fahrenheit, expected, display in (
                    (32, 0.0, "0.0"),
                    (212, 100.0, "100.0"),
                    (98.6, 37.0, "37.0"),
                    (-40, -40.0, "-40.0"),
                )
            ),
            (
                "Subtract 32 before dividing by 1.8; parentheses control that order.",
                "Format the stored celsius value with one decimal place in the print f-string.",
            ),
            "98.6\n",
        ),
    ),
    "choose-a-door": (
        stage_contract(
            "Ask for a key and store it in `key`. Set `destination` to `treasure` for `gold`, "
            "`garden` for `green`, and `locked` for every other answer. Use one if/elif/else "
            "chain, then print destination.",
            """
            key = input("Which key? ")
            if key == "gold":
                destination = "treasure"
            elif key == "green":
                destination = "garden"
            else:
                destination = "locked"
            print(destination)
            """,
            "",
            tuple(
                case(
                    f"Key: {key}",
                    "destination",
                    destination,
                    stdin=key + "\n",
                    output=destination,
                    nudge=(
                        "Use elif so the final else belongs to the whole choice, not only the "
                        "second test."
                    ),
                )
                for key, destination in (
                    ("gold", "treasure"),
                    ("green", "garden"),
                    ("blue", "locked"),
                )
            ),
            (
                'Begin with if key == "gold" and indent its assignment beneath it.',
                (
                    "Use elif for green and else for every other key, then print destination "
                    "outside the chain."
                ),
            ),
            "gold\n",
        ),
        stage_contract(
            "Repair a parcel-size classifier. Read an integer item count into `items`. Set "
            "`size` to `empty` for 0, `small` for 1 through 3, and `large` for anything "
            "greater than 3. Print size. Check the equality boundaries carefully.",
            """
            items = int(input("Items: "))
            if items == 0:
                size = "empty"
            elif items <= 3:
                size = "small"
            else:
                size = "large"
            print(size)
            """,
            """
            items = int(input("Items: "))
            if items <= 1:
                size = "empty"
            elif items < 3:
                size = "small"
            else:
                size = "large"
            print(size)
            """,
            tuple(
                case(
                    f"{items} parcel items",
                    "size",
                    expected,
                    stdin=f"{items}\n",
                    output=expected,
                    nudge="Test the exact boundaries: only zero is empty, and 3 is still small.",
                )
                for items, expected in (
                    (0, "empty"),
                    (1, "small"),
                    (3, "small"),
                    (4, "large"),
                    (10, "large"),
                )
            ),
            (
                "Convert the input to int before comparing it with zero and three.",
                "Use one if/elif/else chain so each count receives exactly one size.",
            ),
            "3\n",
        ),
    ),
}


_FOUNDATION_METADATA = {
    "first-light": (
        "Your first program",
        "Strings, integers, and output",
        8,
        ("Values & output",),
    ),
    "names-and-voices": (
        "Variables and input",
        "Store values and ask the user a question",
        10,
        ("Variables & strings",),
    ),
    "numbers-from-input": (
        "Numbers from input",
        "Convert text and calculate whole-number results",
        15,
        ("Numbers & arithmetic",),
    ),
    "decimal-measurements": (
        "Decimal measurements",
        "Read decimal input and format a calculated measurement",
        15,
        ("Numbers & arithmetic",),
    ),
    "choose-a-door": (
        "Making decisions",
        "Comparisons, booleans, if, elif, and else",
        15,
        ("Conditions",),
    ),
}


def foundation_lesson(identifier):
    build, repair = _FOUNDATION_STAGES[identifier]
    title, subtitle, minutes, concepts = _FOUNDATION_METADATA[identifier]
    legacy = next((lesson for lesson in LEGACY if lesson.id == identifier), None)
    return Lesson(
        identifier,
        "beginner",
        title,
        subtitle,
        minutes,
        concepts,
        lesson_text(identifier),
        repair.starter_files["lesson.py"],
        build.checks,
        build.hints,
        legacy.prediction if legacy else "",
        legacy.choices if legacy else (),
        legacy.answer if legacy else 0,
        legacy.explanation if legacy else "",
        build.reference_files["lesson.py"],
        revision=5,
        chapter_id="b-foundations",
        files=build.files,
        solution_files=build.reference_files,
        repair_files=repair.starter_files,
        stdin=build.stdin,
        build_stage=build,
        repair_stage=repair,
    )


_foundation_lessons = [foundation_lesson(identifier) for identifier in _FOUNDATION_METADATA]
_pack_position = next(index for index, lesson in enumerate(_units) if lesson.id == "pack-your-bag")
_units[_pack_position:_pack_position] = _foundation_lessons

_extra_by_id = {lesson.id: lesson for lesson in EXTRA_LESSONS}
for _anchor, _identifier in INSERT_AFTER.items():
    _position = next(index for index, lesson in enumerate(_units) if lesson.id == _anchor)
    _units.insert(_position + 1, _extra_by_id[_identifier])


LESSONS = tuple(
    replace(
        lesson,
        prerequisites=(_units[index - 1].id,) if index else (),
    )
    for index, lesson in enumerate(_units)
)


def _refresh_stages(lessons):
    refreshed = []
    for lesson in lessons:
        repair = REPAIR_STAGES.get(lesson.id)
        if repair is None:
            refreshed.append(lesson)
            continue
        build = StageContract(
            instructions=BUILD_INSTRUCTIONS[lesson.id],
            checks=lesson.checks,
            hints=lesson.hints,
            stdin=lesson.stdin,
            files=lesson.files,
            starter_files={name: "" for name in lesson.files},
            reference_files=lesson.solution_files or {lesson.entrypoint: lesson.solution},
        )
        refreshed.append(
            replace(
                lesson,
                revision=5,
                repair=repair.starter_files[lesson.entrypoint],
                checks=build.checks,
                hints=build.hints,
                solution=build.reference_files[lesson.entrypoint],
                solution_files=build.reference_files,
                repair_files=repair.starter_files,
                stdin=build.stdin,
                build_stage=build,
                repair_stage=repair,
            )
        )
    return tuple(refreshed)


LESSONS = _refresh_stages(LESSONS)

LESSONS = apply_checkpoints(LESSONS)
