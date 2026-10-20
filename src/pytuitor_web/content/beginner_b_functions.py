"""Stage contracts for b-functions."""

from pytuitor_web.beginner_authoring import _check, _stage

BUILD_INSTRUCTIONS = {
    "small-superpowers": (
        "Write `def heal(health, potion):` and implement its body to return `health"
        " + potion`, with a maximum result of `100`.\nFor example, `heal(20, 10)` s"
        "hould return `30`, and `heal(90, 25)` should return `100`.\n\nUse a variab"
        "le to calculate the new health, an `if` to handle values above 100, and `r"
        "eturn` to send back the answer.\nYou may add `print(heal(90, 25))` outside"
        " the function so you can see the result when you run it.\nChecks call the "
        "function directly, so this extra print is optional."
    ),
    "clean-labels": (
        "A **slug** is a short text label often used in a web address or filename."
        "\nDefine `slug(text)` that returns a lowercase label with words separated "
        "by single hyphens.\nIgnore whitespace at the beginning and end; treat repe"
        "ated spaces and tabs as one separator.\nDo not remove punctuation.\n`slug("
        '"  Blue   Moon ")` returns `"blue-moon"`.\nEmpty or whitespace-only input '
        'returns `""`.\nThis function takes its argument from its caller, so it sho'
        "uld not call `input()`.\nReturn the result instead of only printing it."
    ),
    "function-options": (
        "Define `subtotal(prices, discount=0)`.\n`prices` is a list of nonnegative "
        "integer prices and `discount` is a nonnegative integer amount to subtract "
        "from the total, not a percentage.\nReturn the total after subtracting the "
        "discount, with a minimum of zero.\n`subtotal([6, 4])` returns `10`; `subto"
        "tal([6, 4], discount=3)` returns `7`.\nAn empty list returns `0`, includin"
        "g when a positive discount is given.\nUse the loop and accumulator pattern"
        " you already know.\nDo not change the input list."
    ),
    "recursion-basics": (
        "Define `digit_sum(number)` for a nonnegative integer containing at most 12"
        " digits.\nReturn the sum of its decimal digits as an integer; `digit_sum(2"
        "04)` returns `6`, and `digit_sum(0)` returns `0`.\nInputs are always valid"
        " integers in this range, so no validation is needed.\n`number % 10` gives "
        "the last digit and `number // 10` removes it.\nTry a recursive solution: r"
        "eturn a single digit directly, otherwise add the last digit to the sum of "
        "the remaining digits.\nA correct loop-based solution is also accepted.\nRe"
        "turn the result without printing."
    ),
    "recursive-collections": (
        "Define `sum_nested(items)`.\n`items` is a finite list whose elements are i"
        "ntegers or more lists following the same rule.\nReturn the sum of all inte"
        "gers at every depth.\n`sum_nested([1, [2, [3]], 4])` returns `10`.\nEmpty "
        "lists contribute zero, negative integers are allowed, and nesting is at mo"
        "st 20 levels deep.\nThe input never contains cycles: a list cannot contain"
        " itself, directly or through other lists.\nNo types other than lists and i"
        "ntegers occur.\nDo not change any input list and do not print.\nTry recurs"
        "ion, but any implementation with the required behavior is accepted."
    ),
    "handle-invalid-input": (
        "To **parse** text is to read it as a value or structure your program can u"
        "se.\nDefine `parse_quantity(text)`.\nConvert a string to an integer and re"
        "turn it if it is nonnegative.\nReturn `None` if conversion fails or the in"
        "teger is negative.\nSurrounding whitespace and a leading plus sign are val"
        'id because `int()` accepts them.\n`"3.5"` and `""` are invalid.\nThe input'
        " will always be a string; no input prompts or printed output are required."
    ),
}

REPAIR_STAGES = {
    "small-superpowers": _stage(
        (
            "Repair a separate stamina function. restore(stamina, snack) must add the s"
            "nack and cap the result at 50. A snack that would exceed the cap must not "
            "produce a larger value."
        ),
        """
        def restore(stamina, snack):
            amount = stamina + snack
            if amount > 50:
                amount = 50
            return amount
        """,
        """
        def restore(stamina, snack):
            amount = stamina + snack
            if amount > 50:
                amount = 50
            return stamina
        """,
        (
            _check("Below cap", "restore(20, 10)", 30),
            _check("At cap", "restore(45, 5)", 50),
            _check("Over cap", "restore(45, 20)", 50),
        ),
        (
            "Calculate the new amount before applying the cap.",
            "Return the capped amount, not the original stamina.",
        ),
    ),
    "clean-labels": _stage(
        (
            "Repair a separate heading function. heading(text) must trim outer whitespa"
            "ce, collapse runs of whitespace to single spaces, and capitalize the first"
            " character of each word. Title case starts a new word after punctuation to"
            "o and lowercases remaining letters: DON'T becomes Don'T. Empty or whitespa"
            "ce-only text returns an empty string."
        ),
        """
        def heading(text):
            return " ".join(text.split()).title()
        """,
        """
        def heading(text):
            text.split()
            return text.title()
        """,
        (
            _check("Repeated spaces", "heading('  blue   moon  ')", "Blue Moon"),
            _check("Tabs", "heading('red\\tplanet')", "Red Planet"),
            _check("Punctuation", "heading('version 2.0!')", "Version 2.0!"),
            _check("Empty text", "heading('')", ""),
            _check("Case and punctuation", 'heading("DON\'T stop")', "Don'T Stop"),
            _check("Whitespace only", "heading(' \\t ')", ""),
        ),
        (
            "split() returns the words and does not change text by itself.",
            "Join the cleaned words before applying the capitalization method.",
        ),
    ),
    "function-options": _stage(
        (
            "Repair a separate order function. order_total(prices, service_fee=0) must "
            "add all prices and then add one service fee for the whole order. An empty "
            "order still includes the fee, and prices must not be changed."
        ),
        """
        def order_total(prices, service_fee=0):
            total = 0
            for price in prices:
                total += price
            return total + service_fee
        """,
        """
        def order_total(prices, service_fee=0):
            total = 0
            for price in prices:
                total += price + service_fee
            return total
        """,
        (
            _check("Default fee", "order_total([6, 4])", 10),
            _check("One fee", "order_total([6, 4], service_fee=3)", 13),
            _check("Empty order fee", "order_total([], service_fee=3)", 3),
            _check(
                "Input unchanged",
                "(lambda values: (order_total(values, 2), values))([1, 2])",
                (5, [1, 2]),
            ),
        ),
        ("Add every price first.", "Apply service_fee once after the loop, not once per item."),
    ),
    "recursion-basics": _stage(
        (
            "Repair a separate recursive function. digit_product(number) must multiply "
            "the decimal digits of a nonnegative integer. The one-digit base case "
            "supplies the final digit, and larger numbers reduce with // and %."
        ),
        """
        def digit_product(number):
            if number < 10:
                return number
            return number % 10 * digit_product(number // 10)
        """,
        """
        def digit_product(number):
            if number < 10:
                return 1
            return number % 10 * digit_product(number // 10)
        """,
        (
            _check("Zero", "digit_product(0)", 0),
            _check("One digit", "digit_product(7)", 7),
            _check("Several digits", "digit_product(204)", 0),
            _check("Nonzero digits", "digit_product(234)", 24),
        ),
        (
            "The base case is reached for every one-digit number.",
            "Return that digit so it participates in the multiplication.",
        ),
    ),
    "recursive-collections": _stage(
        (
            "Repair a separate recursive function. count_nested(items) must count every"
            " integer at every depth in a finite nested list. Empty lists count as zero"
            "; do not count a list object as one integer."
        ),
        """
        def count_nested(items):
            total = 0
            for item in items:
                if isinstance(item, list):
                    total += count_nested(item)
                else:
                    total += 1
            return total
        """,
        """
        def count_nested(items):
            total = 0
            for item in items:
                if isinstance(item, list):
                    total += len(item)
                else:
                    total += 1
            return total
        """,
        (
            _check("Empty", "count_nested([])", 0),
            _check("Flat", "count_nested([3, -2])", 2),
            _check("Nested", "count_nested([1, [2, [3]], 4])", 4),
            _check("Empty inner lists", "count_nested([[[], []]])", 0),
            _check(
                ("Input unchanged"),
                ("(lambda x: (count_nested(x), x)[1])([1, [2, []]])"),
                [1, [2, []]],
            ),
        ),
        (
            "Use isinstance(item, list) to choose the recursive path.",
            "The recursive result is the number of integers inside the child list.",
        ),
    ),
    "handle-invalid-input": _stage(
        (
            "Repair a separate parser. parse_score(text) must return an integer from 0 "
            "through 100, or None for conversion errors and values outside that range. "
            "Whitespace and a leading plus sign are accepted by int()."
        ),
        """
        def parse_score(text):
            try:
                score = int(text)
            except ValueError:
                return None
            if score < 0 or score > 100:
                return None
            return score
        """,
        """
        def parse_score(text):
            score = int(text)
            if score < 0:
                return None
            return score
        """,
        (
            _check("Ordinary score", "parse_score('82')", 82),
            _check("Whitespace", "parse_score(' +7 ')", 7),
            _check("Negative", "parse_score('-1')", None),
            _check("Too high", "parse_score('101')", None),
            _check("Not a number", "parse_score('oops')", None),
            _check("Zero score", "parse_score('0')", 0),
            _check("Maximum score", "parse_score('100')", 100),
            _check("Decimal rejected", "parse_score('7.5')", None),
        ),
        (
            "Catch ValueError around int(text).",
            "After conversion, reject both negative and above-cap values.",
        ),
    ),
}
