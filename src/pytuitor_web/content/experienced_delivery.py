"""Build and Repair contracts for python-delivery."""

from pytuitor_web.experienced_authoring import _check, _probe, _repair, check, unit

LESSONS = (
    unit(
        "module-boundaries",
        "python-delivery",
        "Keep imports predictable",
        "Modules & import boundaries",
        "from tools import normalize\n",
        [
            check("Normalize a label", "normalize('  LOW   Disk  ')", "low-disk"),
            check("Blank label", "normalize('  ')", ""),
            check(
                "Import stays quiet",
                (
                    '(lambda output: (exec("import importlib\\nfrom contextlib import redirect_'
                    "stdout\\nwith redirect_stdout(output):\\n    importlib.reload(__import__('"
                    "tools'))\", globals(), {'output': output}), output.getvalue())[1])(__imp"
                    "ort__('io').StringIO())"
                ),
                "",
            ),
        ],
        [
            "Put reusable logic in tools.py and import it into lesson.py.",
            "Keep demonstration printing inside an if __name__ == '__main__' guard.",
        ],
        files=(
            {
                "lesson.py": "from tools import normalize\n",
                "tools.py": "def normalize(text):\n    return '-'.join(text.lower().split())\n",
            },
        ),
    ),
    unit(
        "package-metadata",
        "python-delivery",
        "Understand package metadata",
        "Virtual environments & packaging",
        """
        import tomllib

        def package_summary(text):
            project = tomllib.loads(text)["project"]
            return {
                "name": project["name"],
                "version": project["version"],
                "dependencies": sorted(project.get("dependencies", [])),
            }
        """,
        [
            check(
                "Read and sort metadata",
                (
                    'package_summary(\'[project]\\nname = "weather-tool"\\nversion = "1.2'
                    '.0"\\ndependencies = ["zeta>=2", "alpha==1"]\')'
                ),
                {
                    "name": "weather-tool",
                    "version": "1.2.0",
                    "dependencies": ["alpha==1", "zeta>=2"],
                },
            ),
            check(
                "No dependencies",
                'package_summary(\'[project]\\nname = "local-tool"\\nversion = "0.1.0"\')',
                {"name": "local-tool", "version": "0.1.0", "dependencies": []},
            ),
        ],
        [
            "tomllib.loads parses TOML text into ordinary nested dictionaries.",
            ("Use get with an empty list default for optional dependencies; sort into a new list."),
        ],
    ),
    unit(
        "cli-contracts",
        "python-delivery",
        "Define a predictable CLI",
        "Argument parsing & exit behavior",
        """
        import argparse

        def parse_options(argv):
            parser = argparse.ArgumentParser()
            parser.add_argument("path")
            parser.add_argument("--limit", type=int, default=10)
            parser.add_argument("--json", action="store_true")
            options = parser.parse_args(argv)
            return {"path": options.path, "limit": options.limit, "json": options.json}
        """,
        [
            check(
                "Default options",
                "parse_options(['input.txt'])",
                {"path": "input.txt", "limit": 10, "json": False},
            ),
            check(
                "Explicit flags",
                "parse_options(['--json', '--limit', '3', 'a b.txt'])",
                {"path": "a b.txt", "limit": 3, "json": True},
            ),
            check(
                "Flags after the path",
                "parse_options(['log.txt', '--limit', '0'])",
                {"path": "log.txt", "limit": 0, "json": False},
            ),
        ],
        [
            (
                "Pass argv to parse_args so the function can be tested without changing p"
                "rocess arguments."
            ),
            "Use type=int for --limit and action='store_true' for a flag without a value.",
        ],
    ),
    unit(
        "resource-paths",
        "python-delivery",
        "Read data with explicit paths",
        "Pathlib & structured files",
        """
        import json
        from pathlib import Path

        def read_settings(path):
            try:
                text = Path(path).read_text(encoding="utf-8")
            except FileNotFoundError:
                return {}
            result = json.loads(text)
            if not isinstance(result, dict):
                raise ValueError("Settings must be an object")
            return result
        """,
        [
            check("Missing file has defaults", "read_settings('absent-settings.json')", {}),
            check(
                "Read a JSON object",
                (
                    "(__import__('pathlib').Path('settings.json').write_text('{\"city\": \"Mo"
                    "ntréal\"}', encoding='utf-8'), read_settings('settings.json'))[1]"
                ),
                {"city": "Montréal"},
            ),
            check(
                "Reject an array",
                (
                    "(__import__('pathlib').Path('settings.json').write_text('[]', encoding='ut"
                    "f-8'), __raises_value_error__(read_settings, 'settings.json'))[1]"
                ),
                True,
            ),
            check(
                "Malformed JSON is visible",
                (
                    "(__import__('pathlib').Path('settings.json').write_text('{', encoding='utf"
                    "-8'), __raises_value_error__(read_settings, 'settings.json'))[1]"
                ),
                True,
            ),
        ],
        [
            (
                "Catch only FileNotFoundError for an optional file; malformed content sho"
                "uld remain an error."
            ),
            "After parsing JSON, verify that the top-level value is a dictionary.",
        ],
    ),
)

BUILD_INSTRUCTIONS = {
    "module-boundaries": (
        "\nThe workspace has `lesson.py` and `tools.py`.\nImplement `normalize(text"
        ")` in tools.py, then import it into lesson.py.\nReturn the words of text i"
        "n lowercase, joined by single hyphens.\nWhitespace includes spaces, tabs, "
        "and newlines; discard surrounding whitespace and collapse runs.\nA blank s"
        "tring returns `\"\"`.\nFor example, `'  Build  REPORT '` becomes `'build-"
        "report'`.\n`text.split()` without a separator splits on runs of whitespace"
        ", and `'-'.join(words)` joins strings with hyphens.\nImporting or reloadin"
        "g tools must produce no output.\nDo not read input.\n"
    ).strip(),
    "package-metadata": (
        "\nWrite `package_summary(text)`.\nInput is valid TOML with a project table"
        " containing string name and version fields and an optional list of depende"
        "ncy strings.\nReturn a dictionary with exactly `name`, `version`, and `dep"
        "endencies`.\nCopy the name and version, and return dependencies sorted usi"
        "ng Python's normal string ordering; if absent, use an empty list.\nDo not "
        "install anything or print.\nThe checks teach metadata inspection; an actua"
        "l packaging release also requires building and installing its wheel in a c"
        "lean environment.\n"
    ).strip(),
    "cli-contracts": (
        "\nImplement `parse_options(argv)` with argparse.\n`argv` is a list of stri"
        "ngs excluding the program name.\nRequire one positional argument named `pa"
        "th`.\nAccept `--limit` as an integer with default ten and `--json` as a Bo"
        "olean flag defaulting to false.\nReturn a plain dictionary containing `pat"
        "h`, `limit`, and `json`.\nOptions may occur before or after the path.\nA p"
        "ath containing spaces arrives as one list item; do not split it again.\nZe"
        "ro and negative limits are accepted here, leaving their application meanin"
        "g to the caller.\nFor `['report.txt', '--json']`, return `{'path': 'report"
        ".txt', 'limit': 10, 'json': True}`.\nLet argparse handle invalid input and"
        " help in its normal way.\nDo not parse arguments at import time.\n"
    ).strip(),
    "resource-paths": (
        "\nWrite `read_settings(path)` accepting a string path or a Path object.\nR"
        "ead UTF-8 text and parse it as JSON.\nReturn the parsed dictionary if the "
        "top-level value is an object.\nReturn `{}` only when the file does not exi"
        "st.\nRaise `ValueError` for a valid JSON value that is not a dictionary.\n"
        "Let malformed JSON errors and other filesystem errors propagate.\nDo not w"
        'rite to the file, change directories, or print.\nFor a file containing `{"'
        "theme\": \"blue\"}`, return `{'theme': 'blue'}`.\nChecks create their own"
        " temporary files, so you do not need to prepare sample data before pressin"
        "g Check.\n"
    ).strip(),
}

REPAIR_STAGES = {
    "module-boundaries": _repair(
        "In tools.py define unique_labels(labels). Accept a finite one-pass iterable of strings. "
        "Strip surrounding whitespace, collapse internal whitespace to single spaces, and "
        "lowercase letters. Return a list of distinct nonblank normalized labels in first-seen "
        "order. Preserve punctuation and do not mutate input. Empty input returns []. "
        "In lesson.py import unique_labels so callers can use it there too. Both modules "
        "must import without printing or reading input; keep demonstrations under a main guard.",
        "from tools import unique_labels",
        "from tools import unique_labels",
        [
            _check(
                "Normalize before detecting duplicates",
                "unique_labels(iter(['  A  B ', 'a b', '', 'C!', 'c!']))",
                ["a b", "c!"],
                "Normalize each label before checking whether it has already been seen.",
            ),
            _probe(
                "Preserve source and first-seen order",
                """
            import tools
            labels = ['B', 'A', 'b']
            result = (tools.unique_labels(labels), labels, tools.unique_labels([]))
            """,
                (["b", "a"], ["B", "A", "b"], []),
                "Build a new result list in the reusable module; sorting changes first-seen order.",
            ),
            _check(
                "Quiet imports",
                "__stdout__",
                "",
                "Import-time demonstrations are side effects. "
                "Guard demonstrations so importing stays quiet.",
            ),
        ],
        [
            "Normalize before filtering blanks and duplicates.",
            "Keep ordered results separate from input, and keep reusable modules quiet.",
        ],
        files=(
            {
                "lesson.py": "from tools import unique_labels",
                "tools.py": """
            def unique_labels(labels):
                result = []
                seen = set()
                for label in labels:
                    normalized = ' '.join(label.split()).lower()
                    if normalized and normalized not in seen:
                        result.append(normalized)
                        seen.add(normalized)
                return result
            """,
            },
            {
                "lesson.py": "from tools import unique_labels",
                "tools.py": """
            def unique_labels(labels):
                return sorted(set(labels))

            print(unique_labels(['Demo']))
            """,
            },
        ),
    ),
    "package-metadata": _repair(
        (
            "Define project_requires(text). Read TOML project metadata and return the o"
            "ptional requires-python value, or None when it is absent. Let malformed TO"
            "ML raise. The project table is required: a missing table raises KeyError. "
            "The optional field is a string when present. Do not suppress TOMLDecodeErr"
            "or."
        ),
        """
        import tomllib

        def project_requires(text):
            return tomllib.loads(text)['project'].get('requires-python')
        """,
        """
        import tomllib

        def project_requires(text):
            try:
                return tomllib.loads(text)['project']['requires-python']
            except Exception:
                return ''
        """,
        [
            _check(
                "Read constraint",
                "project_requires('[project]\nrequires-python = \">=3.11\"\n')",
                ">=3.11",
                "Read the nested project field.",
            ),
            _check(
                "Missing value",
                "project_requires(\"[project]\\nname = 'demo'\\n\")",
                None,
                "Use get for an optional metadata field.",
            ),
            _probe(
                "Malformed TOML is not a missing field",
                (
                    """
                import tomllib

                try:
                    project_requires("[project")
                except tomllib.TOMLDecodeError:
                    result = True
                else:
                    result = False
                """
                ),
                True,
                "Only an absent optional field has a fallback; parser failures remain visible.",
            ),
        ],
        [
            "tomllib.loads parses the text into nested dictionaries.",
            "Do not catch malformed TOML or replace a missing value with an arbitrary string.",
        ],
    ),
    "cli-contracts": _repair(
        (
            "Define parse_duration(argv) with argparse. Require a positional task and a"
            "ccept integer --minutes default 30 plus --dry-run. Return a plain dictiona"
            "ry and let argparse handle errors. Return keys task, minutes, and dry_run "
            "with str, int, and bool values. Flags can precede or follow task. Unknown "
            "flags, missing task, or non-integer minutes cause SystemExit with code 2. "
            "No additional positivity rule applies."
        ),
        (
            "\n        import argparse\n\n        def parse_duration(argv):\n          "
            "  parser = argparse.ArgumentParser()\n            parser.add_argument('tas"
            "k')\n            parser.add_argument('--minutes', type=int, default=30)\n "
            "           parser.add_argument('--dry-run', action='store_true')\n        "
            "    options = parser.parse_args(argv)\n            return {'task': options"
            ".task, 'minutes': options.minutes, 'dry_run': options.dry_run}\n        "
        ),
        """
        def parse_duration(argv):
            return {'task': argv[0], 'minutes': 30, 'dry_run': False}
        """,
        [
            _check(
                "Defaults",
                "parse_duration(['backup'])",
                {"task": "backup", "minutes": 30, "dry_run": False},
                "Configure the positional and default option.",
            ),
            _check(
                "Options after task",
                "parse_duration(['backup', '--minutes', '5', '--dry-run'])",
                {"task": "backup", "minutes": 5, "dry_run": True},
                "Let argparse accept flags after the positional argument.",
            ),
            _probe(
                "Options before task and parser errors",
                (
                    """
                result = [parse_duration(["--dry-run", "--minutes", "0", "job"])]
                for args in ([], ["job", "--minutes", "bad"], ["job", "--unknown"]):
                    try:
                        parse_duration(args)
                    except SystemExit as error:
                        result.append(error.code)
                    else:
                        result.append(None)
                """
                ),
                [{"task": "job", "minutes": 0, "dry_run": True}, 2, 2, 2],
                "Use argparse for argument ordering, conversion, and diagnostic exits.",
            ),
        ],
        ["Use type=int for minutes.", "A store_true flag becomes true only when present."],
    ),
    "resource-paths": _repair(
        (
            "Define load_json(path). Return the parsed JSON value for an existing file,"
            " return None only when the file is missing, and let malformed JSON raise i"
            "ts decoder error. Read UTF-8 text and accept str or Path. Return any JSON "
            "value, including lists, numbers, false, and null. Other file errors, inclu"
            "ding trying to read a directory, propagate."
        ),
        """
        import json
        from pathlib import Path

        def load_json(path):
            try:
                return json.loads(Path(path).read_text(encoding='utf-8'))
            except FileNotFoundError:
                return None
        """,
        """
        import json
        from pathlib import Path

        def load_json(path):
            try:
                return json.loads(Path(path).read_text())
            except Exception:
                return None
        """,
        [
            _check(
                "Missing file",
                "load_json('/no/such/pytuitor-file.json')",
                None,
                "Catch FileNotFoundError specifically.",
            ),
            _check(
                "Read JSON",
                "(lambda p: (p.write_text('{\"ok\": true}'), load_json(p))[1])"
                "(__import__('pathlib').Path('stage.json'))",
                {"ok": True},
                "Read text as UTF-8 and parse it.",
            ),
            _check(
                "Malformed JSON",
                "(lambda p: (p.write_text('{'), "
                "__raises_value_error__(load_json, p))[1])"
                "(__import__('pathlib').Path('stage-bad.json'))",
                True,
                "Let JSON decoding errors reach the caller.",
            ),
            _probe(
                "UTF-8 and non-object JSON values",
                (
                    """
                from pathlib import Path

                path = Path("unicode.json")
                path.write_text('["Montréal", false, null]', encoding="utf-8")
                result = load_json(path)
                """
                ),
                ["Montréal", False, None],
                "Read explicit UTF-8 and preserve the type of the decoded JSON value.",
            ),
        ],
        [
            "Keep the missing-file fallback narrow.",
            "Do not turn malformed JSON into a missing file result.",
        ],
    ),
}

EXTRA_CHECKS = {}
