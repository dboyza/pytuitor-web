"""Focused collection and standard-library lessons inserted into the beginner path."""

from pytuitor_web.beginner_authoring import _check as _stage_check
from pytuitor_web.beginner_authoring import _scenario_check
from pytuitor_web.models import Check, Lesson, code, lesson_text


def _check(label, expression, expected, stdin=None):
    return Check(
        label,
        expression,
        expected,
        "Compare the actual and expected results for this input.",
        stdin=stdin,
    )


def _lesson(identifier, title, chapter, subtitle, solution, repair, checks, hints, stdin=""):
    return Lesson(
        id=identifier,
        track="beginner",
        title=title,
        subtitle=subtitle,
        minutes=20,
        concepts=(title,),
        body=lesson_text(identifier),
        repair=code(repair),
        checks=tuple(checks),
        hints=tuple(hints),
        prediction="",
        choices=(),
        answer=0,
        explanation="",
        solution=code(solution),
        chapter_id=chapter,
        stdin=stdin,
    )


# Anchors keep the order explicit without relying on a fixed chapter length.
INSERT_AFTER = {
    "list-positions": "summary-builtins",
    "tuples-and-sets": "comparing-sets",
    "loop-helpers": "nested-collections",
    "word-counts": "dictionary-pairs",
    "dictionary-pairs": "editing-collections",
    "dates-and-deadlines": "date-time-formats",
    "your-own-modules": "numeric-tools",
    "numeric-tools": "repeatable-randomness",
    "your-first-class": "object-principles",
}


SUMMARY_CHECKS = (
    _stage_check(
        "Mixed scores",
        "[scores, total, highest, lowest, passes, anyone_passed, everyone_passed]",
        [[64, 88, 20], 172, 88, 20, [True, True, False], True, False],
        stdin="64 88 20\n",
        output="Total: 172\nHighest: 88\nLowest: 20\nAnyone passed: True\nEveryone passed: False",
        nudge="sum, max, and min summarize the list; any and all read the list of booleans.",
    ),
    _stage_check(
        "Exactly 50 passes",
        "[passes, anyone_passed, everyone_passed]",
        [[True, True], True, True],
        stdin="50 100\n",
        nudge="A score of 50 or more passes, so compare with >= 50.",
    ),
    _stage_check(
        "One failing score",
        "[total, highest, lowest, passes, anyone_passed, everyone_passed]",
        [12, 12, 12, [False], False, False],
        stdin="12\n",
        nudge="With one score, it is both the highest and the lowest.",
    ),
    _stage_check(
        "Zero and negative scores",
        "[total, highest, lowest]",
        [-5, 0, -5],
        stdin="0 -5\n",
        nudge="max and min compare the numbers themselves, including negatives.",
    ),
    _stage_check(
        "No scores",
        "[scores, total, passes, anyone_passed, everyone_passed, "
        "__stdout__.split()[-2:], 'Total' in __stdout__]",
        [[], 0, [], False, True, ["No", "scores"], False],
        stdin="\n",
        nudge="Check len(scores) before max and min; all([]) is True and any([]) is False.",
    ),
)

PAIRS_CHECKS = (
    _stage_check(
        "Repeated supply adds up",
        "[list(stock.items()), total, low]",
        [[["rope", 6], ["lamp", 5]], 11, []],
        stdin="rope lamp rope\n2 5 4\n",
        output="rope: 6\nlamp: 5\nTotal: 11",
        nudge="Add a repeated name's amount with get(), then print each pair from items().",
    ),
    _stage_check(
        "Low supplies keep their order",
        "[list(stock.items()), total, low]",
        [[["map", 1], ["rope", 7], ["flare", 2]], 10, ["map", "flare"]],
        stdin="map rope flare\n1 7 2\n",
        output="map: 1\nrope: 7\nflare: 2\nTotal: 10",
        nudge="Collect names whose amount is below 3 while looping over stock.items().",
    ),
    _stage_check(
        "Extra amounts are ignored",
        "[list(stock.items()), total, low]",
        [[["tea", 4]], 4, []],
        stdin="tea\n4 9\n",
        output="tea: 4\nTotal: 4",
        nudge="zip stops at the shorter line, so the unpaired amount is ignored.",
    ),
    _stage_check(
        "Zero is low",
        "[list(stock.items()), total, low]",
        [[["salt", 0]], 0, ["salt"]],
        stdin="salt\n0\n",
        nudge="An amount of 0 is below 3.",
    ),
    _stage_check(
        "Nothing stored",
        "[list(stock.items()), total, low, __stdout__.split()[-2:]]",
        [[], 0, [], ["Total:", "0"]],
        stdin="\n\n",
        nudge="An empty dictionary has no pairs to print; its values still sum to 0.",
    ),
)

_SUBCLASS_NUDGE = "Override cost() in each subclass and let label() call self.cost()."
PRINCIPLES_CHECKS = (
    _stage_check(
        "A plain ticket",
        "[Ticket(10).cost(), Ticket(10).label()]",
        [10, "Ticket: 10"],
        nudge="Ticket keeps its price; label() uses cost().",
    ),
    _stage_check(
        "A child ticket overrides cost",
        "[ChildTicket(9).cost(), ChildTicket(9).label()]",
        [4, "Ticket: 4"],
        nudge="ChildTicket overrides cost() with // 2 and inherits label() unchanged.",
    ),
    _stage_check(
        "A group overrides cost and label",
        "[GroupTicket(5, 3).cost(), GroupTicket(5, 3).label()]",
        [15, "Group of 3: 15"],
        nudge=_SUBCLASS_NUDGE,
    ),
    _stage_check(
        "Subclasses are tickets",
        "[issubclass(ChildTicket, Ticket), issubclass(GroupTicket, Ticket), "
        "isinstance(GroupTicket(1, 1), Ticket)]",
        [True, True, True],
        nudge="Write the parent in parentheses: class ChildTicket(Ticket):",
    ),
    _stage_check(
        "Free tickets are allowed",
        "[Ticket(0).cost(), ChildTicket(0).cost(), GroupTicket(0, 4).cost()]",
        [0, 0, 0],
        nudge="Only negative prices are rejected.",
    ),
    _stage_check(
        "Invalid tickets are rejected",
        "[__raises_value_error__(Ticket, -1), __raises_value_error__(ChildTicket, -2), "
        "__raises_value_error__(lambda price: GroupTicket(price, 2), -5), "
        "__raises_value_error__(lambda people: GroupTicket(5, people), 0)]",
        [True, True, True, True],
        nudge="GroupTicket reuses Ticket's price rule by calling super().__init__(price).",
        description="Ticket(-1), ChildTicket(-2), GroupTicket(-5, 2), and GroupTicket(5, 0) "
        "each raise ValueError",
    ),
    _stage_check(
        "Each ticket keeps its own price",
        "[Ticket(3).cost(), Ticket(8).cost()]",
        [3, 8],
        nudge="Store the price on self so each object has its own.",
    ),
    _stage_check(
        "One total for every kind of ticket",
        "[total_cost([Ticket(10), ChildTicket(10), GroupTicket(4, 2)]), total_cost([])]",
        [23, 0],
        nudge="Add ticket.cost() for each ticket; an empty list costs 0.",
    ),
    _scenario_check(
        "The total works for any object with cost()",
        """
        class Voucher:
            def cost(self):
                return 2


        result = total_cost([Voucher(), Ticket(1)])
        """,
        3,
        description="total_cost([Voucher(), Ticket(1)]) where Voucher is not a Ticket but "
        "has cost() returning 2",
        nudge="Polymorphism: call cost() on each object instead of checking its class.",
    ),
)

LESSONS = (
    _lesson(
        "comparing-sets",
        "Comparing sets",
        "b-collections",
        "Find shared, missing, and combined values",
        """
        required = set(input("Required: ").split())
        available = set(input("Available: ").split())
        shared = required & available
        missing = required - available
        combined = required | available
        exclusive = required ^ available
        ready = required <= available
        """,
        "",
        [
            _check(
                label,
                "[sorted(shared), sorted(missing), sorted(combined), sorted(exclusive), ready]",
                [
                    sorted(set(a.split()) & set(b.split())),
                    sorted(set(a.split()) - set(b.split())),
                    sorted(set(a.split()) | set(b.split())),
                    sorted(set(a.split()) ^ set(b.split())),
                    set(a.split()) <= set(b.split()),
                ],
                a + "\n" + b + "\n",
            )
            for label, a, b in (
                ("Partial overlap", "rope lamp", "lamp food"),
                ("Equal sets", "rope lamp rope", "lamp rope"),
                ("Empty requirements", "", "lamp"),
                ("Nothing available", "rope", ""),
                ("Both empty", "", ""),
                ("Case-sensitive groups", "Ada ada", "ada"),
            )
        ],
        [
            "& finds shared values; | combines them; ^ finds values present in only one set.",
            "required - available keeps the missing requirements; <= includes equality.",
        ],
        "rope lamp\nlamp food\n",
    ),
    _lesson(
        "nested-collections",
        "Working with nested lists",
        "b-collections",
        "Traverse rows and columns without losing empty rows",
        """
        count = int(input("Rows: "))
        grid = []
        for number in range(count):
            row = []
            for word in input("Row: ").split():
                row.append(int(word))
            grid.append(row)
        row_totals = []
        flat = []
        positions = []
        for r, row in enumerate(grid):
            total = 0
            for c, value in enumerate(row):
                total += value
                flat.append(value)
                positions.append((r, c, value))
            row_totals.append(total)
        """,
        "",
        [
            _check(
                label,
                "[grid, row_totals, flat, [list(item) for item in positions]]",
                [
                    grid,
                    [sum(row) for row in grid],
                    [v for row in grid for v in row],
                    [[r, c, v] for r, row in enumerate(grid) for c, v in enumerate(row)],
                ],
                str(len(grid)) + "\n" + "".join(" ".join(map(str, row)) + "\n" for row in grid),
            )
            for label, grid in (
                ("Unequal rows", [[2, 3], [4]]),
                ("Empty middle row", [[-2], [], [5, 5]]),
                ("No rows", []),
                ("Only empty rows", [[], []]),
            )
        ],
        [
            "Build one new row list per input line, then append that row to grid.",
            "Reset the total for each row; enumerate supplies row and column positions.",
        ],
        "2\n2 3\n4\n",
    ),
    _lesson(
        "editing-collections",
        "Editing lists and dictionaries",
        "b-collections",
        "Insert, remove, sort, and delete deliberately",
        """
        items = input("Items: ").split()
        target = input("Remove: ")
        incoming = input("Add: ")
        if target in items:
            items.remove(target)
        items.insert(0, incoming)
        items.sort()
        counts = {}
        for item in items:
            counts[item] = counts.get(item, 0) + 1
        removed = counts.pop(target, 0)
        keys = sorted(counts.keys())
        """,
        "",
        [
            _check(
                "Remove only the first occurrence",
                "[items, counts, removed, keys]",
                [["apple", "pear", "pear"], {"apple": 1}, 2, ["apple"]],
                "pear apple pear\npear\npear\n",
            ),
            _check(
                "Absent target",
                "[items, counts, removed, keys]",
                [["apple", "pear"], {"apple": 1, "pear": 1}, 0, ["apple", "pear"]],
                "pear\nplum\napple\n",
            ),
            _check(
                "Start empty",
                "[items, counts, removed, keys]",
                [["z"], {"z": 1}, 0, ["z"]],
                "\na\nz\n",
            ),
            _check(
                "Repeated other items",
                "[items, counts, removed, keys]",
                [["a", "b", "b"], {"b": 2}, 1, ["b"]],
                "b b a\na\na\n",
            ),
        ],
        [
            "list.remove deletes the first match; check if target in items before removing it.",
            "sort changes the list; dict.pop(key, 0) removes a key with a safe default.",
        ],
        "pear apple pear\npear\npear\n",
    ),
    _lesson(
        "date-time-formats",
        "Parsing dates and times",
        "b-automation",
        "Combine calendar dates, clock times, and explicit formats",
        """
        from datetime import datetime, timedelta
        def appointment(day, clock, minutes):
            start = datetime.combine(datetime.strptime(day, "%d/%m/%Y").date(),
                                     datetime.strptime(clock, "%H:%M").time())
            end = start + timedelta(minutes=minutes)
            return end.strftime("%Y-%m-%d %H:%M")
        """,
        "",
        [
            _check("Cross midnight", "appointment('31/12/2024', '23:50', 20)", "2025-01-01 00:10"),
            _check(
                "Day precedes month", "appointment('03/04/2024', '09:00', 0)", "2024-04-03 09:00"
            ),
            _check("Leap day", "appointment('28/02/2024', '23:30', 60)", "2024-02-29 00:30"),
            _check("Move backwards", "appointment('01/03/2024', '00:10', -20)", "2024-02-29 23:50"),
            _check(
                "Reject invalid clock",
                "[__raises_value_error__(lambda clock: appointment('01/01/2024', clock, 0), bad) "
                "for bad in ('24:00', '09:60')]",
                [True, True],
            ),
            _check(
                "Reject invalid date",
                "__raises_value_error__(lambda args: appointment(*args), "
                "('31/02/2024', '09:00', 5))",
                True,
            ),
        ],
        [
            "strptime parses with a format; strftime produces formatted text.",
            "Combine date and time before adding timedelta(minutes=minutes).",
        ],
    ),
    _lesson(
        "numeric-tools",
        "Math and statistical summaries",
        "b-tools",
        "Use library calculations and distinguish mean from median",
        """
        import math
        import statistics
        def summarize(values, capacity):
            if capacity <= 0 or not values:
                raise ValueError("Need data and positive capacity")
            return (statistics.mean(values), statistics.median(values),
                    math.ceil(len(values) / capacity))
        """,
        "",
        [
            _check("Unsorted even sample", "list(summarize([9, 1, 5, 3], 3))", [4.5, 4.0, 2]),
            _check("Negative and positive", "list(summarize([-2, 0, 5], 2))", [1.0, 0, 2]),
            _check("One value", "list(summarize([7], 1))", [7, 7, 1]),
            _check(
                "No data", "__raises_value_error__(lambda args: summarize(*args), ([], 2))", True
            ),
            _check(
                "Invalid capacity",
                "__raises_value_error__(lambda args: summarize(*args), ([1], 0))",
                True,
            ),
            _check(
                "Negative capacity",
                "__raises_value_error__(lambda args: summarize(*args), ([1], -2))",
                True,
            ),
            _check("Fractional data", "list(summarize([1.5, -0.5, 3.0, 2.0], 3))", [1.5, 1.75, 2]),
            _check(
                "Input is untouched", "(lambda xs: (summarize(xs, 2), xs)[1])([8, 1, 4])", [8, 1, 4]
            ),
        ],
        [
            "statistics.mean averages; statistics.median finds the middle of the ordered data.",
            "math.ceil rounds up, so a partly filled final group still counts.",
        ],
    ),
    _lesson(
        "repeatable-randomness",
        "Repeatable random choices",
        "b-tools",
        "Repeat random choices without affecting other code",
        """
        import random
        def draw(items, count, seed):
            if count < 0 or (count > 0 and not items):
                raise ValueError("Invalid draw")
            rng = random.Random(seed)
            result = []
            for index in range(count):
                result.append(rng.choice(items))
            return result
        """,
        "",
        [
            _check(
                "Repeatable draws",
                "draw(['a', 'b', 'c'], 8, 12)",
                {
                    "expr": "(lambda rng: [rng.choice(['a', 'b', 'c']) for _ in range(8)])"
                    "(__import__('random').Random(12))"
                },
            ),
            _check(
                "Repeated calls restart independently",
                "[draw(['x', 'y', 'z'], 10, 4), draw(['x', 'y', 'z'], 10, 4)]",
                {
                    "expr": "(lambda values: [values, values])((lambda rng: "
                    "[rng.choice(['x', 'y', 'z']) for _ in range(10)])"
                    "(__import__('random').Random(4)))"
                },
            ),
            _check("Zero draws from empty input", "draw([], 0, 1)", []),
            _check(
                "Reject empty choices",
                "__raises_value_error__(lambda args: draw(*args), ([], 1, 1))",
                True,
            ),
            _check(
                "Reject negative count",
                "__raises_value_error__(lambda args: draw(*args), (['a'], -1, 1))",
                True,
            ),
            _check(
                "Shared random generator is unchanged",
                "(lambda before: (draw(['a', 'b'], 5, 9), "
                "__import__('random').getstate() == before)[1])(__import__('random').getstate())",
                True,
            ),
            _check(
                "Input remains unchanged",
                "(lambda xs: (draw(xs, 5, 3), xs)[1])(['b', 'a'])",
                ["b", "a"],
            ),
        ],
        [
            "Create random.Random(seed) inside each call for independent repeatable draws.",
            "Use that generator's choice method; random.seed would modify shared state.",
        ],
    ),
    _lesson(
        "summary-builtins",
        "Summarizing lists",
        "b-collections",
        "Use sum, max, min, any, and all on a whole list",
        """
        scores = []
        for word in input("Scores: ").split():
            scores.append(int(word))
        total = sum(scores)
        passes = []
        for score in scores:
            passes.append(score >= 50)
        anyone_passed = any(passes)
        everyone_passed = all(passes)
        if len(scores) == 0:
            print("No scores")
        else:
            highest = max(scores)
            lowest = min(scores)
            print(f"Total: {total}")
            print(f"Highest: {highest}")
            print(f"Lowest: {lowest}")
            print(f"Anyone passed: {anyone_passed}")
            print(f"Everyone passed: {everyone_passed}")
        """,
        "",
        SUMMARY_CHECKS,
        [
            "sum(), max(), and min() each take the whole list; check len(scores) before "
            "calling max() or min().",
            "Build passes with a loop that appends score >= 50, then give that list to any() "
            "and all().",
        ],
        "64 88 20\n",
    ),
    _lesson(
        "dictionary-pairs",
        "Looping over dictionary pairs",
        "b-collections",
        "Visit keys and values together with items()",
        """
        names = input("Supplies: ").split()
        amounts = input("Amounts: ").split()
        stock = {}
        for name, amount in zip(names, amounts):
            stock[name] = stock.get(name, 0) + int(amount)
        low = []
        for name, amount in stock.items():
            print(f"{name}: {amount}")
            if amount < 3:
                low.append(name)
        total = sum(stock.values())
        print(f"Total: {total}")
        """,
        "",
        PAIRS_CHECKS,
        [
            "Build stock first, then loop over stock.items() to receive each name and amount.",
            "sum(stock.values()) adds the amounts; compare each amount with 3 to fill low.",
        ],
        "rope lamp rope\n2 5 4\n",
    ),
    _lesson(
        "object-principles",
        "Inheritance and polymorphism",
        "b-tools",
        "Encapsulation, abstraction, inheritance, and polymorphism",
        """
        class Ticket:
            def __init__(self, price):
                if price < 0:
                    raise ValueError("Price cannot be negative")
                self._price = price

            def cost(self):
                return self._price

            def label(self):
                return f"Ticket: {self.cost()}"


        class ChildTicket(Ticket):
            def cost(self):
                return self._price // 2


        class GroupTicket(Ticket):
            def __init__(self, price, people):
                super().__init__(price)
                if people < 1:
                    raise ValueError("A group needs at least one person")
                self._people = people

            def cost(self):
                return self._price * self._people

            def label(self):
                return f"Group of {self._people}: {self.cost()}"


        def total_cost(tickets):
            total = 0
            for ticket in tickets:
                total = total + ticket.cost()
            return total
        """,
        "",
        PRINCIPLES_CHECKS,
        [
            "Write Ticket first; ChildTicket can then override only cost().",
            "In GroupTicket.__init__, call super().__init__(price) before checking people.",
            "total_cost adds ticket.cost() for each ticket; each object runs its own version.",
        ],
    ),
)
