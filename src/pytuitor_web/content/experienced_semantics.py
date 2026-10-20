"""Build and Repair contracts for python-semantics."""

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
    unit(
        "python-expressions",
        "python-semantics",
        "Expressions with intent",
        "Python syntax & truthiness",
        """
        def display_name(value):
            if value is None:
                return "Anonymous"
            return value.strip() or "Anonymous"
        """,
        [
            check("Trim a name", "display_name('  Lin  ')", "Lin"),
            check("Missing value", "display_name(None)", "Anonymous"),
            check("Blank name", "display_name('   ')", "Anonymous"),
            check("Do not discard zero text", "display_name('0')", "0"),
        ],
        [
            "Handle None before calling a string method.",
            "An empty string is false in a condition; the string '0' is true.",
        ],
    ),
    legacy("objects-not-boxes", "python-semantics"),
    unit(
        "call-contracts",
        "python-semantics",
        "Make call sites readable",
        "Positional & keyword arguments",
        """
        def quote(price, quantity=1, *, discount=0):
            if price < 0 or quantity < 0 or not 0 <= discount <= 1:
                raise ValueError("Invalid quote")
            return round(price * quantity * (1 - discount), 2)
        """,
        [
            check("Defaults", "quote(12.5)", 12.5),
            check("Percentage discount", "quote(10, 3, discount=0.2)", 24.0),
            check("Free quote", "quote(9, 0)", 0),
            check("Reject negative price", "__raises_value_error__(quote, -1)", True),
            check(
                "Invalid discount",
                "__raises_value_error__(lambda _: quote(3, discount=2), None)",
                True,
            ),
        ],
        [
            "The discount is a fraction of the subtotal, not a fixed amount.",
            "Validate before calculating; round the final amount to two places.",
        ],
    ),
    unit(
        "collection-idioms",
        "python-semantics",
        "Group without losing order",
        "Dictionaries, sets & comprehensions",
        """
        def group_names(pairs):
            groups = {}
            for group, name in pairs:
                names = groups.setdefault(group, [])
                if name not in names:
                    names.append(name)
            return groups
        """,
        [
            check(
                "Group and deduplicate",
                "group_names([('ops', 'Ada'), ('dev', 'Lin'), ('ops', 'Bo'), ('ops', 'Ada')])",
                {"ops": ["Ada", "Bo"], "dev": ["Lin"]},
            ),
            check(
                "One-pass iterable",
                "group_names(iter([('x', 'a'), ('x', 'b')]))",
                {"x": ["a", "b"]},
            ),
            check("Empty input", "group_names([])", {}),
        ],
        [
            "Create a separate list for each key, then append new names.",
            "setdefault(key, []) returns the existing list or inserts a new one.",
        ],
    ),
    unit(
        "pattern-matching",
        "python-semantics",
        "Match values by their shape",
        "match & case patterns",
        """
        def handle(command):
            match command:
                case []:
                    return "Say something"
                case ["look"]:
                    return "You look around"
                case ["go", direction] if direction in ("north", "south", "east", "west"):
                    return f"You go {direction}"
                case ["go", _]:
                    return "You can't go that way"
                case ["take"]:
                    return "Take what?"
                case ["take", *items]:
                    return "Taken: " + ", ".join(items)
                case ["quit" | "exit"]:
                    return "Goodbye"
                case _:
                    return "Unknown command"
        """,
        [
            check("No words", "handle([])", "Say something"),
            check("Look", "handle(['look'])", "You look around"),
            check(
                "Known and unknown directions",
                "[handle(['go', 'north']), handle(['go', 'up'])]",
                ["You go north", "You can't go that way"],
            ),
            check(
                "Take nothing, one item, or several",
                "[handle(['take']), handle(['take', 'rope']), handle(['take', 'rope', 'lamp'])]",
                ["Take what?", "Taken: rope", "Taken: rope, lamp"],
            ),
            check("Two ways to leave", "[handle(['quit']), handle(['exit'])]", ["Goodbye"] * 2),
            check(
                "Everything else is unknown",
                "[handle(['go']), handle(['look', 'up']), handle(['dance']), "
                "handle(['go', 'north', 'now'])]",
                ["Unknown command"] * 4,
            ),
            check("A tuple has the same shape", "handle(('go', 'east'))", "You go east"),
            check(
                "The command is not changed",
                "(lambda words: (handle(words), words)[1])(['take', 'rope'])",
                ["take", "rope"],
            ),
        ],
        [
            "Write one case per command shape, from the most specific to the most general.",
            "A guard such as if direction in (...) decides between two go cases; "
            "*items collects the rest.",
        ],
    ),
)

BUILD_INSTRUCTIONS = {
    "python-expressions": (
        "\nWrite `display_name(value)`.\nIts argument is either `None` or a string."
        '\nReturn `"Anonymous"` for `None` or a string containing only whitespace.'
        "\nOtherwise return the string with surrounding whitespace removed, preserv"
        'ing its case and internal spaces.\nFor example, `display_name("  Ravi Shah'
        '  ")` returns `"Ravi Shah"`.\nThe string `"0"` must remain `"0"`.\nDefine '
        "the function without asking for input or printing.\nChecks call it with se"
        "veral arguments; Run can be used with your own temporary print calls.\n"
    ).strip(),
    "objects-not-boxes": (
        "\nWrite `def add_tag(record, tag):` so it returns an independent copy with"
        ' `tag` appended to its `"tags"` list.\nPreserve every other field, and do '
        "not change the original record or its nested contents.\nAssume the record "
        "contains ordinary dictionaries, lists, strings, and numbers.\n\nAdd a smal"
        "l example below your function and use Run to inspect both the original and"
        " the returned value.\nCheck also tests nested metadata, so copying only th"
        "e tags list is not sufficient for this contract.\n"
    ).strip(),
    "call-contracts": (
        "\nDefine `quote(price, quantity=1, *, discount=0)`.\nArguments are finite "
        "numbers; quantity is a nonnegative integer.\nReject a negative price, nega"
        "tive quantity, or discount outside the inclusive range zero through one wi"
        "th `ValueError`.\nReturn the price times quantity after applying the fract"
        "ional discount, rounded to two decimal places.\nFor example, `quote(8, 4, "
        "discount=0.25)` returns `24.0`.\nZero quantity and a discount of one are v"
        "alid and return zero.\nDo not print or read input.\n"
    ).strip(),
    "collection-idioms": (
        "\nWrite `group_names(pairs)`.\nEach pair contains a group string and a nam"
        "e string.\nReturn a dictionary mapping each group to its distinct names in"
        " first-seen order.\nKeep groups in their first-seen order too.\nNames are "
        "case-sensitive and already cleaned; preserve each supplied string exactly."
        "\nFor example, `[('team', 'Mina'), ('team', 'Sol'), ('team', 'Mina')]` bec"
        "omes `{'team': ['Mina', 'Sol']}`.\nAccept an empty iterable and a one-pass"
        " iterator.\nDo not mutate the input or print.\n"
    ).strip(),
    "pattern-matching": (
        "Define `handle(command)`, where `command` is a list or tuple of lowercase words, and "
        "return exactly these strings.\n"
        "No words return `Say something`, and exactly `look` returns `You look around`.\n"
        "`go` followed by `north`, `south`, `east`, or `west` returns `You go DIRECTION`; `go` "
        "followed by any other single word returns `You can't go that way`.\n"
        "Exactly `take` returns `Take what?`, and `take` followed by items returns `Taken: ` "
        "and the items joined with `, `, such as `Taken: rope, lamp`.\n"
        "Exactly `quit` or exactly `exit` returns `Goodbye`.\n"
        "Anything else, including `go` alone or a word after `look`, returns `Unknown "
        "command`.\n"
        "A `match` statement is recommended, but an equivalent `if` chain is valid.\n"
        "Do not change `command`."
    ),
}

REPAIR_STAGES = {
    "python-expressions": _repair(
        (
            "Write format_label(name, count). Use 'Anonymous' for a missing or blank na"
            "me and return '<name>: <count>' with the count converted to text. Preserve"
            " zero and do not print. Assume name is None or a string and count is an in"
            "teger. Strip only surrounding whitespace from names and preserve case and "
            "internal spaces."
        ),
        """
        def format_label(name, count):
            name = name.strip() if name is not None else ""
            return f"{name or 'Anonymous'}: {count}"
        """,
        """
        def format_label(name, count):
            return f"{name.strip()}: {count}"
        """,
        [
            _check(
                "Missing label",
                "format_label(None, 0)",
                "Anonymous: 0",
                "Handle None before using a string method.",
            ),
            _check(
                "Trim label",
                "format_label('  Ada  ', 3)",
                "Ada: 3",
                "Trim only the name and preserve the count.",
            ),
            _probe(
                "Blank, zero, and internal spaces",
                """
                result = [format_label(" \\t", 0), format_label("  A  B  ", -2)]
                """,
                ["Anonymous: 0", "A  B: -2"],
                "Handle whitespace-only names without losing zero or internal spaces.",
            ),
        ],
        [
            "Treat None and blank text as the same fallback case.",
            "An f-string can format the numeric count without changing its value.",
        ],
    ),
    "objects-not-boxes": _repair(
        (
            "Write merge_settings(base, overrides). Return a deep independent copy of b"
            "ase with override values applied, leaving base and its nested values uncha"
            "nged. Both arguments are dictionaries of ordinary nested containers and sc"
            "alar values. Overrides replace whole values, without recursive merging. Th"
            "e result must share no mutable nested containers with either argument."
        ),
        """
        from copy import deepcopy

        def merge_settings(base, overrides):
            result = deepcopy(base)
            result.update(deepcopy(overrides))
            return result
        """,
        """
        def merge_settings(base, overrides):
            base.update(overrides)
            return base
        """,
        [
            _check(
                "Apply overrides",
                "merge_settings({'a': 1}, {'b': 2})",
                {"a": 1, "b": 2},
                "Copy before updating.",
            ),
            _check(
                "Keep nested input independent",
                "(lambda x: (merge_settings(x, {}) is x, "
                "merge_settings(x, {})['meta'] is x['meta']))({'meta': []})",
                (False, False),
                "A shallow or in-place copy still aliases nested data.",
            ),
            _probe(
                "Overrides are independent too",
                (
                    """
                base = {"meta": {"tags": ["old"]}, "keep": []}
                overrides = {"meta": {"tags": ["new"]}}
                merged = merge_settings(base, overrides)
                merged["meta"]["tags"].append("changed")
                merged["keep"].append(1)
                result = (base, overrides)
                """
                ),
                ({"meta": {"tags": ["old"]}, "keep": []}, {"meta": {"tags": ["new"]}}),
                "Copy override values as well as the base before sharing the result.",
            ),
        ],
        ["Use deepcopy for nested independence.", "Update the copy, not the caller's mapping."],
    ),
    "call-contracts": _repair(
        (
            "Define label(text, /, prefix='item', *, upper=False). Return prefix plus '"
            ": ' plus text, uppercased only when requested, and preserve the positional"
            "-only and keyword-only contract. Both text and prefix are strings. Upperca"
            "se the whole result only when upper is true. Passing text by keyword or up"
            "per positionally must raise TypeError."
        ),
        """
        def label(text, /, prefix="item", *, upper=False):
            result = f"{prefix}: {text}"
            return result.upper() if upper else result
        """,
        """
        def label(text, prefix="item", upper=False):
            return f"{text}: {prefix}".upper() if upper else f"{text}: {prefix}"
        """,
        [
            _check(
                "Default label",
                "label('report')",
                "item: report",
                "Put the default prefix before the text.",
            ),
            _check(
                "Upper option",
                "label('report', prefix='file', upper=True)",
                "FILE: REPORT",
                "Uppercase the completed label only when requested.",
            ),
            _check(
                "Call contract",
                _exec(
                    """
                    try:
                        label(text="x")
                    except TypeError:
                        result = True
                    else:
                        result = False
                    """
                ),
                True,
                "A slash makes text positional-only.",
            ),
            _probe(
                "Reject a positional option",
                (
                    """
                try:
                    label("x", "tag", True)
                except TypeError:
                    result = True
                else:
                    result = False
                """
                ),
                True,
                "A bare star makes upper keyword-only.",
            ),
        ],
        [
            "Use a slash for positional-only text and a bare star before upper.",
            "Build the normal label first, then conditionally uppercase it.",
        ],
    ),
    "collection-idioms": _repair(
        (
            "Define count_words(words). Return a first-seen-order dictionary of word co"
            "unts for a one-pass iterable. Preserve case and do not mutate input. Words"
            " are strings. Empty input returns {}. Keep words such as A and a separate "
            "and preserve first insertion order."
        ),
        """
        def count_words(words):
            counts = {}
            for word in words:
                counts[word] = counts.get(word, 0) + 1
            return counts
        """,
        """
        def count_words(words):
            return {word: 1 for word in words}
        """,
        [
            _check(
                "Count repeats",
                "count_words(['red', 'blue', 'red'])",
                {"red": 2, "blue": 1},
                "Increment an existing count instead of replacing it.",
            ),
            _check(
                "One-pass words",
                "count_words(iter(['a', 'a']))",
                {"a": 2},
                "Iterate once and build the dictionary as you go.",
            ),
            _probe(
                "Empty, case, and insertion order",
                (
                    """
                result = [
                    list(count_words(iter(["b", "A", "a", "b"])).items()),
                    count_words([]),
                ]
                """
                ),
                [[("b", 2), ("A", 1), ("a", 1)], {}],
                (
                    "Counts are case-sensitive and dictionary insertion order follows the first"
                    " occurrence."
                ),
            ),
        ],
        [
            "Use get(word, 0) for a missing count.",
            "Dictionary assignment preserves the first insertion order.",
        ],
    ),
    "pattern-matching": _repair(
        "Repair `route(message)`, which receives one message.\n"
        "A dictionary whose `kind` is `move` and that has a `to` key returns `Moving to "
        "PLACE`.\n"
        "A dictionary whose `kind` is `move` without a `to` key returns `Where to?`.\n"
        "A dictionary whose `kind` is `say` and that has a `text` key returns that text.\n"
        "Anything else, including other kinds, missing keys, or a value that is not a "
        "dictionary, returns `Ignored`.\n"
        "Extra keys in a message do not change the result.",
        """
        def route(message):
            match message:
                case {"kind": "move", "to": place}:
                    return f"Moving to {place}"
                case {"kind": "move"}:
                    return "Where to?"
                case {"kind": "say", "text": text}:
                    return text
                case _:
                    return "Ignored"
        """,
        """
        def route(message):
            match message:
                case {"kind": "move"}:
                    return "Where to?"
                case {"kind": "move", "to": place}:
                    return f"Moving to {place}"
                case {"kind": "say", "text": text}:
                    return text
        """,
        [
            _check(
                "Move with a destination",
                "route({'kind': 'move', 'to': 'ridge'})",
                "Moving to ridge",
                "Mapping patterns ignore extra keys, so the first move case also fits here.",
            ),
            _check(
                "Move without a destination",
                "route({'kind': 'move'})",
                "Where to?",
                "A move message without a to key still needs its own case.",
            ),
            _check(
                "Extra keys are allowed",
                "[route({'kind': 'say', 'text': 'hello', 'volume': 3}), "
                "route({'to': 'cave', 'kind': 'move', 'speed': 2})]",
                ["hello", "Moving to cave"],
                "Order the cases from the most keys to the fewest.",
            ),
            _check(
                "Everything else is ignored",
                "[route({'kind': 'dance'}), route({}), route(['move']), route({'kind': 'say'})]",
                ["Ignored"] * 4,
                "A function that reaches its end without return gives None; add a final "
                "wildcard case.",
            ),
        ],
        (
            "Call route with a move message that has a to key and see which case runs.",
            "The first matching case wins, and a match with no fitting case returns None.",
        ),
    ),
}

EXTRA_CHECKS = {
    "call-contracts": (
        probe(
            "Discount is keyword-only",
            """
            try:
                quote(10, 2, 0.1)
            except TypeError:
                __probe_result__ = True
            else:
                __probe_result__ = False
            """,
            True,
            "Call quote(10, 2, 0.1); expect TypeError because discount must be named.",
            "Place discount after a bare * in the signature.",
        ),
        check(
            "Reject negative quantity", "__raises_value_error__(lambda _: quote(2, -1), None)", True
        ),
    ),
}
