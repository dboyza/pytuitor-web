"""Stage contracts for b-tools."""

from pytuitor_web.beginner_authoring import _check, _scenario_check, _stage
from pytuitor_web.models import code

BUILD_INSTRUCTIONS = {
    "your-own-modules": (
        "Create `conversions.py` with a function `minutes_to_seconds(minutes)` that"
        " returns `minutes * 60`.\nInputs are nonnegative integers.\nIn `lesson.py`"
        ", import that function so it is available there under the same name.\nDo n"
        "ot print or request input at import time.\nBoth files are part of this exe"
        "rcise and both begin blank in Build."
    ),
    "numeric-tools": (
        "Define `summarize(values, capacity)`.\n`values` is a list of finite number"
        "s: ordinary integers or floats, excluding infinity and the special not-a-n"
        "umber value `nan`.\n`capacity` is an integer representing how many reading"
        "s fit into one group.\nReturn a tuple containing the mean, the median, and"
        " the number of groups needed to hold all readings.\nA partial last group c"
        "ounts, so four readings with capacity three need two groups.\nReject an em"
        "pty values list or a capacity of zero or less with `ValueError`.\nDo not c"
        "hange `values`, read input, or print.\nFor `[9, 1, 5, 3]` and capacity `3`"
        ", return `(4.5, 4.0, 2)`."
    ),
    "repeatable-randomness": (
        "Define `draw(items, count, seed)`.\n`items` is a list, `count` is an integ"
        "er, and `seed` is an integer.\nUse an independent `random.Random(seed)` an"
        "d call its `choice(items)` exactly once per draw, in order.\nReturn the ch"
        "oices in a new list, leaving both `items` and the module's shared random g"
        "enerator state unchanged.\nReject negative counts, or a positive count wit"
        "h empty items, using `ValueError`.\nZero draws return an empty list even w"
        "hen items is empty.\nThe same arguments must give the same result on repea"
        "ted calls.\nDo not read input or print."
    ),
    "command-line-options": (
        "Define `make_parser()` that returns an `argparse.ArgumentParser`.\nAdd a r"
        "equired positional argument `name` and an optional `--count` integer argum"
        "ent whose default is `1`.\nDo not parse arguments inside `make_parser()`."
        '\nThe checks call `.parse_args(...)` on your returned parser.\nFor `["Ada"'
        ', "--count", "3"]`, its attributes should be `.name == "Ada"` and `.count '
        "== 3`.\nDo not request keyboard input or print anything when this file run"
        "s."
    ),
    "your-first-class": (
        "Define a class `Wallet`.\n`Wallet()` starts with a `.balance` of `0`.\nIts"
        " method `deposit(amount)` adds a nonnegative integer amount to the balance"
        " and returns the new balance.\nIts method `spend(amount)` returns `True` a"
        "nd subtracts the amount when affordable; otherwise it returns `False` with"
        "out changing the balance.\nEach wallet must have its own balance.\nAmounts"
        " are always nonnegative integers.\nSpending zero succeeds, even for an emp"
        "ty wallet."
    ),
    "named-states": (
        "Import `Enum` and define `Status(Enum)` with exactly three members in this"
        ' order: `TODO = "todo"`, `DOING = "doing"`, and `DONE = "done"`.\nDefine `'
        "next_status(status)` returning the next enum member: TODO becomes DOING, D"
        "OING becomes DONE, and DONE stays DONE.\nThe argument is always a `Status`"
        " member; string conversion or invalid-input handling is not required in th"
        "is function.\nReturn enum members, not their string values, and do not pri"
        "nt."
    ),
    "tests-for-your-code": (
        "Define `clamp(value, low, high)` that returns `low` below the lower bounda"
        "ry, `high` above the upper boundary, and the original value otherwise.\nAs"
        "sume `low <= high`.\nAlso define a `unittest.TestCase` subclass named `Cla"
        "mpTests` with at least three test methods: `test_below`, `test_inside`, an"
        "d `test_above`.\nEach must call `clamp` and assert its expected result.\nU"
        "se distinct cases that would detect a clamp implementation always returnin"
        "g the lower bound, the original value, or the upper bound.\nDo not call `u"
        "nittest.main()` outside a function or class definition because Check manag"
        "es the test run."
    ),
    "object-principles": (
        "In `lesson.py`, define three classes and one function.\n"
        "`Ticket(price)` raises `ValueError` when `price` is negative and otherwise keeps the "
        "price inside the object; a price of 0 is allowed.\n"
        "`Ticket.cost()` returns the price, and `Ticket.label()` returns `Ticket: COST` using "
        "the result of `cost()`.\n"
        "`ChildTicket(price)` is a subclass of `Ticket` that overrides `cost()` to return half "
        "the price, rounded down with `//`.\n"
        "`ChildTicket` inherits `label()` unchanged, so `ChildTicket(9).label()` is `Ticket: "
        "4`.\n"
        "`GroupTicket(price, people)` is a subclass of `Ticket` whose `__init__()` calls "
        "`super().__init__(price)`, so a negative price still raises `ValueError`.\n"
        "`GroupTicket` also raises `ValueError` when `people` is less than 1.\n"
        "`GroupTicket` overrides `cost()` to return the price multiplied by `people`, and "
        "`label()` to return `Group of PEOPLE: COST`, such as `Group of 3: 15`.\n"
        "`total_cost(tickets)` returns the sum of `cost()` for every ticket in the list without "
        "checking which class each ticket is; an empty list costs 0.\n"
        "Printing is optional; checks create tickets and call your methods."
    ),
}

REPAIR_STAGES = {
    "your-own-modules": _stage(
        (
            "Repair a separate conversion module. Create conversions.py with hours_to_m"
            "inutes(hours, minutes=0) returning hours times 60 plus minutes, then impor"
            "t it in lesson.py under the same name. Both arguments are nonnegative inte"
            "gers; minutes defaults to zero. Both files must remain quiet when imported"
            "."
        ),
        "",
        "",
        (
            _check("One hour", "hours_to_minutes(1)", 60),
            _check("No hours", "hours_to_minutes(0)", 0),
            _check("Several hours", "__import__('conversions').hours_to_minutes(7)", 420),
            _check("Extra minutes", "hours_to_minutes(2, minutes=15)", 135),
            _check("Only minutes", "hours_to_minutes(0, 20)", 20),
            _check("Imports are quiet", "__stdout__", ""),
        ),
        (
            "Put the function definition in conversions.py.",
            "Import it from lesson.py without calling it at module load time.",
        ),
        files=("lesson.py", "conversions.py"),
        starter_files={
            "lesson.py": "from conversions import hours_to_minutes\n",
            "conversions.py": code("""
                def hours_to_minutes(hours, minutes=0):
                    return (hours + minutes) * 60
            """),
        },
        reference_files={
            "lesson.py": "from conversions import hours_to_minutes\n",
            "conversions.py": code("""
                def hours_to_minutes(hours, minutes=0):
                    return hours * 60 + minutes
            """),
        },
    ),
    "numeric-tools": _stage(
        (
            "Repair a separate score summary. score_summary(values) must return (minimu"
            "m, maximum, mean) for a nonempty list of numbers without changing it. A on"
            "e-value list has the same minimum, maximum, and mean."
        ),
        """
        from statistics import mean

        def score_summary(values):
            return min(values), max(values), mean(values)
        """,
        """
        from statistics import mean

        def score_summary(values):
            return max(values), min(values), mean(values)
        """,
        (
            _check("Mixed values", "score_summary([9, 1, 5, 3])", (1, 9, 4.5)),
            _check("Repeated values", "score_summary([2, 2, 8])", (2, 8, 4)),
            _check("Negative values", "score_summary([-3, 0, 6])", (-3, 6, 1)),
            _check("One value", "score_summary([7])", (7, 7, 7)),
            _check("Input unchanged", "(lambda x: (score_summary(x), x)[1])([9, 1, 5])", [9, 1, 5]),
        ),
        (
            "min and max each inspect the whole collection.",
            "The order of the returned tuple is minimum, maximum, then mean.",
        ),
    ),
    "repeatable-randomness": _stage(
        (
            "Repair a separate seeded picker. pick_sequence(items, count, seed) must us"
            "e a fresh Random(seed) for each call and return count choices in order. Re"
            "peated calls with the same inputs must match, and shared random state must"
            " remain unchanged. count and seed are integers. Reject negative counts or "
            "a positive count with empty items using ValueError. Zero draws return []; "
            "leave items unchanged."
        ),
        """
        import random

        def pick_sequence(items, count, seed):
            if count < 0 or (count and not items):
                raise ValueError("invalid draw")
            generator = random.Random(seed)
            return [generator.choice(items) for _ in range(count)]
        """,
        """
        import random

        def pick_sequence(items, count, seed):
            if count < 0 or (count and not items):
                raise ValueError("invalid draw")
            random.seed(seed)
            return [random.choice(items) for _ in range(count)]
        """,
        (
            _check(
                "Seeded sequence",
                "pick_sequence(['red', 'blue', 'green'], 4, 7)",
                ["blue", "red", "blue", "green"],
            ),
            _check(
                "Repeat call",
                (
                    "pick_sequence(['red', 'blue', 'green'], 4, 7) == pick_sequence(['red', "
                    "'blue', 'green'], 4, 7)"
                ),
                True,
            ),
            _check(
                "Shared state unchanged",
                (
                    "(lambda module: (module.seed(123), (lambda before: (pick_sequence(['red'],"
                    " 1, 7), module.getstate() == before)[1])(module.getstate())))(__import__('"
                    "random'))"
                ),
                (None, True),
            ),
            _check("Zero draws", "pick_sequence([], 0, 7)", []),
            _check(
                ("Negative count"),
                ("__raises_value_error__(lambda args: pick_sequence(*args), (['a'], -1, 7))"),
                True,
            ),
            _check(
                ("Empty choices"),
                ("__raises_value_error__(lambda args: pick_sequence(*args), ([], 1, 7))"),
                True,
            ),
            _check(
                ("Input unchanged"),
                ("(lambda x: (pick_sequence(x, 4, 7), x)[1])(['b', 'a'])"),
                [("b"), ("a")],
            ),
        ),
        (
            "Create random.Random(seed), not a shared seeded generator.",
            "Call choice once for each requested draw.",
        ),
    ),
    "command-line-options": _stage(
        (
            "Repair a separate command-line parser. make_tool_parser() must require a p"
            "ositional path and provide an integer --limit option defaulting to 10. Ret"
            "urn the parser without parsing arguments in the function."
        ),
        """
        import argparse

        def make_tool_parser():
            parser = argparse.ArgumentParser()
            parser.add_argument("path")
            parser.add_argument("--limit", type=int, default=10)
            return parser
        """,
        """
        import argparse

        def make_tool_parser():
            parser = argparse.ArgumentParser()
            parser.add_argument("path")
            parser.add_argument("--limit", default="0")
            return parser
        """,
        (
            _check(
                "Default",
                "vars(make_tool_parser().parse_args(['notes']))",
                {"path": "notes", "limit": 10},
            ),
            _check(
                "Explicit integer",
                "vars(make_tool_parser().parse_args(['notes', '--limit', '3']))",
                {"path": "notes", "limit": 3},
            ),
            _scenario_check(
                "Invalid arguments",
                """
                import contextlib
                import io

                result = []
                for args in ([], ["notes", "--limit", "many"]):
                    with contextlib.redirect_stderr(io.StringIO()):
                        try:
                            make_tool_parser().parse_args(args)
                        except SystemExit as error:
                            result.append(error.code)
                        else:
                            result.append(None)
                """,
                [2, 2],
                description=(
                    "Parsing must reject a missing path and a non-integer --limit with "
                    "argparse's usage error. "
                ),
                nudge=("Keep the path required and use type=int on the optional limit. "),
            ),
        ),
        ("Add the positional path first.", "Use type=int and default=10 for --limit."),
    ),
    "your-first-class": _stage(
        (
            "Repair a separate Ledger class. Ledger starts with balance zero, add(amoun"
            "t) returns the new balance, and withdraw(amount) returns True only when it"
            " can afford the amount. An unsuccessful withdrawal must not change balance"
            ". transfer_to(other, amount) moves money to another Ledger and returns Tru"
            "e only when affordable; otherwise return False and leave both balances unc"
            "hanged. Amounts are nonnegative integers; other is a different Ledger."
        ),
        """
        class Ledger:
            def __init__(self):
                self.balance = 0

            def add(self, amount):
                self.balance += amount
                return self.balance

            def withdraw(self, amount):
                if amount > self.balance:
                    return False
                self.balance -= amount
                return True

            def transfer_to(self, other, amount):
                if self.withdraw(amount):
                    other.add(amount)
                    return True
                return False
        """,
        """
        class Ledger:
            def __init__(self):
                self.balance = 0

            def add(self, amount):
                self.balance += amount
                return self.balance

            def withdraw(self, amount):
                self.balance -= amount
                return self.balance >= 0

            def transfer_to(self, other, amount):
                if self.withdraw(amount):
                    other.add(amount)
                    return True
                return False
        """,
        (
            _check(
                "Transfer and refusal",
                "(lambda a, b: [a.add(10), a.transfer_to(b, 4), a.transfer_to(b, 20), "
                "a.balance, b.balance])(Ledger(), Ledger())",
                [10, True, False, 6, 4],
                description="Transfer 4 from a ledger holding 10, then refuse 20; "
                "balances remain 6 and 4.",
            ),
            _check(
                "Successful and refused",
                (
                    "(lambda account: [account.add(8), account.withdraw(3), "
                    "account.withdraw(10), account.balance])(Ledger())"
                ),
                [8, True, False, 5],
            ),
            _check(
                "Independent ledgers",
                "(lambda a, b: (a.add(5), b.balance)[1])(Ledger(), Ledger())",
                0,
            ),
            _check(
                "Exact withdrawal",
                "(lambda account: [account.add(6), account.withdraw(6), "
                "account.balance])(Ledger())",
                [6, True, 0],
            ),
            _check(
                ("Zero withdrawal"), ("(lambda x: [x.withdraw(0), x.balance])(Ledger())"), [True, 0]
            ),
        ),
        (
            "Check affordability before subtracting.",
            "A failed withdrawal returns False and leaves the balance unchanged.",
        ),
    ),
    "named-states": _stage(
        (
            'Repair a separate Priority enum. Define Priority with LOW = "low", MEDIUM '
            '= "medium", and HIGH = "high", in that order, and raise_priority(priority)'
            " so LOW becomes MEDIUM, MEDIUM becomes HIGH, and HIGH stays HIGH."
        ),
        """
        from enum import Enum

        class Priority(Enum):
            LOW = "low"
            MEDIUM = "medium"
            HIGH = "high"

        def raise_priority(priority):
            if priority is Priority.LOW:
                return Priority.MEDIUM
            if priority is Priority.MEDIUM:
                return Priority.HIGH
            return Priority.HIGH
        """,
        """
        from enum import Enum

        class Priority(Enum):
            LOW = "low"
            MEDIUM = "medium"
            HIGH = "high"

        def raise_priority(priority):
            if priority is Priority.LOW:
                return Priority.MEDIUM
            return Priority.LOW
        """,
        (
            _check(
                "Members",
                "[(item.name, item.value) for item in Priority]",
                [("LOW", "low"), ("MEDIUM", "medium"), ("HIGH", "high")],
            ),
            _check("Raise low", "raise_priority(Priority.LOW) is Priority.MEDIUM", True),
            _check("Raise medium", "raise_priority(Priority.MEDIUM) is Priority.HIGH", True),
            _check("High is final", "raise_priority(Priority.HIGH) is Priority.HIGH", True),
        ),
        (
            "Give the three members their fixed string values.",
            "Handle LOW, MEDIUM, and HIGH separately so the final state does not go backward.",
        ),
    ),
    "tests-for-your-code": _stage(
        (
            "Repair the range validator and its tests. between(value, low, high) return"
            "s a boolean: True inside the inclusive range, False outside. Assume low <="
            " high. Keep RangeTests as a unittest.TestCase with test_below, test_inside"
            ", and test_above. Add boundary tests that would catch a function accepting"
            " or rejecting everything. Check runs your tests; do not call unittest.main"
            "()."
        ),
        """
        import unittest

        def between(value, low, high):
            return low <= value <= high

        class RangeTests(unittest.TestCase):
            def test_below(self):
                self.assertEqual(between(-2, 0, 10), False)

            def test_inside(self):
                self.assertEqual(between(5, 0, 10), True)

            def test_above(self):
                self.assertEqual(between(12, 0, 10), False)

            def test_boundaries(self):
                self.assertEqual(between(0, 0, 10), True)
                self.assertEqual(between(10, 0, 10), True)
        """,
        """
        import unittest

        def between(value, low, high):
            return low < value < high

        class RangeTests(unittest.TestCase):
            def test_below(self):
                self.assertEqual(between(-2, 0, 10), False)

            def test_inside(self):
                self.assertEqual(between(5, 0, 10), True)

            def test_above(self):
                self.assertEqual(between(12, 0, 10), False)
        """,
        (
            _check("Below", "between(-2, 0, 10) is False", True),
            _check("Inside", "between(5, 0, 10) is True", True),
            _check("Above", "between(12, 0, 10) is False", True),
            _check("Inclusive lower bound", "between(0, 0, 10) is True", True),
            _check("Inclusive upper bound", "between(10, 0, 10) is True", True),
            _check("Equal boundaries", "between(4, 4, 4) is True", True),
            _check(
                "Tests pass",
                (
                    "(lambda result: [result.testsRun >= 3, result.wasSuccessful()])(__import__"
                    "('unittest').defaultTestLoader.loadTestsFromTestCase(RangeTests).run(__imp"
                    "ort__('unittest').TestResult()))"
                ),
                [True, True],
                description="Run RangeTests: at least three tests must pass.",
            ),
            _check(
                ("Named cases"),
                ("{'test_below', 'test_inside', 'test_above'} <= set(dir(RangeTests))"),
                True,
            ),
            *tuple(
                _check(
                    "Tests reject " + label,
                    "(RangeTests.test_inside.__globals__.__setitem__('between', "
                    f"lambda value, low, high: {stub}), "
                    "__import__('unittest').defaultTestLoader.loadTestsFromTestCase(RangeTests)"
                    ".run(__import__('unittest').TestResult()).wasSuccessful())[1]",
                    False,
                    nudge=("Include an assertion whose expected result differs from this defect."),
                    description="Run your tests with between replaced by " + label + ".",
                )
                for label, stub in (
                    ("always True", "True"),
                    ("always False", "False"),
                    ("exclusive lower bound", "low < value <= high"),
                    ("exclusive upper bound", "low <= value < high"),
                )
            ),
        ),
        (
            "The supplied tests miss values exactly on the boundary. Add those cases first.",
            "An inclusive range includes low and high: compare with <= at both ends.",
        ),
    ),
    "object-principles": _stage(
        (
            "Repair the shape classes in `lesson.py`.\n"
            "`Shape(name)` stores `name`, and its `describe()` returns `NAME: AREA` using "
            "`area()`.\n"
            "`Shape.area()` is an abstract method that raises `NotImplementedError`.\n"
            "`Rectangle(width, height)` is a subclass of `Shape` named `Rectangle`, whose area "
            "is width multiplied by height.\n"
            "`Square(side)` is a subclass of `Rectangle` with equal sides, named `Square`.\n"
            "`total_area(shapes)` returns the sum of every shape's area, and 0 for an empty "
            "list.\n"
            "Keep the family tree: `Square` inherits from `Rectangle`, which inherits from "
            "`Shape`."
        ),
        """
        class Shape:
            def __init__(self, name):
                self.name = name

            def area(self):
                raise NotImplementedError("Each shape must define area()")

            def describe(self):
                return f"{self.name}: {self.area()}"


        class Rectangle(Shape):
            def __init__(self, width, height):
                super().__init__("Rectangle")
                self.width = width
                self.height = height

            def area(self):
                return self.width * self.height


        class Square(Rectangle):
            def __init__(self, side):
                super().__init__(side, side)
                self.name = "Square"


        def total_area(shapes):
            total = 0
            for shape in shapes:
                total = total + shape.area()
            return total
        """,
        """
        class Shape:
            def __init__(self, name):
                self.name = name

            def area(self):
                raise NotImplementedError("Each shape must define area()")

            def describe(self):
                return f"{self.name}: {self.area()}"


        class Rectangle(Shape):
            def __init__(self, width, height):
                super().__init__("Rectangle")
                self.width = width
                self.height = height

            def area_of(self):
                return self.width * self.height


        class Square(Rectangle):
            def __init__(self, side):
                self.side = side
                self.name = "Square"


        def total_area(shapes):
            total = 0
            for shape in shapes:
                total = total + shape.area()
            return total
        """,
        (
            _check(
                "A rectangle's area",
                "[Rectangle(2, 3).area(), Rectangle(2, 3).describe()]",
                [6, "Rectangle: 6"],
                nudge="An override must use exactly the parent's method name.",
            ),
            _check(
                "A square reuses Rectangle",
                "[Square(4).area(), Square(4).describe()]",
                [16, "Square: 16"],
                nudge="Square's __init__ must let Rectangle set up width and height.",
            ),
            _check(
                "The family tree is unchanged",
                "[issubclass(Square, Rectangle), issubclass(Rectangle, Shape)]",
                [True, True],
            ),
            _check(
                "Total of mixed shapes",
                "[total_area([Rectangle(1, 2), Square(3)]), total_area([])]",
                [11, 0],
            ),
            _scenario_check(
                "A plain Shape stays abstract",
                """
                try:
                    Shape("blob").area()
                    result = "no error"
                except NotImplementedError:
                    result = "NotImplementedError"
                """,
                "NotImplementedError",
                description="Shape('blob').area() raises NotImplementedError",
                nudge="Leave Shape.area() abstract; each subclass provides its own area().",
            ),
        ),
        (
            "Run Rectangle(2, 3).area() and read which class's area() raised the error.",
            "Compare the method names in Shape and Rectangle, then compare Square's __init__ "
            "with Rectangle's.",
            "super().__init__(side, side) lets Rectangle store both sides.",
        ),
    ),
}
