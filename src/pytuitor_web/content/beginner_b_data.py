"""Stage contracts for b-data."""

from pytuitor_web.beginner_authoring import _check, _stage

BUILD_INSTRUCTIONS = {
    "text-files": (
        "Define `line_total(path)` that reads a UTF-8 file of integers, one per lin"
        "e, and returns their sum.\nIgnore blank and whitespace-only lines.\nAll no"
        "nblank lines contain valid integers, including negatives.\nAn empty file r"
        "eturns `0`.\nFor file contents `4`, a blank line, and `-1`, return `3`.\nR"
        "ead only the supplied path and do not change its contents.\nChecks create "
        "temporary files before calling your function."
    ),
    "paths-and-folders": (
        "Define `save_note(folder, text)`.\nCreate the requested folder, including "
        "missing parents.\nWrite `text` exactly as given to `note.txt` inside it, u"
        "sing UTF-8.\nReturn the resulting `Path` object.\nThe caller supplies a fo"
        "lder path as a string.\nIf `note.txt` already exists, replace its contents"
        " deliberately.\nDo not add a newline unless `text` already has one."
    ),
    "json-records": (
        "Define `save_scores(path, scores)`.\n`scores` is a dictionary mapping name"
        "s to nonnegative integer scores.\nWrite it as JSON to the supplied path an"
        "d return the sum of its scores.\nA dictionary's `.values()` method gives i"
        "ts values for a loop.\nAn empty dictionary must save an empty JSON object "
        "and return `0`.\nKeep every name exactly as given, including names with ac"
        "cented letters or characters from other languages.\nThese characters are r"
        "epresented using Unicode, the character system Python strings use.\nFormat"
        "ting and JSON key order do not matter.\nThe parent folder already exists."
    ),
    "csv-tables": (
        "Define `csv_total(path)` for a UTF-8 CSV with headers `item,quantity,price"
        "`.\nReturn the sum of `quantity * price` across all data rows.\nQuantities"
        " and prices are nonnegative integers; prices represent whole credits.\nA h"
        "eader-only file returns `0`.\nItem names may contain quoted commas and sho"
        "uld not affect the calculation.\nRead the file without modifying it."
    ),
    "regex-validation": (
        "Define `valid_code(text)` returning `True` only for exactly two uppercase "
        'ASCII letters, one hyphen, and exactly three ASCII digits.\n`"AB-123"` and'
        ' `"ZZ-000"` are valid.\nLowercase letters, spaces, extra characters, trail'
        "ing newlines, and non-ASCII digits are invalid.\nAn empty string is invali"
        "d.\nThe input is always a string; do not remove whitespace or change its c"
        "haracters before checking it.\nUse `[A-Z]` for uppercase ASCII letters and"
        " `[0-9]` for ASCII digits.\nReturn a Boolean without printing."
    ),
    "regex-transformations": (
        "Define `redact_tags(text)` returning a tuple `(names, redacted)`.\nHere, r"
        "edacting means hiding the names in the returned text.\nA valid tag is exac"
        "tly `[user:name]`, where `name` contains one or more lowercase ASCII lette"
        "rs.\n`names` is a list of names from every valid tag, preserving order and"
        " duplicates.\n`redacted` replaces every complete valid tag with `[user:hid"
        'den]` and preserves all other text exactly.\nFor `"[user:ada] met [user:bo'
        'b]"`, return `(["ada", "bob"], "[user:hidden] met [user:hidden]")`.\nInval'
        "id tags such as `[user:Ada]`, `[user:]`, and `[user:ab2]` remain unchanged"
        ' and contribute no names.\nEmpty input returns `([], "")`.\nThe input is a'
        "lways a string; do not print."
    ),
}

REPAIR_STAGES = {
    "text-files": _stage(
        (
            "Repair a separate file-reading function. nonblank_lines(path) must return "
            "the number of nonblank lines in a UTF-8 text file. Whitespace-only lines d"
            "o not count, including when they appear between negative and positive numb"
            "ers."
        ),
        """
        def nonblank_lines(path):
            with open(path, encoding="utf-8") as handle:
                count = 0
                for line in handle:
                    if line.strip():
                        count += 1
                return count
        """,
        """
        def nonblank_lines(path):
            with open(path, encoding="utf-8") as handle:
                count = 0
                for line in handle:
                    count += 1
                return count
        """,
        (
            _check(
                "Blank lines",
                (
                    "(__import__('pathlib').Path('lines.txt').write_text('4\\n \\n-1\\n', "
                    "encoding='utf-8'), nonblank_lines('lines.txt'))[1]"
                ),
                2,
            ),
            _check(
                "Empty file",
                (
                    "(__import__('pathlib').Path('lines.txt').write_text('', encoding='utf-8'),"
                    " nonblank_lines('lines.txt'))[1]"
                ),
                0,
            ),
            _check(
                "Whitespace only",
                (
                    "(__import__('pathlib').Path('lines.txt').write_text(' \\n\\t\\n', "
                    "encoding='utf-8'), nonblank_lines('lines.txt'))[1]"
                ),
                0,
            ),
        ),
        ("Read the file with a with block.", "Test line.strip() before counting the line."),
    ),
    "paths-and-folders": _stage(
        (
            "Repair a separate path helper. ensure_note(folder, title, text) must creat"
            "e missing parents, write text exactly inside folder/title.txt, and return "
            "the resulting Path. title is a nonempty filename stem without separators. "
            "Use UTF-8 and replace an existing note only at that exact path."
        ),
        """
        from pathlib import Path

        def ensure_note(folder, title, text):
            directory = Path(folder)
            directory.mkdir(parents=True, exist_ok=True)
            target = directory / (title + ".txt")
            target.write_text(text, encoding="utf-8")
            return target
        """,
        """
        from pathlib import Path

        def ensure_note(folder, title, text):
            target = Path(folder + title + ".txt")
            target.write_text(text, encoding="utf-8")
            return target
        """,
        (
            _check(
                "Nested folder",
                (
                    "(lambda path: [path.as_posix(), path.read_text(encoding='utf-8')])(ensure_"
                    "note('notes/deep', 'draft', 'café'))"
                ),
                ["notes/deep/draft.txt", "café"],
            ),
            _check(
                "Replace note",
                (
                    "(ensure_note('notes', 'daily', 'old'), ensure_note('notes', 'daily', "
                    "'new').read_text(encoding='utf-8'))[1]"
                ),
                "new",
            ),
            _check(
                ("Exact empty note"),
                (
                    "(lambda p: [p.as_posix(), p.read_bytes() == b''])(ensure_note('empty', "
                    "'blank', ''))"
                ),
                [("empty/blank.txt"), True],
            ),
        ),
        (
            "Create Path(folder) before joining a filename.",
            "mkdir(parents=True, exist_ok=True) handles missing folders.",
        ),
    ),
    "json-records": _stage(
        (
            "Repair a separate JSON settings reader. load_preferences(path) must read a"
            " JSON object with enabled and label fields and return [enabled, label]. JS"
            "ON's true and null values are valid here, so Python's display syntax is no"
            "t a substitute for JSON parsing."
        ),
        """
        import json

        def load_preferences(path):
            with open(path, encoding="utf-8") as handle:
                settings = json.load(handle)
            return [settings["enabled"], settings["label"]]
        """,
        """
        import json

        def load_preferences(path):
            with open(path, encoding="utf-8") as handle:
                settings = json.loads(handle)
            return [settings["enabled"], settings["label"]]
        """,
        (
            _check(
                "JSON boolean and null",
                (
                    "(__import__('pathlib').Path('settings.json').write_text('{\"enabled\": "
                    "true, \"label\": null}', encoding='utf-8'), "
                    "load_preferences('settings.json'))[1]"
                ),
                [True, None],
            ),
            _check(
                "Unicode label",
                (
                    "(__import__('pathlib').Path('settings.json').write_text('{\"enabled\": "
                    'false, "label": "café"}\', encoding=\'utf-8\'), '
                    "load_preferences('settings.json'))[1]"
                ),
                [False, "café"],
            ),
        ),
        (
            "Open the file with a with block and call json.load.",
            "JSON uses true, false, and null spellings that are not Python literals.",
        ),
    ),
    "csv-tables": _stage(
        (
            "Repair a separate CSV function. total_quantities(path) must add the "
            "quantity column from every data row, including rows whose item name "
            "contains a quoted comma. A header only file returns zero."
        ),
        """
        import csv

        def total_quantities(path):
            total = 0
            with open(path, newline="", encoding="utf-8") as handle:
                for row in csv.DictReader(handle):
                    total += int(row["quantity"])
            return total
        """,
        """
        import csv

        def total_quantities(path):
            total = 0
            with open(path, newline="", encoding="utf-8") as handle:
                for row in csv.DictReader(handle):
                    total += int(row["price"])
            return total
        """,
        (
            _check(
                "Quoted item",
                (
                    "(__import__('pathlib').Path('table.csv').write_text('item,quantity,price\\"
                    "n\"pen, blue\",2,3\\nbook,1,8\\n', encoding='utf-8'), total_quantities('"
                    "table.csv'))[1]"
                ),
                3,
            ),
            _check(
                "Header only",
                (
                    "(__import__('pathlib').Path('table.csv').write_text('item,quantity,price\\"
                    "n', encoding='utf-8'), total_quantities('table.csv'))[1]"
                ),
                0,
            ),
            _check(
                "Zero quantity",
                (
                    "(__import__('pathlib').Path('table.csv').write_text('item,quantity,price\\"
                    "nbox,0,9\\n', encoding='utf-8'), total_quantities('table.csv'))[1]"
                ),
                0,
            ),
        ),
        (
            "DictReader names the columns for you.",
            "Convert row['quantity'] to int and add that field, not price.",
        ),
    ),
    "regex-validation": _stage(
        (
            "Repair a separate text validator. valid_ticket(text) must accept exactly "
            "three lowercase ASCII letters, a colon, and two ASCII digits. Reject "
            "matching fragments, extra text, spaces, and non-ASCII digits."
        ),
        """
        import re

        def valid_ticket(text):
            return re.fullmatch(r"[a-z]{3}:[0-9]{2}", text) is not None
        """,
        """
        import re

        def valid_ticket(text):
            return re.search(r"[a-z]{3}:[0-9]{2}", text) is not None
        """,
        (
            _check("Valid ticket", "valid_ticket('abc:12')", True),
            _check("Extra text", "valid_ticket('xabc:12y')", False),
            _check("Uppercase", "valid_ticket('ABC:12')", False),
            _check("Unicode digit", "valid_ticket('abc:１２')", False),
            _check("Trailing newline", "valid_ticket('abc:12\\n')", False),
            _check("Empty text", "valid_ticket('')", False),
            _check("Wrong digit count", "valid_ticket('abc:1')", False),
        ),
        (
            "Use fullmatch so the complete string is checked.",
            "Use [0-9] when the contract calls for ASCII digits.",
        ),
    ),
    "regex-transformations": _stage(
        (
            "Repair the chat masker. mask_mentions(text) replaces every complete <@name"
            "> marker with <@hidden>, where name is one or more lowercase ASCII letters"
            ". Preserve all other text exactly. For '<@ada> met <@bob>', return '<@hidd"
            "en> met <@hidden>'. Invalid markers such as <@Ada>, <@bob2>, and <@> remai"
            "n unchanged. Empty text stays empty."
        ),
        """
        import re

        def mask_mentions(text):
            return re.sub(r"<@[a-z]+>", "<@hidden>", text)
        """,
        """
        import re

        def mask_mentions(text):
            return re.sub(r"<@[a-z]+>", "<@hidden>", text, count=1)
        """,
        (
            _check(
                "Two mentions", "mask_mentions('<@ada> met <@bob>')", ("<@hidden> met <@hidden>")
            ),
            _check(
                ("Repeated mention"),
                ("mask_mentions('<@ada> and <@ada>')"),
                ("<@hidden> and <@hidden>"),
            ),
            _check(
                "Invalid mentions", "mask_mentions('<@Ada> <@bob2> <@>')", ("<@Ada> <@bob2> <@>")
            ),
            _check("Incomplete marker", "mask_mentions('<@ada')", "<@ada"),
            _check("Adjacent mentions", "mask_mentions('<@ada><@bob>')", "<@hidden><@hidden>"),
            _check("Empty text", "mask_mentions('')", ""),
        ),
        (
            "Trace how many matches the replacement call changes.",
            "re.sub replaces every match by default; count=1 limits it to the first match.",
        ),
    ),
}
