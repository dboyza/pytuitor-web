"""Build and Repair contracts for python-design."""

from pytuitor_web.experienced_authoring import (
    _check,
    _exec,
    _probe,
    _repair,
    check,
    legacy,
    probe,
    unit,
)

LESSONS = (
    legacy("ready-to-ship", "python-design"),
    unit(
        "data-models",
        "python-design",
        "Model a small value object",
        "Classes & dataclasses",
        """
        from dataclasses import dataclass

        @dataclass(frozen=True)
        class Item:
            name: str
            quantity: int

            def restock(self, amount):
                if amount < 0:
                    raise ValueError("Amount must be nonnegative")
                return Item(self.name, self.quantity + amount)
        """,
        [
            check(
                "Restock a value",
                "(lambda item: (item.name, item.quantity))(Item('bolts', 2).restock(3))",
                ["bolts", 5],
            ),
            check(
                "Original is unchanged",
                "(lambda item: (item.restock(2), item.quantity)[1])(Item('nuts', 4))",
                4,
            ),
            check("Value equality", "Item('bolts', 2) == Item('bolts', 2)", True),
            check("Negative restock", "__raises_value_error__(Item('x', 1).restock, -1)", True),
        ],
        [
            "A dataclass can generate initialization and equality from annotated fields.",
            "Construct a new Item in restock rather than updating self.",
        ],
    ),
    unit(
        "dataclass-lifecycle",
        "python-design",
        "Dataclass defaults and updates",
        "Dataclass factories & post-init",
        """
        from dataclasses import dataclass, field, replace

        @dataclass
        class Batch:
            name: str
            tags: list[str] = field(default_factory=list)
            def __post_init__(self):
                self.name = self.name.strip()
                if not self.name:
                    raise ValueError("Empty name")
            def renamed(self, name):
                return replace(self, name=name, tags=self.tags.copy())
        """,
        [
            check("Normalize name", "Batch('  parts ').name", "parts"),
            check("Reject blank", "__raises_value_error__(Batch, '  ')", True),
            check(
                "Separate defaults",
                (
                    "(exec(\"a = Batch('a')\\nb = Batch('b')\\na.tags.append('hot')\\"
                    'nresult = b.tags", globals()), result)[1]'
                ),
                [],
            ),
            check(
                "Copy on rename",
                (
                    "(exec(\"a = Batch('old', ['x'])\\nb = a.renamed(' new ')\\nb.tags.app"
                    "end('y')\\nresult = [a.name, a.tags, b.name, b.tags, a is b]\", globals()"
                    "), result)[1]"
                ),
                ["old", ["x"], "new", ["x", "y"], False],
            ),
            check("Validate rename", "__raises_value_error__(Batch('old').renamed, '')", True),
            check("Dataclass values", "Batch('x', ['a']) == Batch('x', ['a'])", True),
        ],
        [
            (
                "Use field(default_factory=list) for independent defaults and"
                " __post_init__ to normalize and validate."
            ),
            "replace is shallow: provide a copy of tags when constructing the renamed batch.",
        ],
    ),
    unit(
        "typed-contracts",
        "python-design",
        "Unions and generic contracts",
        "Union types & TypeVar generics",
        """
        from collections.abc import Iterable
        from typing import TypeVar

        T = TypeVar("T")

        def first_or(items: Iterable[T], default: T) -> T:
            return next(iter(items), default)

        def parse_optional(text: str | None) -> int | None:
            if text is None or not text.strip():
                return None
            return int(text)
        """,
        [
            check("Keep an item that tests as false", "first_or(iter([0, 2]), 9)", 0),
            check("Keep generic value", "first_or([{'a': 1}], {})", {"a": 1}),
            check("Empty uses default", "first_or(iter([]), 'fallback')", "fallback"),
            check(
                "Consume one only",
                (
                    "(exec('source = iter([1, 2])\\nfirst_or(source, 0)\\nresult = "
                    "next(source)', globals()), result)[1]"
                ),
                2,
            ),
            check(
                "Missing optional values",
                "[parse_optional(None), parse_optional('  ')]",
                [None, None],
            ),
            check("Signed integer", "parse_optional(' -4 ')", -4),
            check("Reject invalid input", "__raises_value_error__(parse_optional, '1.5')", True),
        ],
        [
            (
                "next(iter(items), default) returns the first item even if it tests as false, "
                "or default if there are no items. It reads at most one item."
            ),
            (
                "Handle None and blank text before int conversion; TypeVar re"
                "lates the iterable element and return types."
            ),
        ],
    ),
    unit(
        "practical-object-protocols",
        "python-design",
        "Objects that fit Python",
        "Properties & special methods",
        """
        class Score:
            def __init__(self, points):
                self.points = points
            @property
            def points(self):
                return self._points
            @points.setter
            def points(self, value):
                if value < 0:
                    raise ValueError("Negative points")
                self._points = value
            def __repr__(self):
                return f"Score({self.points})"
            def __len__(self):
                return self.points
            def __eq__(self, other):
                if not isinstance(other, Score):
                    return NotImplemented
                return self.points == other.points
            def __add__(self, other):
                if not isinstance(other, Score):
                    return NotImplemented
                return Score(self.points + other.points)
        """,
        [
            check("Readable representation", "repr(Score(3))", "Score(3)"),
            check(
                "Length and equality",
                "[len(Score(0)), Score(2) == Score(2), Score(2) == Score(3), Score(2) == 2]",
                [0, True, False, False],
            ),
            check(
                "Independent sum",
                (
                    "(exec('a = Score(2)\\nb = Score(3)\\nc = a + b\\nresult = [a.points, b.poi"
                    "nts, c.points, c is a, c is b]', globals()), result)[1]"
                ),
                [2, 3, 5, False, False],
            ),
            check("Reject negative creation", "__raises_value_error__(Score, -1)", True),
            check(
                "Reject assignment without mutation",
                (
                    "(exec('s = Score(4)\\ntry:\\n    s.points = -1\\nexcept ValueEr"
                    "ror:\\n    result = s.points', globals()), result)[1]"
                ),
                4,
            ),
            check(
                "Accept assignment",
                ("(exec('s = Score(1)\\ns.points = 0\\nresult = s.points', globals()), result)[1]"),
                0,
            ),
            check(
                "Unsupported addition",
                (
                    "(exec('try:\\n    Score(2) + 2\\nexcept TypeError:\\n    result"
                    " = True', globals()), result)[1]"
                ),
                True,
            ),
        ],
        [
            (
                "Validate before updating the backing attribute in the proper"
                "ty setter to preserve rejected updates."
            ),
            (
                "Return a new Score when adding and NotImplemented for unsupp"
                "orted operand types; compare point values."
            ),
        ],
    ),
    unit(
        "class-construction",
        "python-design",
        "Factories and abstract interfaces",
        "Class methods, static methods & ABCs",
        """
        from abc import ABC, abstractmethod

        class Renderer(ABC):
            @abstractmethod
            def render(self, text):
                pass

        class PrefixRenderer(Renderer):
            def __init__(self, prefix):
                self.prefix = prefix
            @staticmethod
            def valid_prefix(value):
                return bool(value.strip())
            @classmethod
            def from_text(cls, text):
                prefix = text.strip()
                if not cls.valid_prefix(prefix):
                    raise ValueError("Empty prefix")
                return cls(prefix)
            def render(self, text):
                return self.prefix + text
        """,
        [
            check(
                "Factory normalization",
                "PrefixRenderer.from_text(' > ').render('hello')",
                (">hello"),
            ),
            check(
                "Validation helper",
                '[PrefixRenderer.valid_prefix(" "), PrefixRenderer.valid_prefix("!")]',
                [False, True],
            ),
            check(
                "Reject blank factory",
                "__raises_value_error__(PrefixRenderer.from_text, ' ')",
                True,
            ),
            check(
                "Subclass factory",
                (
                    '(exec("class Special(PrefixRenderer):\\n    pass\\nobj = Special.from_text'
                    "(' ! ')\\nresult = [type(obj) is Special, obj.render('ok')]\", globals("
                    ")), result)[1]"
                ),
                [True, "!ok"],
            ),
            check(
                "Abstract base cannot instantiate",
                (
                    "(exec('try:\\n    Renderer()\\nexcept TypeError:\\n    result ="
                    " True', globals()), result)[1]"
                ),
                True,
            ),
            check(
                "Incomplete subclass cannot instantiate",
                (
                    "(exec('class Incomplete(Renderer):\\n    pass\\ntry:\\n    Incomplete()\\n"
                    "except TypeError:\\n    result = True', globals()), result)[1]"
                ),
                True,
            ),
        ],
        [
            (
                "Inherit from ABC and mark render with abstractmethod to prevent incomplete"
                " instances."
            ),
            (
                "The classmethod factory must construct cls, not a fixed "
                "class, after trimming and validating text."
            ),
        ],
    ),
    unit(
        "structural-typing",
        "python-design",
        "Program to a small protocol",
        "Structural typing & protocols",
        """
        from typing import Protocol

        class Writer(Protocol):
            def write(self, text: str) -> object: ...

        def emit_lines(writer: Writer, lines):
            count = 0
            for line in lines:
                writer.write(line + "\\n")
                count += 1
            return count
        """,
        [
            check(
                "StringIO writer",
                (
                    "(lambda w: (emit_lines(w, ['a', 'b']), w.getvalue()))(__import__('io"
                    "').StringIO())"
                ),
                [2, "a\nb\n"],
            ),
            check(
                "An unrelated writer",
                (
                    "(lambda events: (emit_lines(type('Sink', (), {'write': lambda self, text: "
                    "events.append(text)})(), iter(['x'])), events))([])"
                ),
                [1, ["x\n"]],
            ),
            check("Empty input", "emit_lines(__import__('io').StringIO(), [])", 0),
        ],
        [
            (
                "Use the write method promised by the protocol without inspecting the concr"
                "ete class."
            ),
            (
                "Count input lines, not the return value of write; different writers may "
                "return different values."
            ),
        ],
    ),
    unit(
        "test-doubles",
        "python-design",
        "Inject effects for reliable tests",
        "Dependency injection & mocking",
        """
        def retry(operation, attempts, pause):
            if attempts < 1:
                raise ValueError("Attempts must be positive")
            for attempt in range(attempts):
                try:
                    return operation()
                except ValueError:
                    if attempt == attempts - 1:
                        raise
                    pause()
        """,
        [
            check(
                "Recover and pause once",
                (
                    "(lambda op, pause: (retry(op, 3, pause), op.call_count, pause.call_count))"
                    "(__import__('unittest.mock', fromlist=['Mock']).Mock(side_effect=[ValueErr"
                    "or('busy'), 7]), __import__('unittest.mock', fromlist=['Mock']).Mock())"
                ),
                [7, 2, 1],
            ),
            check(
                "Final failure is raised",
                (
                    "__raises_value_error__(lambda _: retry(lambda: int('bad'), 2, lambda"
                    ": None), None)"
                ),
                True,
            ),
            check(
                "No final pause",
                (
                    "(lambda pause: (__raises_value_error__(lambda _: retry(lambda: int('bad'),"
                    " 2, pause), None), pause.call_count))(__import__('unittest.mock', fromlist"
                    "=['Mock']).Mock())"
                ),
                [True, 1],
            ),
            check(
                "No attempts is invalid",
                "__raises_value_error__(lambda _: retry(lambda: 1, 0, lambda: None), None)",
                True,
            ),
        ],
        [
            "Only retry ValueError; let other exception types propagate.",
            (
                "Pause only when another attempt remains; a bare raise re-raises the curr"
                "ent exception."
            ),
        ],
    ),
    unit(
        "sqlite-records",
        "python-design",
        "Store records in SQLite",
        "sqlite3 databases",
        """
        import sqlite3


        def open_store(path):
            connection = sqlite3.connect(path)
            connection.execute(
                "CREATE TABLE IF NOT EXISTS supplies "
                "(name TEXT PRIMARY KEY, amount INTEGER NOT NULL)"
            )
            return connection


        def add_supply(connection, name, amount):
            if amount < 0:
                raise ValueError("Amount cannot be negative")
            try:
                with connection:
                    connection.execute("INSERT INTO supplies VALUES (?, ?)", (name, amount))
            except sqlite3.IntegrityError as error:
                raise ValueError(f"{name} is already stored") from error


        def supply_amount(connection, name):
            row = connection.execute(
                "SELECT amount FROM supplies WHERE name = ?", (name,)
            ).fetchone()
            return None if row is None else row[0]


        def low_supplies(connection, limit):
            rows = connection.execute(
                "SELECT name FROM supplies WHERE amount < ? ORDER BY name", (limit,)
            ).fetchall()
            return [name for (name,) in rows]
        """,
        [
            probe(
                "Add and read back, including apostrophes",
                """
                store = open_store(":memory:")
                add_supply(store, "rope", 3)
                add_supply(store, "O'Brien lamp", 1)
                __probe_result__ = [
                    supply_amount(store, "rope"),
                    supply_amount(store, "O'Brien lamp"),
                    supply_amount(store, "map"),
                ]
                """,
                [3, 1, None],
                "Add rope 3 and O'Brien lamp 1 to a new in-memory store, then read rope, "
                "O'Brien lamp, and the missing map",
                "Use ? placeholders so quotes inside a name are ordinary data.",
            ),
            probe(
                "Low supplies are sorted by name",
                """
                store = open_store(":memory:")
                for name, amount in [("zeta", 1), ("apple", 2), ("mid", 9), ("edge", 3)]:
                    add_supply(store, name, amount)
                __probe_result__ = [low_supplies(store, 3), low_supplies(store, 0)]
                """,
                [["apple", "zeta"], []],
                "Store zeta 1, apple 2, mid 9, and edge 3, then ask for supplies below 3 and "
                "below 0",
                "Filter with amount < ? and sort with ORDER BY name.",
            ),
            probe(
                "Duplicates and negative amounts are rejected",
                """
                store = open_store(":memory:")
                add_supply(store, "rope", 3)
                __probe_result__ = [
                    __raises_value_error__(lambda name: add_supply(store, name, 8), "rope"),
                    __raises_value_error__(lambda amount: add_supply(store, "map", amount), -1),
                    supply_amount(store, "rope"),
                    supply_amount(store, "map"),
                ]
                """,
                [True, True, 3, None],
                "Add rope 3, then try adding rope 8 and map -1",
                "Translate sqlite3.IntegrityError into ValueError; check the amount before "
                "inserting.",
            ),
            probe(
                "Saved changes survive reopening the file",
                """
                first = open_store("store.db")
                add_supply(first, "rope", 3)
                first.close()
                second = open_store("store.db")
                __probe_result__ = supply_amount(second, "rope")
                second.close()
                """,
                3,
                "Add rope 3 to store.db, close it, open store.db again, and read rope",
                "Commit each insert, for example with a with connection: block.",
            ),
            probe(
                "SQL-shaped text is only data",
                """
                store = open_store(":memory:")
                name = "x'); DROP TABLE supplies; --"
                add_supply(store, name, 1)
                __probe_result__ = [supply_amount(store, name), low_supplies(store, 5)]
                """,
                [1, ["x'); DROP TABLE supplies; --"]],
                "Store a name that looks like SQL, then read it back and list low supplies",
                "Placeholders keep values out of the SQL text, so nothing in a name runs.",
            ),
        ],
        [
            "Create the table with CREATE TABLE IF NOT EXISTS inside open_store.",
            "Use ? placeholders for every value and with connection: to commit each insert.",
        ],
    ),
)

BUILD_INSTRUCTIONS = {
    "ready-to-ship": (
        "\nImplement `parse_count(text: str) -> int` to accept nonnegative integers"
        " with optional surrounding whitespace.\nUse `int(text)` to convert text to"
        " an integer; it already accepts surrounding whitespace and raises `ValueEr"
        'ror` for non-integer text.\nReturn `0` for `"0"` and `12` for `" 12 "`.\nR'
        'aise `ValueError` for negative values and non-integer text such as `"2.5"`'
        ' or `"hello"`.\n\nWrite assertions and exception checks in `test_parse_cou'
        "nt()` for zero, whitespace, and invalid input.\nCheck runs your test again"
        "st your implementation and deliberately broken versions to see whether it "
        "detects mistakes.\n"
    ).strip(),
    "data-models": (
        "\nImplement `Item(name, quantity)` with accessible `name` and `quantity` a"
        "ttributes and value equality.\nNames are strings and initial quantities ar"
        "e nonnegative integers.\nIts method `restock(amount)` accepts an integer, "
        "returning a new Item with the same name and its quantity increased by amou"
        "nt.\nNever change the original Item.\nReject negative amounts with `ValueE"
        "rror`; zero is valid and still returns a new Item.\nFor example, restockin"
        "g `Item('washers', 8)` by two produces an Item with quantity ten while the"
        " original remains eight.\nTwo Items with the same name and quantity must c"
        "ompare equal.\nDo not print.\n"
    ).strip(),
    "dataclass-lifecycle": (
        "\nDefine a dataclass `Batch(name: str, tags: list[str])` whose tags defaul"
        "t to a fresh empty list for each instance.\nStrip surrounding whitespace f"
        "rom the name during initialization and raise `ValueError` if the result is"
        " empty.\nImplement `renamed(self, name)` returning a different `Batch` wit"
        "h the normalized, validated new name and a copy of the original tags.\nThe"
        " original name and tags must remain unchanged when the returned batch is m"
        "odified.\nTags contain strings, so a shallow list copy is sufficient.\nPre"
        "serve dataclass value equality.\nDo not print or read input.\n"
    ).strip(),
    "typed-contracts": (
        "\nWrite `first_or(items: Iterable[T], default: T) -> T`, using a type vari"
        "able to describe the relationship.\nReturn the first value unchanged, or t"
        "he supplied default when input is empty.\nAccept one-pass iterables and co"
        "nsume at most one item.\nKeep falsy values such as `0`, `False`, and `''`;"
        " these are real first items even though they are false in conditions.\nWri"
        "te `parse_optional(text: str | None) -> int | None` returning `None` for `"
        "None` or whitespace-only text and otherwise the `int` conversion.\nAllow s"
        "igns and surrounding whitespace; invalid nonblank text raises `ValueError`"
        ".\nChecks assess behavior, so annotation spelling is not prescribed.\nDo n"
        "ot print or read input.\n"
    ).strip(),
    "practical-object-protocols": (
        "\nDefine `Score(points)` for nonnegative integers, with a readable and wri"
        "table `points` property.\nReject negative initialization or assignment wit"
        "h `ValueError`, leaving an existing value unchanged after a rejected updat"
        "e.\nYou may assume supplied point values are integers.\n`repr(Score(3))` m"
        "ust be `'Score(3)'`, and `len(score)` must equal its points.\nTwo scores c"
        "ompare equal exactly when their points match; a score is unequal to a plai"
        "n integer.\nAdding two scores returns a new score with their summed points"
        " and changes neither operand.\nAdding a score and an unsupported type must"
        " raise `TypeError`.\nDo not print or read input.\n"
    ).strip(),
    "class-construction": (
        "\nDefine abstract `Renderer` with required instance method `render(self, t"
        "ext)`.\nDefine `PrefixRenderer(Renderer)` as a subclass implementing that "
        "method.\nIts constructor must store the supplied string prefix, and its `r"
        "ender` method must prepend that prefix to string text.\nProvide static hel"
        "per `valid_prefix(value)` returning whether a string contains any non-whit"
        "espace character.\nProvide class method `from_text(text)` stripping surrou"
        "nding whitespace and rejecting blank prefixes with `ValueError`.\nThe fact"
        "ory must return an instance of the class it was called on, including subcl"
        "asses that inherit the constructor.\n`Renderer` and subclasses that omit `"
        "render` must not be instantiable.\nDo not print or read input.\n"
    ).strip(),
    "structural-typing": (
        "\nDefine a `Writer` protocol with a `write(self, text: str)` method, then "
        "implement `emit_lines(writer: Writer, lines)`.\nFor each string in the fin"
        "ite iterable `lines`, call `writer.write` once with that string followed b"
        "y exactly one newline character.\nInput strings do not already contain new"
        "line characters.\nReturn the number of input lines written.\nAccept any ob"
        "ject with the required method, including unrelated classes; do not require"
        " `isinstance` or inheritance.\nEmpty input returns zero without writes.\nF"
        "or `['one', 'two']`, a StringIO should contain `'one\ntwo\n'` and the retu"
        "rn value should be two.\nDo not print or write to the terminal; send text "
        "only through the supplied writer.\n"
    ).strip(),
    "test-doubles": (
        "\nWrite `retry(operation, attempts, pause)`.\n`operation` and `pause` are "
        "callables taking no arguments; `attempts` is an integer.\nReject attempts "
        "below one with `ValueError` before calling either dependency.\nCall operat"
        "ion up to that many times, returning immediately after its first successfu"
        "l result.\nRetry only when it raises `ValueError`.\nCall pause once betwee"
        "n failed attempts, never before the first attempt or after the final failu"
        "re.\nIf every attempt fails, re-raise the last `ValueError`.\nLet other ex"
        "ceptions propagate without retrying.\nFor an operation that fails once and"
        " then returns 12 with three allowed attempts, return 12 after one pause.\n"
        "The tutor checks with fakes, so you do not need real sleeping or network a"
        "ccess.\n"
    ).strip(),
    "sqlite-records": (
        "Define four functions that keep supplies in an SQLite database.\n"
        '`open_store(path)` connects to `path`, which may be a file name or `":memory:"`, and '
        "returns the connection.\n"
        "It creates a table named `supplies`, with a unique text column `name` and a required "
        "integer column `amount`, if the table does not already exist.\n"
        "`add_supply(connection, name, amount)` stores a new supply and commits it.\n"
        "It raises `ValueError` for a negative amount or a name that is already stored, leaving "
        "the existing row unchanged.\n"
        "`supply_amount(connection, name)` returns the stored amount, or `None` when the name "
        "is not stored.\n"
        "`low_supplies(connection, limit)` returns the names whose amount is below `limit`, "
        "sorted by name.\n"
        "Names may contain any text, including quotes.\n"
        "Use `?` placeholders for every value, and never build SQL text from a value."
    ),
}

REPAIR_STAGES = {
    "ready-to-ship": _repair(
        (
            "Implement parse_percentage(text) and test_parse_percentage(). Accept integ"
            "er text from 0 through 100, including whitespace, and make the tests rejec"
            "t negative and oversized values. Raise ValueError for non-integer text and"
            " out-of-range values. The no-argument test function must pass with a corre"
            "ct implementation and fail if either boundary or invalid-input validation "
            "is removed. Do not print or read input."
        ),
        """
        def parse_percentage(text: str) -> int:
            value = int(text)
            if not 0 <= value <= 100:
                raise ValueError("Percentage out of range")
            return value

        def test_parse_percentage():
            assert parse_percentage('0') == 0
            assert parse_percentage(' 100 ') == 100
            for invalid in ('-1', '101', '2.5'):
                try:
                    parse_percentage(invalid)
                except ValueError:
                    pass
                else:
                    raise AssertionError('Invalid percentage accepted')
        """,
        """
        def parse_percentage(text: str) -> int:
            return int(text)

        def test_parse_percentage():
            assert parse_percentage('0') == 0
            assert parse_percentage(' 100 ') == 100
        """,
        [
            _check(
                "Valid boundaries",
                "(parse_percentage('0'), parse_percentage(' 100 '))",
                (0, 100),
                "Accept both inclusive boundaries.",
            ),
            _check(
                "Reject oversized",
                "__raises_value_error__(parse_percentage, '101')",
                True,
                "Validate the upper boundary after conversion.",
            ),
            _check(
                "Regression test",
                "(test_parse_percentage(), True)[1]",
                True,
                "Run the authored test function.",
            ),
            _probe(
                "Reject negative and noninteger input",
                (
                    """
                result = [
                    __raises_value_error__(parse_percentage, value)
                    for value in ("-1", "2.5", "text")
                ]
                """
                ),
                [True, True, True],
                "Check the lower boundary and preserve int conversion failures.",
            ),
            _probe(
                "Learner tests detect removed validation",
                (
                    """
                original = parse_percentage
                mutants = [lambda text: int(text), lambda text: 0]
                result = []
                try:
                    for mutant in mutants:
                        globals()["parse_percentage"] = mutant
                        try:
                            test_parse_percentage()
                        except AssertionError:
                            result.append(True)
                        else:
                            result.append(False)
                finally:
                    globals()["parse_percentage"] = original
                """
                ),
                [True, True],
                "Your test must fail when range validation disappears or every result is zero.",
            ),
        ],
        [
            "Check both lower and upper bounds.",
            "Keep the test function meaningful by exercising invalid input.",
        ],
    ),
    "data-models": _repair(
        "Define a frozen Span dataclass with start and end numeric fields. Reject start > end "
        "with ValueError; equal endpoints are valid. overlap(other) returns a new Span covering "
        "the common interval, or None when the spans are disjoint. Touching endpoints produce "
        "a zero-length Span. Preserve both operands and support negative endpoints. Assume "
        "finite numbers and another Span. Use standard dataclass repr and value equality; "
        "do not print or read input.",
        """
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Span:
        start: float
        end: float

        def __post_init__(self):
            if self.start > self.end:
                raise ValueError('Reversed endpoints')

        def overlap(self, other):
            start = max(self.start, other.start)
            end = min(self.end, other.end)
            if start > end:
                return None
            return Span(start, end)
    """,
        """
    from dataclasses import dataclass

    @dataclass
    class Span:
        start: float
        end: float

        def overlap(self, other):
            self.start = max(self.start, other.start)
            self.end = max(self.end, other.end)
            return self
    """,
        [
            _check(
                "Overlapping interval",
                "repr(Span(1,7).overlap(Span(4,9)))",
                "Span(start=4, end=7)",
                "An intersection takes the later start and earlier end.",
            ),
            _check(
                "Touching and disjoint spans",
                "(repr(Span(-2,0).overlap(Span(0,3))), Span(1,2).overlap(Span(3,4)))",
                ("Span(start=0, end=0)", None),
                "Equal endpoints still intersect, but a gap returns None.",
            ),
            _check(
                "Reject reversed endpoints",
                "__raises_value_error__(lambda _: Span(3,2), None)",
                True,
                "Validate the relationship between the fields during construction.",
            ),
            _probe(
                "Frozen operands and a separate result",
                """
            from dataclasses import FrozenInstanceError, is_dataclass
            first, second = Span(1,5), Span(0,6)
            overlap = first.overlap(second)
            try:
                first.start = -1
            except FrozenInstanceError:
                frozen = True
            else:
                frozen = False
            result = (is_dataclass(first), frozen, overlap is first, overlap == first,
                      repr(first), repr(second))
            """,
                (True, True, False, True, "Span(start=1, end=5)", "Span(start=0, end=6)"),
                "Compute a fresh value instead of changing either operand.",
            ),
        ],
        [
            "Separate constructor validation from deciding whether two valid spans intersect.",
            "Take max of the starts and min of the ends; "
            "construct a new frozen value only when they overlap.",
        ],
    ),
    "dataclass-lifecycle": _repair(
        (
            "Define Entry with a normalized nonblank name and independent labels. Add t"
            "agged(label) returning a new Entry with a copied label list. Entry(name, l"
            "abels=...) is a dataclass. Strip surrounding whitespace from name and reje"
            "ct blank names with ValueError. Omitted labels creates a fresh list. tagge"
            "d appends to a new copied list and preserves the original Entry."
        ),
        """
        from dataclasses import dataclass, field, replace

        @dataclass
        class Entry:
            name: str
            labels: list[str] = field(default_factory=list)
            def __post_init__(self):
                self.name = self.name.strip()
                if not self.name:
                    raise ValueError('Empty name')
            def tagged(self, label):
                return replace(self, labels=[*self.labels, label])
        """,
        """
        from dataclasses import dataclass

        @dataclass
        class Entry:
            name: str
            labels: list[str] = []
            def tagged(self, label):
                self.labels.append(label)
                return self
        """,
        [
            _check(
                "Normalize and copy",
                "repr((lambda e: (e.tagged('new'), e))(Entry('  log  ', ['old']))[1])",
                "Entry(name='log', labels=['old'])",
                "Normalize during construction and return a separate tagged value.",
            ),
            _check(
                "Reject blank",
                "__raises_value_error__(Entry, '   ')",
                True,
                "Validate the normalized name in __post_init__.",
            ),
            _probe(
                "Fresh defaults and returned labels",
                (
                    """
                a, b = Entry("one"), Entry("two")
                a.labels.append("old")
                new = a.tagged("new")
                new.labels.append("later")
                result = (a.labels, b.labels, new.labels, new is a)
                """
                ),
                (["old"], [], ["old", "new", "later"], False),
                "Use a default factory and copy the labels when creating a tagged entry.",
            ),
        ],
        [
            "Use field(default_factory=list) for per-instance labels.",
            "replace creates the new dataclass while the list expression copies labels.",
        ],
    ),
    "typed-contracts": _repair(
        (
            "Define last_or(items, default) preserving the element type and consuming a"
            " one-pass iterable once. Define parse_flag(text) returning None for blank "
            "text, True for yes, and False for no. Annotate last_or using a TypeVar sha"
            "red by Iterable elements, default, and result. Return the default unchange"
            "d for empty input. parse_flag accepts None or strings, strips whitespace, "
            "compares yes/no case-insensitively, and raises ValueError for other nonbla"
            "nk text. Annotate its bool | None result."
        ),
        """
        from typing import TypeVar
        from collections.abc import Iterable

        T = TypeVar('T')

        def last_or(items: Iterable[T], default: T) -> T:
            result = default
            for item in items:
                result = item
            return result

        def parse_flag(text: str | None) -> bool | None:
            if text is None or not text.strip():
                return None
            value = text.strip().lower()
            if value == 'yes':
                return True
            if value == 'no':
                return False
            raise ValueError('Expected yes or no')
        """,
        """
        def last_or(items, default):
            return next(iter(items), default)

        def parse_flag(text):
            return bool(text)
        """,
        [
            _check(
                "Last item",
                "last_or(iter([1, 2, 3]), 0)",
                3,
                "Keep replacing the accumulator as the iterator advances.",
            ),
            _check(
                "False flag",
                "parse_flag(' no ')",
                False,
                "Recognize no as a real false value, not missing input.",
            ),
            _check("Blank flag", "parse_flag('   ')", None, "Handle blank input as missing."),
            _probe(
                "Falsy values and the full flag vocabulary",
                (
                    """
                result = [
                    last_or(iter([1, 0]), 9),
                    last_or([], False),
                    parse_flag(None),
                    parse_flag(" YES "),
                ]
                try:
                    parse_flag("maybe")
                except ValueError:
                    result.append(True)
                else:
                    result.append(False)
                """
                ),
                [0, False, None, True, True],
                (
                    "An empty iterable differs from a falsy final value; only yes and no are re"
                    "cognized flags."
                ),
            ),
        ],
        [
            "A type variable describes a relationship but does not convert values.",
            "Distinguish None from False when parsing a flag.",
        ],
    ),
    "practical-object-protocols": _repair(
        (
            "Define Temperature with a validated Celsius property, readable repr, equal"
            "ity by value, and addition that returns a new Temperature for another Temp"
            "erature only. Assume finite numeric values. Reject celsius below -273.15 o"
            "n construction and assignment without changing the prior value. repr is Te"
            "mperature(value). Equality compares Celsius values; equality and addition "
            "return NotImplemented for unrelated types. A sum below absolute zero raise"
            "s ValueError. Neither operand is mutated."
        ),
        """
        class Temperature:
            def __init__(self, celsius):
                self.celsius = celsius
            @property
            def celsius(self):
                return self._celsius
            @celsius.setter
            def celsius(self, value):
                if value < -273.15:
                    raise ValueError('Below absolute zero')
                self._celsius = value
            def __repr__(self):
                return f'Temperature({self.celsius})'
            def __eq__(self, other):
                if not isinstance(other, Temperature):
                    return NotImplemented
                return self.celsius == other.celsius
            def __add__(self, other):
                if not isinstance(other, Temperature):
                    return NotImplemented
                return Temperature(self.celsius + other.celsius)
        """,
        """
        class Temperature:
            def __init__(self, celsius):
                self.celsius = celsius
            def __repr__(self):
                return str(self.celsius)
            def __eq__(self, other):
                return True
            def __add__(self, other):
                self.celsius += other.celsius
                return self
        """,
        [
            _check(
                "Readable value",
                "repr(Temperature(20))",
                "Temperature(20)",
                "Format the class name and value.",
            ),
            _check(
                "Independent addition",
                "repr((lambda a, b: (a + b, a))(Temperature(2), Temperature(3))[1])",
                "Temperature(2)",
                "Addition must not mutate its left operand.",
            ),
            _check(
                "Validate property",
                "__raises_value_error__(Temperature, -274)",
                True,
                "Validate before storing the private value.",
            ),
            _probe(
                "Value operations and refused assignment",
                (
                    """
                a, b = Temperature(2), Temperature(3)
                sum_value = a + b
                try:
                    a.celsius = -300
                except ValueError:
                    pass
                result = (
                    repr(sum_value),
                    a.celsius,
                    b.celsius,
                    a == Temperature(2),
                    a == b,
                    a.__eq__(object()) is NotImplemented,
                    a.__add__(4) is NotImplemented,
                )
                """
                ),
                ("Temperature(5)", 2, 3, True, False, True, True),
                (
                    "Validate before assignment and implement value equality and addition witho"
                    "ut mutating operands."
                ),
            ),
        ],
        [
            "Property setters run during construction and later assignment.",
            "Return NotImplemented for unrelated operands.",
        ],
    ),
    "class-construction": _repair(
        (
            "Focus this repair on base validation and the subclass-aware factory. "
            "The abstract interface and instance decoding are supplied correctly. "
            "Define abstract Decoder with decode(self, text). Define IntegerDecoder(Dec"
            "oder), whose constructor stores base. Its decode uses int(text, self.base)"
            ". Define static valid_base(value) for integer bases 2 through 36 inclusive"
            ", and classmethod from_text(text) that converts stripped integer text, rej"
            "ects invalid bases with ValueError, and constructs the actual called class"
            ", including subclasses. The factory accepts signed and whitespace-padded i"
            "nteger text. Direct constructor arguments are assumed valid. Decoder and s"
            "ubclasses omitting decode cannot be instantiated. Keep import-time behavio"
            "r quiet."
        ),
        """
    from abc import ABC, abstractmethod

    class Decoder(ABC):
        @abstractmethod
        def decode(self, text):
            pass

    class IntegerDecoder(Decoder):
        def __init__(self, base):
            self.base = base

        @staticmethod
        def valid_base(value):
            return 2 <= value <= 36

        @classmethod
        def from_text(cls, text):
            base = int(text.strip())
            if not cls.valid_base(base):
                raise ValueError('Base must be from 2 through 36')
            return cls(base)

        def decode(self, text):
            return int(text, self.base)
    """,
        """
    from abc import ABC, abstractmethod

    class Decoder(ABC):
        @abstractmethod
        def decode(self, text):
            pass

    class IntegerDecoder(Decoder):
        def __init__(self, base):
            self.base = base

        @staticmethod
        def valid_base(value):
            return 2 < value < 36

        @classmethod
        def from_text(cls, text):
            return IntegerDecoder(int(text))

        def decode(self, text):
            return int(text, self.base)
    """,
        [
            _check(
                "Decode a different base",
                "IntegerDecoder.from_text(' 16 ').decode('ff')",
                255,
                "Use the stored base when converting text.",
            ),
            _probe(
                "Factory preserves subclasses",
                """
                class Special(IntegerDecoder):
                    pass


                result = (
                    type(Special.from_text("2")) is Special,
                    Special.from_text("2").decode("101"),
                    [IntegerDecoder.valid_base(n) for n in (1, 2, 36, 37)],
                )
                """,
                (True, 5, [False, True, True, False]),
                "Construct cls and include both valid boundaries.",
            ),
            _probe(
                "Reject invalid factory values",
                """
                result = [
                    __raises_value_error__(IntegerDecoder.from_text, text)
                    for text in ("1", "37", "bad", "")
                ]
                """,
                [True, True, True, True],
                "Convert then validate the base before constructing an instance.",
            ),
            _probe(
                "Abstract interface is enforced",
                """
                class Missing(Decoder):
                    pass


                result = []
                for cls in (Decoder, Missing):
                    try:
                        cls()
                    except TypeError:
                        result.append(True)
                    else:
                        result.append(False)
                """,
                [True, True],
                "Mark decode abstract on an ABC so incomplete classes cannot instantiate.",
            ),
        ],
        [
            "The factory belongs to the class, while decoding uses an instance base.",
            (
                "Normalize, validate, then construct cls. An abstract method defines the re"
                "quired interface."
            ),
        ],
    ),
    "structural-typing": _repair(
        (
            "Define a Reader protocol with read(). Implement read_all(reader) by readin"
            "g until an empty string, joining chunks, and accepting unrelated objects t"
            "hat provide read. Reader.read(self) -> str requires no size argument. Anno"
            "tate read_all(reader: Reader) -> str. A read may return only part of the d"
            "ata. Continue until exactly an empty string, preserve whitespace, propagat"
            "e read errors, and do not close the caller-owned reader."
        ),
        """
        from typing import Protocol

        class Reader(Protocol):
            def read(self) -> str: ...

        def read_all(reader: Reader) -> str:
            chunks = []
            while True:
                chunk = reader.read()
                if not chunk:
                    return ''.join(chunks)
                chunks.append(chunk)
        """,
        """
        from typing import Protocol

        class Reader(Protocol):
            def read(self) -> str: ...

        def read_all(reader: Reader) -> str:
            return reader.read(1)
        """,
        [
            _check(
                "Read chunks",
                "read_all(__import__('io').StringIO('ab'))",
                "ab",
                "Keep reading until read returns an empty string.",
            ),
            _check(
                "Unrelated reader",
                "read_all(type('R', (), {'read': lambda self: ''})())",
                "",
                "Use the operation, not inheritance or isinstance checks.",
            ),
            _probe(
                "Read all chunks through the protocol",
                (
                    """
                class Chunks:
                    def __init__(self):
                        self.chunks = iter(["a", " ", "b", ""])
                        self.reads = 0

                    def read(self):
                        self.reads += 1
                        return next(self.chunks)


                reader = Chunks()
                result = (read_all(reader), reader.reads)
                """
                ),
                ("a b", 4),
                (
                    "One read need not return the whole stream. Whitespace is data, not an end "
                    "marker."
                ),
            ),
        ],
        [
            "Protocols document the required operation.",
            "An empty chunk marks the end of the stream.",
        ],
    ),
    "test-doubles": _repair(
        (
            "Define fetch_with_fallback(primary, backup). Call primary once; return its"
            " result on success, and call backup only when primary raises ConnectionErr"
            "or. Let other errors propagate. Do not call backup after a successful prim"
            "ary, including None or False. Do not retry either callable. Exceptions fro"
            "m backup must propagate unchanged."
        ),
        """
        def fetch_with_fallback(primary, backup):
            try:
                return primary()
            except ConnectionError:
                return backup()
        """,
        """
        def fetch_with_fallback(primary, backup):
            try:
                return primary()
            except Exception:
                return backup()
        """,
        [
            _check(
                "Use primary",
                "fetch_with_fallback(lambda: 4, lambda: 9)",
                4,
                "Return the primary result without calling backup.",
            ),
            _check(
                "Fallback error only",
                (
                    "fetch_with_fallback(lambda: (_ for _ in ()).throw(ConnectionError()), lamb"
                    "da: 9)"
                ),
                9,
                "Catch the specific connection failure.",
            ),
            _check(
                "Other errors visible",
                _exec(
                    "\n                    try:\n                        fetch_with_fallback(\n"
                    "                            lambda: (_ for _ in ()).throw(TypeError()), la"
                    "mbda: 9\n                        )\n                    except TypeError:"
                    "\n                        result = True\n                    else:\n      "
                    "                  result = False\n                    "
                ),
                True,
                "Do not hide unrelated programming errors.",
            ),
            _probe(
                "Successful falsy results do not call backup",
                (
                    """
                calls = []


                def primary():
                    calls.append("primary")
                    return None


                def backup():
                    calls.append("backup")
                    return 4


                result = (fetch_with_fallback(primary, backup), calls)
                """
                ),
                (None, ["primary"]),
                (
                    "Fallback responds to ConnectionError, not to the truthiness of a successfu"
                    "l result."
                ),
            ),
        ],
        [
            "Catch only ConnectionError.",
            "The fallback is a callable and should run only after the intended failure.",
        ],
    ),
    "sqlite-records": _repair(
        "Repair the visit log.\n"
        "The `visits` table already exists, with text columns `visitor` and `place`.\n"
        "`record_visit(connection, visitor, place)` saves one row permanently, so it is still "
        "there after the connection closes.\n"
        "Visitor and place may contain any text, including apostrophes.\n"
        "`visits_to(connection, place)` returns the visitors recorded for that place, sorted by "
        "name, or `[]` when there are none.\n"
        "Never insert values into the SQL text itself.",
        """
        def record_visit(connection, visitor, place):
            with connection:
                connection.execute(
                    "INSERT INTO visits (visitor, place) VALUES (?, ?)", (visitor, place)
                )


        def visits_to(connection, place):
            rows = connection.execute(
                "SELECT visitor FROM visits WHERE place = ? ORDER BY visitor", (place,)
            ).fetchall()
            return [visitor for (visitor,) in rows]
        """,
        """
        def record_visit(connection, visitor, place):
            connection.execute(
                f"INSERT INTO visits (visitor, place) VALUES ('{visitor}', '{place}')"
            )


        def visits_to(connection, place):
            rows = connection.execute(
                f"SELECT visitor FROM visits WHERE place = '{place}' ORDER BY visitor"
            ).fetchall()
            return [visitor for (visitor,) in rows]
        """,
        [
            _probe(
                "A visit is still saved after closing",
                """
                import sqlite3

                first = sqlite3.connect("visits.db")
                first.execute("CREATE TABLE visits (visitor TEXT, place TEXT)")
                record_visit(first, "Ada", "ridge")
                first.close()
                second = sqlite3.connect("visits.db")
                result = visits_to(second, "ridge")
                second.close()
                """,
                ["Ada"],
                "A change is permanent only after the transaction is committed.",
            ),
            _probe(
                "Apostrophes are ordinary text",
                """
                import sqlite3

                store = sqlite3.connect(":memory:")
                store.execute("CREATE TABLE visits (visitor TEXT, place TEXT)")
                record_visit(store, "O'Neil", "Kim's camp")
                result = visits_to(store, "Kim's camp")
                """,
                ["O'Neil"],
                "A quote inside an f-string ends the SQL text early; pass values with ? instead.",
            ),
            _probe(
                "Visitors are sorted and filtered by place",
                """
                import sqlite3

                store = sqlite3.connect(":memory:")
                store.execute("CREATE TABLE visits (visitor TEXT, place TEXT)")
                for visitor, place in [("Mo", "cave"), ("Al", "cave"), ("Zed", "ridge")]:
                    record_visit(store, visitor, place)
                result = [visits_to(store, "cave"), visits_to(store, "lake")]
                """,
                [["Al", "Mo"], []],
                "Filter by place with a placeholder and sort with ORDER BY.",
            ),
        ],
        (
            "Try a visitor named O'Neil and read the error.",
            "Close the connection, reopen it, and check whether the earlier visit is still there.",
        ),
    ),
}

EXTRA_CHECKS = {
    "data-models": (
        check(
            "Zero restock still returns a new value",
            "(lambda item: item.restock(0) is item)(Item('x', 2))",
            False,
        ),
    ),
    "test-doubles": (
        probe(
            "Other errors are not retried",
            """
            calls = []
            def operation():
                calls.append("call")
                raise TypeError("programming error")
            try:
                retry(operation, 3, lambda: calls.append("pause"))
            except TypeError:
                __probe_result__ = calls
            else:
                raise AssertionError("TypeError was hidden")
            """,
            ["call"],
            ("Raise TypeError from operation; expect it to propagate after one call and no pause."),
            "Catch ValueError specifically, not all exceptions.",
        ),
    ),
}
