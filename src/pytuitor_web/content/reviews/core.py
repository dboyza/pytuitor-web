"""Transfer practice for the eleven core chapters, within their taught syntax."""

from pytuitor_web.content.reviews.authoring import chapter, prediction, task

CORE = {
    "first-programs": chapter(
        "first-programs",
        prediction(
            "A boundary decision",
            """
                seats = 3
                people = 3
                print(people <= seats)
            """,
            ("True", "False", "3"),
            0,
            "Equality satisfies <=, so exactly three people fit.",
        ),
        task(
            "Repair the change",
            "Keep cost = 7 and paid = 10. Print exactly Change: 3. Repair the calculation.",
            """
                cost = 7
                paid = 10
                print("Change:", paid - cost)
            """,
            [
                ("Correct change", "__stdout__.strip()", "Change: 3"),
                ("Keep the given values", "[cost, paid]", [7, 10]),
            ],
            broken="""
                cost = 7
                paid = 10
                print("Change:", cost - paid)
            """,
            hint="Subtract the cost from the amount paid.",
        ),
        task(
            "Write a ticket total",
            "Set adults = 2 and children = 3. An adult ticket costs 5 "
            "and a child ticket costs 2. Calculate total and print "
            "exactly Total: 16.",
            """
                adults = 2
                children = 3
                total = adults * 5 + children * 2
                print("Total:", total)
            """,
            [
                ("Counts and total", "[adults, children, total]", [2, 3, 16]),
                ("Printed receipt", "__stdout__.strip()", "Total: 16"),
            ],
            hint="Calculate the cost of each group, then add the two amounts.",
        ),
    ),
    "lists-and-sets": chapter(
        "lists-and-sets",
        prediction(
            "Repeated supplies",
            """
                items = ["cup", "cup", "map"]
                print(len(items), len(set(items)))
            """,
            ("3 2", "2 2", "3 3"),
            0,
            "The list retains both cups; the set has two distinct kinds.",
        ),
        task(
            "Repair a missing-items report",
            'Keep owned = {"cup", "map"} and required = {"map", '
            '"lamp"}. Set missing to required items not owned. Do not '
            "change either input.",
            """
                owned = {"cup", "map"}
                required = {"map", "lamp"}
                missing = required - owned
            """,
            [
                ("Missing equipment", "sorted(missing)", ["lamp"]),
                (
                    "Inputs preserved",
                    "[sorted(owned), sorted(required)]",
                    [["cup", "map"], ["lamp", "map"]],
                ),
            ],
            broken="""
                owned = {"cup", "map"}
                required = {"map", "lamp"}
                missing = owned - required
            """,
            hint="The left side of set difference is the collection you are "
            "checking for missing items.",
        ),
        task(
            "Read the ends",
            'Create names = ["Ari", "Bo", "Cy"]. Store the first and '
            "last names in a tuple called ends. Leave names unchanged.",
            """
                names = ["Ari", "Bo", "Cy"]
                ends = (names[0], names[-1])
            """,
            [
                ("First and last", "list(ends)", ["Ari", "Cy"]),
                ("Names unchanged", "names", ["Ari", "Bo", "Cy"]),
            ],
            hint="Position 0 is first; position -1 is last.",
        ),
    ),
    "loops-and-dictionaries": chapter(
        "loops-and-dictionaries",
        prediction(
            "An accumulator",
            """
                total = 0
                for n in [2, 0, 3]:
                    total = total + n
                print(total)
            """,
            ("3", "5", "0"),
            1,
            "Each iteration adds to the existing total; adding zero leaves it unchanged.",
        ),
        task(
            "Repair duplicate counting",
            'Keep words = ["rain", "sun", "rain"]. Build counts with '
            "every occurrence counted. Do not alter words.",
            """
                words = ["rain", "sun", "rain"]
                counts = {}
                for word in words:
                    counts[word] = counts.get(word, 0) + 1
            """,
            [
                ("Both rain entries counted", "counts", {"rain": 2, "sun": 1}),
                ("Original words", "words", ["rain", "sun", "rain"]),
            ],
            broken="""
                words = ["rain", "sun", "rain"]
                counts = {}
                for word in words:
                    counts[word] = 1
            """,
            hint="Use the previous count when the word already has an entry.",
        ),
        task(
            "Collect positive readings",
            "Keep readings = [0, 4, -2, 7]. Use a loop to create "
            "positive containing only values greater than zero in "
            "their original order.",
            """
                readings = [0, 4, -2, 7]
                positive = []
                for value in readings:
                    if value > 0:
                        positive.append(value)
            """,
            [
                ("Positive values in order", "positive", [4, 7]),
                ("Readings unchanged", "readings", [0, 4, -2, 7]),
            ],
            hint="Start with an empty list and append only inside the condition.",
        ),
    ),
    "functions-and-input": chapter(
        "functions-and-input",
        prediction(
            "Return a value",
            """
                def double(n):
                    return n * 2


                answer = double(4)
                print(answer + 1)
            """,
            ("8", "9", "None"),
            1,
            "The returned 8 becomes answer; the final expression adds one.",
        ),
        task(
            "Repair a zero quantity",
            "quantity(text) returns a nonnegative integer parsed from "
            "a string, or None for invalid or negative input. Zero and "
            "surrounding whitespace are valid.",
            """
                def quantity(text):
                    try:
                        value = int(text)
                    except ValueError:
                        return None
                    return value if value >= 0 else None
            """,
            [
                ("Zero is valid", 'quantity("0")', 0),
                ("Whitespace is valid", 'quantity(" 4 ")', 4),
                ("Bad quantities", '[quantity("-1"), quantity("no")]', [None, None]),
            ],
            broken="""
                def quantity(text):
                    try:
                        value = int(text)
                    except ValueError:
                        return None
                    return value if value > 0 else None
            """,
            hint="Zero belongs on the accepted side of the boundary.",
        ),
        task(
            "Write a bounded refill",
            "Define refill(current, added, limit=20). Inputs are "
            "nonnegative integers. Return current + added capped at "
            "limit. Do not prompt or print.",
            """
                def refill(current, added, limit=20):
                    total = current + added
                    if total > limit:
                        total = limit
                    return total
            """,
            [
                ("Default cap", "refill(18, 5)", 20),
                ("Custom cap", "refill(3, 9, limit=8)", 8),
                ("No refill", "refill(0, 0)", 0),
            ],
            hint="Compare the computed total with the limit before returning it.",
        ),
    ),
    "files-and-data": chapter(
        "files-and-data",
        prediction(
            "JSON values",
            """
                import json

                record = json.loads('{"count": 0, "ready": false}')
                print(record["count"], record["ready"])
            """,
            ("0 False", '"0" "false"', "0 false"),
            0,
            "JSON numbers and booleans become Python values, including Python False.",
        ),
        task(
            "Repair a fresh read",
            "read_note(path) must return the complete UTF-8 text in a "
            "file without changing it. A missing file may raise OSError.",
            """
                from pathlib import Path


                def read_note(path):
                    return Path(path).read_text(encoding="utf-8")
            """,
            [
                (
                    "Read Unicode text",
                    '(exec("from pathlib import '
                    "Path\\nPath('note.txt').write_text('café\\\\n', "
                    "encoding='utf-8')\", globals()), "
                    'read_note("note.txt"))[1]',
                    "café\n",
                )
            ],
            broken="""
                from pathlib import Path


                def read_note(path):
                    return Path(path).write_text("", encoding="utf-8")
            """,
            hint="Reading should not open the file for writing.",
        ),
        task(
            "Write a JSON round trip",
            "Define save_items(path, items) and load_items(path) using "
            "UTF-8 JSON. items is a list of text labels. Preserve "
            "order, repeats, and empty lists.",
            """
                import json
                from pathlib import Path


                def save_items(path, items):
                    Path(path).write_text(json.dumps(items), encoding="utf-8")


                def load_items(path):
                    return json.loads(Path(path).read_text(encoding="utf-8"))
            """,
            [
                (
                    "Repeated and Unicode items",
                    '(save_items("pack.json", ["café", "map", "map"]), load_items("pack.json"))[1]',
                    ["café", "map", "map"],
                ),
                ("Empty list", '(save_items("empty.json", []), load_items("empty.json"))[1]', []),
            ],
            hint="Serialize when saving and deserialize when loading; return the decoded value.",
        ),
    ),
    "text-patterns": chapter(
        "text-patterns",
        prediction(
            "Whole text or a prefix?",
            """
                import re

                print(re.fullmatch(r"[A-Z]{2}", "AB3") is None)
            """,
            ("False", "True", "AB"),
            1,
            "A full match must consume the entire string, including the unwanted 3.",
        ),
        task(
            "Repair a code boundary",
            "valid_code(text) returns True only for exactly two "
            "uppercase ASCII letters followed by two ASCII digits, "
            "with no extra characters.",
            """
                import re


                def valid_code(text):
                    return re.fullmatch(r"[A-Z]{2}[0-9]{2}", text) is not None
            """,
            [
                ("Valid code", 'valid_code("AB12")', True),
                (
                    "Reject suffix and prefix",
                    '[valid_code("AB123"), valid_code("xAB12")]',
                    [False, False],
                ),
                ("Reject lowercase", 'valid_code("ab12")', False),
            ],
            broken="""
                import re


                def valid_code(text):
                    return re.match(r"[A-Z]{2}[0-9]{2}", text) is not None
            """,
            hint="A prefix match is not a full-string validation.",
        ),
        task(
            "Extract measurements",
            "Define measurements(text), returning all runs of one or "
            "more ASCII digits followed immediately by km. Return just "
            "the digit strings in order; no matches gives [].",
            """
                import re


                def measurements(text):
                    return re.findall(r"([0-9]+)km", text)
            """,
            [
                ("Two measurements", 'measurements("walk 3km then 12km")', ["3", "12"]),
                ("No measurements", 'measurements("3 miles")', []),
            ],
            hint="Capture the digits in parentheses and match km after that group.",
        ),
    ),
    "modules-and-library-tools": chapter(
        "modules-and-library-tools",
        prediction(
            "A local random source",
            """
                import random

                a = random.Random(7)
                b = random.Random(7)
                print(a.randint(1, 100) == b.randint(1, 100))
            """,
            ("True", "False", "It must change every run"),
            0,
            "Two independent generators with the same seed begin with the same sequence.",
        ),
        task(
            "Repair an empty summary",
            "mean_reading(values) returns statistics.mean(values), or "
            "None for an empty list. Do not change the list.",
            """
                import statistics


                def mean_reading(values):
                    if not values:
                        return None
                    return statistics.mean(values)
            """,
            [("Empty input", "mean_reading([])", None), ("A mean", "mean_reading([2, 6])", 4)],
            broken="""
                import statistics


                def mean_reading(values):
                    return statistics.mean(values)
            """,
            hint="Handle the documented empty case before calling mean.",
        ),
        task(
            "Write repeatable choices",
            "Define rolls(seed, count). Return count integer dice "
            "rolls in 1..6 using a local random.Random(seed), leaving "
            "global random state unchanged. count is nonnegative.",
            """
                import random


                def rolls(seed, count):
                    rng = random.Random(seed)
                    result = []
                    for _ in range(count):
                        result.append(rng.randint(1, 6))
                    return result
            """,
            [
                ("Empty series", "rolls(4, 0)", []),
                ("Repeatability", "rolls(4, 5) == rolls(4, 5)", True),
                (
                    "Global state retained",
                    "(exec('import random\\nbefore = "
                    "random.getstate()\\nrolls(9, 3)', globals()), "
                    "random.getstate() == before)[1]",
                    True,
                ),
                (
                    "Dice range",
                    "len(rolls(4, 5)) == 5 and all(1 <= n <= 6 for n in rolls(4, 5))",
                    True,
                ),
            ],
            hint="Create a local generator inside the function instead of "
            "reseeding the global module.",
        ),
    ),
    "dates-and-times": chapter(
        "dates-and-times",
        prediction(
            "Crossing February",
            """
                from datetime import date, timedelta

                print(date(2024, 2, 28) + timedelta(days=2))
            """,
            ("2024-03-01", "2024-02-30", "2024-03-02"),
            0,
            "2024 is a leap year; February 29 comes between these dates.",
        ),
        task(
            "Repair a deadline",
            "due(start, days) takes a datetime.date and a nonnegative "
            "number of days. Return the date days later, including "
            "across month and year boundaries.",
            """
                from datetime import timedelta


                def due(start, days):
                    return start + timedelta(days=days)
            """,
            [
                (
                    "Year boundary",
                    'str(due(__import__("datetime").date(2025, 12, 31), 1))',
                    "2026-01-01",
                ),
                ("Zero days", 'str(due(__import__("datetime").date(2025, 1, 3), 0))', "2025-01-03"),
            ],
            broken="""
                def due(start, days):
                    return start.replace(day=start.day + days)
            """,
            hint="A duration handles calendar boundaries; replacing the day field does not.",
        ),
        task(
            "Read an explicit date",
            "Define read_day(text) that parses a date in DD/MM/YYYY "
            "format and returns a datetime.date. Invalid dates may "
            "raise ValueError.",
            """
                from datetime import datetime


                def read_day(text):
                    return datetime.strptime(text, "%d/%m/%Y").date()
            """,
            [
                ("Day comes first", 'str(read_day("04/03/2025"))', "2025-03-04"),
                ("Leap date", 'str(read_day("29/02/2024"))', "2024-02-29"),
            ],
            hint="Use %d for day and %m for month, then take the date from the parsed datetime.",
        ),
    ),
    "collection-tools": chapter(
        "collection-tools",
        prediction(
            "A queue",
            """
                from collections import deque

                queue = deque(["A", "B"])
                print(queue.popleft(), list(queue))
            """,
            ("B ['A']", "A ['B']", "A ['A', 'B']"),
            1,
            "popleft removes the oldest, leftmost item.",
        ),
        task(
            "Repair an active filter",
            "active_names(records) returns names of records whose "
            "active field is True, in input order. Each record has "
            "name and active; do not modify records.",
            """
                def active_names(records):
                    return [r["name"] for r in records if r["active"]]
            """,
            [
                (
                    "Filter and preserve order",
                    'active_names([{"name":"A","active":False},{"name":"B","active":True}])',
                    ["B"],
                ),
                ("Empty records", "active_names([])", []),
            ],
            broken="""
                def active_names(records):
                    return [r["name"] for r in records if not r["active"]]
            """,
            hint="Select the records that satisfy the active condition.",
        ),
        task(
            "Count deliveries",
            "Define totals(labels), returning a dict of counts for "
            "each text label. Empty input returns {}. Do not change labels.",
            """
                from collections import Counter


                def totals(labels):
                    return dict(Counter(labels))
            """,
            [
                ("Repeated labels", 'totals(["wood", "food", "wood"])', {"wood": 2, "food": 1}),
                ("Empty delivery", "totals([])", {}),
            ],
            hint="Counter accumulates each occurrence, rather than overwriting it.",
        ),
    ),
    "classes-and-tested-tools": chapter(
        "classes-and-tested-tools",
        prediction(
            "Independent instances",
            """
                class Meter:
                    def __init__(self):
                        self.value = 0


                a = Meter()
                b = Meter()
                a.value = 4
                print(b.value)
            """,
            ("4", "0", "None"),
            1,
            "Each instance receives its own value attribute in __init__.",
        ),
        task(
            "Repair a spent token",
            "Token starts unused. claim() returns True once and False "
            "on every later call for that instance. Different tokens "
            "are independent.",
            """
                class Token:
                    def __init__(self):
                        self.used = False

                    def claim(self):
                        if self.used:
                            return False
                        self.used = True
                        return True
            """,
            [
                (
                    "Only one claim",
                    "(exec('t = Token()\\na = t.claim()\\nb = t.claim()', globals()), [a, b])[1]",
                    [True, False],
                ),
                ("Independent tokens", "[Token().claim(), Token().claim()]", [True, True]),
            ],
            broken="""
                class Token:
                    def __init__(self):
                        self.used = False

                    def claim(self):
                        if self.used:
                            return False
                        return True
            """,
            hint="Record the successful transition before returning.",
        ),
        task(
            "Write a small counter",
            "Define Counter(start=0) with value and add(amount). add "
            "updates value and returns the new value. Inputs are "
            "integers; instances must stay independent.",
            """
                class Counter:
                    def __init__(self, start=0):
                        self.value = start

                    def add(self, amount):
                        self.value += amount
                        return self.value
            """,
            [
                ("Starting value and addition", "Counter(3).add(2)", 5),
                (
                    "Repeated calls",
                    "(exec('c = Counter()\\nc.add(4)\\nc.add(-1)', globals()), c.value)[1]",
                    3,
                ),
                ("Independent default", "Counter().value", 0),
            ],
            hint="Store state on self in __init__, then update that same attribute.",
        ),
    ),
    "careful-automation": chapter(
        "careful-automation",
        prediction(
            "Preview before writing",
            """
                planned = ["a.txt", "b.txt"]
                confirmed = False
                print(len(planned) if confirmed else "preview")
            """,
            ("2", "preview", "0"),
            1,
            "Without confirmation, this expression chooses the preview branch.",
        ),
        task(
            "Repair an overwrite guard",
            "write_new(path, text) writes UTF-8 text only to a new "
            "file. If the path already exists, raise FileExistsError "
            "and leave its content unchanged.",
            """
                def write_new(path, text):
                    with open(path, "x", encoding="utf-8") as stream:
                        stream.write(text)
            """,
            [
                (
                    "New file",
                    '(write_new("new.txt", "rain"), '
                    '__import__("pathlib").Path("new.txt").read_text())[1]',
                    "rain",
                ),
                (
                    "Existing file is preserved",
                    '(exec("from pathlib import '
                    "Path\\nPath('old.txt').write_text('keep')\\ntry:\\n  "
                    "  write_new('old.txt', 'lose')\\nexcept "
                    "FileExistsError:\\n    refused = True\\nelse:\\n    "
                    'refused = False", globals()), [refused, '
                    'Path("old.txt").read_text()])[1]',
                    [True, "keep"],
                ),
            ],
            broken="""
                def write_new(path, text):
                    with open(path, "w", encoding="utf-8") as stream:
                        stream.write(text)
            """,
            hint="Exclusive creation makes an existing file an error instead of truncating it.",
        ),
        task(
            "Build a safe name check",
            "Define valid_name(name) for text. Return True only for a "
            "nonempty single file name: reject . and .., / and "
            "backslash anywhere. This exercise does not claim a "
            "complete filesystem security boundary.",
            """
                def valid_name(name):
                    return (
                        bool(name)
                        and name not in (".", "..")
                        and "/" not in name
                        and "\\\\" not in name
                    )
            """,
            [
                ("Simple file name", 'valid_name("notes.txt")', True),
                (
                    "Reject traversal and empty names",
                    '[valid_name(s) for s in ["", ".", "..", "a/b", "a\\\\b"]]',
                    [False] * 5,
                ),
            ],
            hint="Validate all the rejected forms before doing any file operation.",
        ),
    ),
}
