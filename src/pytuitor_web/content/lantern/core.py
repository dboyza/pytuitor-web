"""The persistent, tested core game and its independent repair incidents."""

from pytuitor_web.content.lantern.authoring import api_import, milestone, public_names, scenario
from pytuitor_web.content.lantern.foundations import CORE_CHECKS, M4
from pytuitor_web.models import Check, code


def extend(files, source, *, module=None):
    """Assemble authored reference snapshots, never transform learner source."""
    files = dict(files)
    module = module or ("engine.py" if "engine.py" in files else "game.py")
    original = files[module]
    suffix = "\nmain()\n" if original.endswith("\nmain()\n") else ""
    files[module] = original.removesuffix(suffix) + "\n\n" + code(source) + suffix
    if module == "engine.py":
        names = public_names(files[module], {name.removesuffix(".py") for name in files})
        files[("game.py")] = (
            api_import(("engine"), names) + '\nif __name__ == "__main__":\n    main()\n'
        )
    return files


SAVE_CODE = """
    import csv
    import json
    from pathlib import Path


    def save_game(state, path):
        Path(path).write_text(json.dumps(state, indent=2), encoding="utf-8")


    def load_game(path):
        state = json.loads(Path(path).read_text(encoding="utf-8"))
        if (
            not isinstance(state, dict)
            or state.get("location") not in ("outpost", "forest", "ridge")
            or state.get("quest") not in ("open", "done")
            or type(state.get("turn")) is not int
            or state["turn"] < 0
            or not isinstance(state.get("supplies"), dict)
            or not {"food", "rope", "wood"} <= state["supplies"].keys()
        ):
            raise ValueError("Invalid game save")
        for count in state["supplies"].values():
            if type(count) is not int or count < 0:
                raise ValueError("Invalid supply count")
        return state


    def export_supplies(supplies, path):
        with open(path, "w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["item", "count"])
            writer.writerows(supplies.items())


    def import_supplies(path):
        result = {}
        with open(path, encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != ["item", "count"]:
                raise ValueError("Expected item,count header")
            for row in reader:
                count = int(row["count"])
                if not row["item"] or count < 0 or row["item"] in result:
                    raise ValueError("Invalid or duplicate supply")
                result[row["item"]] = count
        return result


    _step_before_saves = step


    def step(state, command):
        command = command.strip().lower()
        try:
            if command == "save":
                save_game(state, "save.json")
                return "Expedition saved."
            if command == "load":
                restored = load_game("save.json")
                state.clear()
                state.update(restored)
                return "Expedition restored."
            if command == "ledger":
                export_supplies(state["supplies"], "supplies.csv")
                return "Supply ledger exported."
        except (OSError, ValueError, KeyError, TypeError):
            return "Cannot read or write this expedition file."
        return _step_before_saves(state, command)
"""
SAVE_FILES = extend(M4.lesson.solution_files, SAVE_CODE)
SAVE_CHECKS = CORE_CHECKS + (
    scenario(
        "JSON round trip and rejected corrupt save",
        """
            from pathlib import Path

            state = new_game()
            step(state, "forest")
            save_game(state, "journey.json")
            restored = load_game("journey.json")
            Path("bad.json").write_text('{"location": "forest"}', encoding="utf-8")
            rejected = False
            try:
                load_game("bad.json")
            except ValueError:
                rejected = True
            result = (
                __expect__("restored", restored, state, "==")
                and restored is not state
                and rejected
            )
        """,
        "Validate loaded fields before making the loaded dictionary the active game.",
    ),
    scenario(
        "CSV uses quoted fields and an explicit header",
        """
            supplies = {"wood, dry": 3, "rope": 1}
            export_supplies(supplies, "ledger.csv")
            restored = import_supplies("ledger.csv")
            export_supplies({}, "empty.csv")
            result = __expect__("restored", restored, supplies, "==") and __expect__(
                "import_supplies('empty.csv')", import_supplies("empty.csv"), {}, "=="
            )
        """,
        "Use csv's reader and writer rather than splitting lines on commas.",
    ),
    scenario(
        "Playable save and load commands",
        """
            state = new_game()
            step(state, 'forest')
            step(state, 'save')
            step(state, 'ridge')
            step(state, 'load')
            result = __expect__("state['location']", state['location'], 'forest', '==')
        """,
        "Connect persistence to commands in the actual game loop.",
    ),
)
M5 = milestone(
    chapter="files-and-data",
    title="Keep a journal",
    capability="saves",
    requires=M4.provides,
    base=M4.lesson.solution_files,
    story=(
        "Leave the valley and return later. Mira also wants a supply ledger "
        "she can read as a table."
    ),
    teaching="## Source files and game saves are different\n\n"
    "Your Python files describe the rules; JSON records a particular expedition. "
    "For example, `json.dumps({'visits': 2})` produces text that can be written with UTF-8 "
    "and read with json.loads. Check the loaded structure before using it. "
    "CSV writers quote fields such as `tea, dried` correctly; do not "
    "join them with commas by hand. "
    "Generated saves stay in your workspace folder between runs.",
    requirements="Keep the previous game API and commands. Add `save_game(state, path)` and "
    "`load_game(path)` using UTF-8 JSON. Loaded state must be a dictionary with a valid location "
    "(outpost/forest/ridge), quest (open/done), nonnegative integer "
    "turn (not bool), and a supplies "
    "dictionary containing food, rope, wood with nonnegative integer counts (not bool). "
    "Reject malformed state with ValueError; missing paths may raise "
    "OSError. Keep extra fields.\n\n"
    "`export_supplies(supplies, path)` writes a CSV header `item,count` and the entries in "
    "insertion order. `import_supplies(path)` returns the same mapping; reject incorrect headers, "
    "blank/duplicate item names, noninteger or negative counts. A "
    "header-only file means an empty mapping. "
    "Use newline='' for CSV and preserve commas in item names.\n\n"
    "Add `save` and `load` commands using `save.json`, and `ledger` using `supplies.csv`. "
    "Failed file operations return helpful messages and leave the active state unchanged. "
    "Successful load updates the existing state object. These commands do not advance time.",
    reference=SAVE_FILES,
    checks=SAVE_CHECKS,
    repair_instructions=(
        "Repair `read_deliveries(path)`: read UTF-8 CSV with header "
        "`item,count`, including quoted item names, and return a list of "
        "`(item, integer_count)` tuples in file order. Skip no rows; a "
        "header-only file returns an empty list. Files supplied here have "
        "valid values. Close the file reliably. Do not return the header as a "
        "delivery."
    ),
    repair_reference="""
        import csv
        def read_deliveries(path):
            with open(path, encoding="utf-8", newline="") as stream:
                deliveries = []
                for row in csv.DictReader(stream):
                    deliveries.append((row["item"], int(row["count"])))
                return deliveries
    """,
    repair_broken="""
        def read_deliveries(path):
            with open(path, encoding="utf-8") as stream:
                return [tuple(line.strip().split(",")) for line in stream]
    """,
    repair_checks=(
        scenario(
            "Quoted item and empty ledger",
            """
                from pathlib import Path

                Path("delivery.csv").write_text(
                    'item,count\\n"wood, dry",2\\nrope,1\\n', encoding="utf-8"
                )
                Path("empty.csv").write_text("item,count\\n", encoding="utf-8")
                result = __expect__(
                    "read_deliveries('delivery.csv')",
                    read_deliveries("delivery.csv"),
                    [("wood, dry", 2), ("rope", 1)],
                    "==",
                ) and __expect__(
                    "read_deliveries('empty.csv')", read_deliveries("empty.csv"), [], "=="
                )
            """,
            "Let csv handle quoted delimiters and convert each count after reading the header.",
        ),
    ),
    hints=(
        "Serialize the dictionary with json; load into a temporary value before changing the game.",
        "Check required keys and types, including bool being a subclass of int.",
        "Use csv.DictReader with validated fieldnames and csv.writer with newline=''.",
    ),
    repair_hints=(
        "A comma can belong inside a quoted item name.",
        "DictReader consumes the header; convert each row's count.",
    ),
    minutes=40,
)

PATTERN_FILES = extend(
    SAVE_FILES,
    """
        import re


        def valid_marker(text):
            return re.fullmatch(r"[A-Z]{2}-[0-9]{3}", text) is not None


        def find_markers(text):
            return re.findall(
                r"(?<![A-Za-z0-9_])[A-Z]{2}-[0-9]{3}(?![A-Za-z0-9_])", text
            )


        def redact_markers(text):
            return re.sub(
                r"(?<![A-Za-z0-9_])[A-Z]{2}-[0-9]{3}(?![A-Za-z0-9_])",
                "[marker]",
                text,
            )


        _step_before_markers = step


        def step(state, command):
            cleaned = command.strip()
            if cleaned.lower().startswith("decode "):
                found = find_markers(cleaned[7:])
                return "Markers: " + (", ".join(found) if found else "none")
            return _step_before_markers(state, command)
    """,
)
MARKER_CHECKS = SAVE_CHECKS + (
    scenario(
        "Whole marker validation and text boundaries",
        """
            result = (
                valid_marker("AB-123")
                and (
                    not any(
                        (
                            valid_marker(s)
                            for s in (
                                "AB-1234",
                                "xAB-123",
                                "ab-123",
                                "AB-１２３",
                                "AB-123\\n",
                            )
                        )
                    )
                )
                and __expect__(
                    "find_markers('Use AB-123, then CD-456. Not xEF-789 or AB-1234.')",
                    find_markers("Use AB-123, then CD-456. Not xEF-789 or AB-1234."),
                    ["AB-123", "CD-456"],
                    "==",
                )
                and __expect__(
                    "redact_markers('Use AB-123; keep xAB-123.')",
                    redact_markers("Use AB-123; keep xAB-123."),
                    "Use [marker]; keep xAB-123.",
                    "==",
                )
                and __expect__(
                    "step(new_game(), 'decode AB-123')",
                    step(new_game(), "decode AB-123"),
                    "Markers: AB-123",
                    "==",
                )
            )
        """,
        "Use fullmatch for the whole code and guard surrounding word characters when extracting.",
    ),
)
M6 = milestone(
    chapter="text-patterns",
    title="Decode trail markers",
    capability="markers",
    requires=M5.provides,
    base=SAVE_FILES,
    reference=PATTERN_FILES,
    checks=MARKER_CHECKS,
    story=(
        "Old trail notes contain beacon markers. Read the complete code "
        "without accepting nearby junk."
    ),
    teaching="## Validation and extraction differ\n\n"
    "`re.fullmatch` checks an entire string. Searching prose needs boundaries around the match. "
    "For a separate example, `r'(?<![A-Za-z])cat(?![A-Za-z])'` finds cat without finding it "
    "inside scatter. These negative lookarounds assert that the adjacent character is not "
    "in the given set; they do not consume that character. `[0-9]` specifies ASCII digits.",
    requirements=(
        "Retain earlier game behavior. Add `valid_marker(text)` for exactly "
        "two uppercase ASCII letters, a hyphen, and three ASCII digits. Add "
        "`find_markers(text)` returning matching codes in order, preserving "
        "repeats; a code must not touch an ASCII letter, digit, or underscore. "
        "`redact_markers(text)` replaces those codes with `[marker]` and "
        "leaves other text unchanged. Add `decode TEXT` to step: return "
        "`Markers: ` plus codes joined by comma-space, or `Markers: none`. The "
        "command word is case-insensitive; retain the original case of its "
        "text. Do not mutate state."
    ),
    repair_instructions="Repair `rewrite_notes(text)` so it replaces only whole marker codes "
    "(two uppercase ASCII letters, hyphen, three ASCII digits, no adjacent ASCII word characters) "
    "with `<trail>`. Preserve all punctuation, whitespace, and invalid longer tokens.",
    repair_reference="""
        import re


        def rewrite_notes(text):
            return re.sub(
                r"(?<![A-Za-z0-9_])[A-Z]{2}-[0-9]{3}(?![A-Za-z0-9_])",
                "<trail>",
                text,
            )
    """,
    repair_broken="""
        import re
        def rewrite_notes(text):
            return re.sub(r"[A-Z]{2}-[0-9]+", "<trail>", text).strip()
    """,
    repair_checks=(
        Check(
            "Only complete trail codes are rewritten",
            "rewrite_notes(' AB-123, xCD-456 CD-4567!\\n')",
            " <trail>, xCD-456 CD-4567!\n",
            "Protect token boundaries and leave surrounding text exactly as it was.",
        ),
    ),
    hints=(
        "Use separate fullmatch and extraction patterns.",
        (
            "Lookarounds can exclude adjacent letters, digits, and underscores "
            "without consuming punctuation."
        ),
        "Normalize the command prefix, not the marker text.",
    ),
    repair_hints=(
        "A variable digit count accepts a prefix of an invalid token.",
        "Avoid strip: rewriting does not authorize changing whitespace.",
    ),
    minutes=20,
)

MODULAR_FILES = {
    "game.py": "",  # extend() authors the explicit launcher after adding the feature.
    "engine.py": PATTERN_FILES["game.py"].removesuffix("\nmain()\n"),
}
MODULAR_FILES = extend(
    MODULAR_FILES,
    """
        import argparse
        import random
        import statistics


        def encounter(seed):
            return random.Random(seed).choice(
                [
                    "A fox crosses the trail.",
                    "You find a clear spring.",
                    "The valley is quiet.",
                ]
            )


        def supply_mean(values):
            return statistics.mean(values) if values else 0


        _step_before_scouts = step


        def step(state, command):
            if command.strip().lower() == "scout":
                return encounter(state.get("seed", 0) + state["turn"])
            if command.strip().lower() == "summary":
                return "Mean supplies: " + str(
                    supply_mean(list(state["supplies"].values()))
                )
            return _step_before_scouts(state, command)


        def main(argv=None):
            parser = argparse.ArgumentParser(
                description="Explore Lantern Reach and help Mira restore its beacon."
            )
            parser.add_argument("--seed", type=int, default=0)
            parser.add_argument("--name", default="Explorer")
            args = parser.parse_args(argv)
            state = new_game()
            state["seed"] = args.seed
            state["name"] = args.name
            print("Lantern Reach | " + args.name)
            print(
                "Travel: outpost, forest, ridge. Actions: look, gather, inventory, deliver, eat N"
            )
            print(
                "Journal: save, load, ledger, decode TEXT. Explore: scout, summary. Exit: quit"
            )
            while True:
                try:
                    command = input("> ")
                except EOFError:
                    break
                if command.strip().lower() == "quit":
                    break
                print(step(state, command))
            print("Until next time.")
    """,
)
MODULE_CHECKS = MARKER_CHECKS + (
    scenario(
        "Repeatable encounters without changing global random state",
        """
            import random

            random.seed(317)
            before = random.getstate()
            first = encounter(5)
            result = (
                __expect__("encounter(5)", encounter(5), first, "==")
                and __expect__("random.getstate()", random.getstate(), before, "==")
                and (
                    first
                    in (
                        "A fox crosses the trail.",
                        "You find a clear spring.",
                        "The valley is quiet.",
                    )
                )
                and __expect__(
                    "supply_mean([1, 2, 6])", supply_mean([1, 2, 6]), 3, "=="
                )
                and __expect__("supply_mean([])", supply_mean([]), 0, "==")
            )
        """,
        "Use a local Random instance and handle an empty collection before calculating its mean.",
    ),
    scenario(
        "The engine is reusable without opening the input loop",
        """
            import contextlib, importlib, io

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                engine_module = importlib.reload(__import__("engine"))
            result = __expect__(
                "output.getvalue()", output.getvalue(), "", "=="
            ) and callable(engine_module.step)
        """,
        "Keep entrypoint execution behind the __name__ guard in game.py.",
    ),
)
M7 = milestone(
    chapter="modules-and-library-tools",
    title="Organize the expedition",
    capability="modules",
    requires=M6.provides,
    base=PATTERN_FILES,
    reference=MODULAR_FILES,
    checks=MODULE_CHECKS,
    story=(
        "The valley has enough rules to deserve a reusable engine. Scouting "
        "brings repeatable little discoveries."
    ),
    teaching="## Move responsibilities without replacing your work\n\n"
    "Move your existing functions into engine.py and import the functions you need in game.py. "
    "Place the entrypoint call under `if __name__ == '__main__':` so "
    "importing a module stays quiet. "
    "For independent randomness, `random.Random(7)` owns its state without reseeding other code. "
    "Your old game.py is retained; the new engine.py starts blank for you to organize it.",
    requirements="Create `engine.py` containing all previous public functions and game rules. "
    "`game.py` imports/re-exports those functions so they remain available there and invokes "
    "`main()` only under the __name__ guard. Importing either file must not prompt or print. "
    "`main(argv=None)` accepts argparse options `--name` (default Explorer) and integer `--seed` "
    "(default 0), displays the name in the greeting, and retains the interactive game.\n\n"
    "`encounter(seed)` chooses with a local random.Random from, in this order, "
    "`A fox crosses the trail.`, `You find a clear spring.`, `The valley is quiet.`. "
    "It must not change global random state. `supply_mean(values)` returns the arithmetic mean, "
    "or 0 for an empty list. Add `scout` and `summary` commands using these functions. "
    "Scout uses seed + current turn, without advancing time; summary "
    "returns `Mean supplies: VALUE`. "
    "Keep all earlier commands and the JSON/CSV helpers.",
    repair_instructions="Repair `choose_route(seed, routes)` so it returns a repeatable choice "
    "using a private random generator and leaves the caller's list and global random state "
    "unchanged. An empty route list returns None. Do not reset or advance global randomness.",
    repair_reference="""
        import random
        def choose_route(seed, routes):
            return random.Random(seed).choice(routes) if routes else None
    """,
    repair_broken="""
        import random
        def choose_route(seed, routes):
            random.seed(seed)
            random.shuffle(routes)
            return routes[0]
    """,
    repair_checks=(
        scenario(
            "Local randomness and caller ownership",
            """
                import random

                routes = ["river", "ridge", "forest"]
                before = random.getstate()
                first = choose_route(8, routes)
                result = (
                    __expect__("first", first, choose_route(8, routes), "==")
                    and __expect__("routes", routes, ["river", "ridge", "forest"], "==")
                    and __expect__("random.getstate()", random.getstate(), before, "==")
                    and (choose_route(0, []) is None)
                )
            """,
            "Create a private Random and choose without shuffling the caller's list.",
        ),
    ),
    hints=(
        "Move your functions into engine.py before changing their behavior.",
        "Re-export the functions in game.py and guard only the main call.",
        "Build the argparse parser inside main; use a local random generator for encounters.",
    ),
    repair_hints=(
        "Global seed changes other features' random choices.",
        "Handle empty routes before calling choice.",
    ),
    minutes=35,
)

DATE_FILES = extend(
    MODULAR_FILES,
    """
    from datetime import date, datetime, timedelta

    def game_date(state):
        return date(2030, 3, 1) + timedelta(days=state["turn"])

    def days_left(today, deadline):
        return (date.fromisoformat(deadline) - date.fromisoformat(today)).days

    def parse_meeting(text):
        return datetime.strptime(text, "%Y-%m-%d %H:%M").isoformat(timespec="minutes")

    _step_before_calendar = step

    def step(state, command):
        if command.strip().lower() == "calendar":
            today = game_date(state).isoformat()
            return today + " | days to gathering: " + str(days_left(today, "2030-03-08"))
        return _step_before_calendar(state, command)
""",
)
DATE_CHECKS = MODULE_CHECKS + (
    scenario(
        "Calendar arithmetic and visible game date",
        """
            state = new_game()
            state["turn"] = 31
            result = (
                __expect__(
                    "str(game_date(state))", str(game_date(state)), "2030-04-01", "=="
                )
                and __expect__(
                    "days_left('2028-02-28', '2028-03-01')",
                    days_left("2028-02-28", "2028-03-01"),
                    2,
                    "==",
                )
                and __expect__(
                    "days_left('2030-01-01', '2029-12-31')",
                    days_left("2030-01-01", "2029-12-31"),
                    -1,
                    "==",
                )
                and __expect__(
                    "parse_meeting('2030-03-08 09:30')",
                    parse_meeting("2030-03-08 09:30"),
                    "2030-03-08T09:30",
                    "==",
                )
                and step(state, "calendar").startswith("2030-04-01")
            )
        """,
        "Use date differences and timedelta; negative remaining days are meaningful.",
    ),
)
M8 = milestone(
    chapter="dates-and-times",
    title="Plan the supply run",
    capability="calendar",
    requires=M7.provides,
    base=MODULAR_FILES,
    reference=DATE_FILES,
    checks=DATE_CHECKS,
    story=(
        "The residents gather on March 8. Each successful action is a day in "
        "the expedition calendar."
    ),
    teaching="## A game clock you can test\n\n"
    "Use the stored turn count rather than today's real date. "
    "For example, adding `timedelta(days=2)` to December 31 naturally crosses a year boundary. "
    "A negative deadline difference means the date is in the past; do not erase that information.",
    requirements="Keep the game and add `game_date(state)`, returning a date for 2030-03-01 "
    "plus state['turn'] days. `days_left(today, deadline)` accepts ISO date strings and returns "
    "the signed whole-day difference. `parse_meeting(text)` accepts `YYYY-MM-DD HH:MM` and "
    "returns ISO text with minute precision, for example `2030-03-08T09:30`; invalid input "
    "raises ValueError. Add `calendar` returning `DATE | days to gathering: N` for the "
    "2030-03-08 gathering without changing state. Expose new functions from game.py too.",
    repair_instructions=(
        "Repair `arrival_date(start, days)` for a courier: accept an ISO date "
        "and a nonnegative integer duration, return the correct ISO arrival "
        "date across month/year boundaries, and raise ValueError for negative "
        "duration. Do not use the machine's current date."
    ),
    repair_reference="""
        from datetime import date, timedelta
        def arrival_date(start, days):
            if days < 0:
                raise ValueError("Negative duration")
            return (date.fromisoformat(start) + timedelta(days=days)).isoformat()
    """,
    repair_broken="""
        def arrival_date(start, days):
            year, month, day = start.split("-")
            return f"{year}-{month}-{int(day) + abs(days):02}"
    """,
    repair_checks=(
        scenario(
            "Leap year and rejected negative trip",
            """
                rejected = False
                try:
                    arrival_date("2030-01-01", -1)
                except ValueError:
                    rejected = True
                result = (
                    __expect__(
                        "arrival_date('2028-02-28', 2)",
                        arrival_date("2028-02-28", 2),
                        "2028-03-01",
                        "==",
                    )
                    and __expect__(
                        "arrival_date('2029-12-31', 1)",
                        arrival_date("2029-12-31", 1),
                        "2030-01-01",
                        "==",
                    )
                    and rejected
                )
            """,
            (
                "Calendar arithmetic handles month lengths; validation must preserve "
                "the sign's meaning."
            ),
        ),
    ),
    hints=(
        "Create a date from the fixed game start and add timedelta.",
        "Subtract deadline and today dates rather than day numbers.",
        "Use strptime for the explicit meeting format.",
    ),
    repair_hints=(
        "Changing only the day field cannot cross a month.",
        "Validate negative input before adding a timedelta.",
    ),
    minutes=20,
)

DEPOT_FILES = extend(
    DATE_FILES,
    """
        from collections import defaultdict, deque

        _new_game_before_depot = new_game


        def new_game():
            state = _new_game_before_depot()
            state["residents"] = []
            state["buildings"] = []
            return state


        def group_deliveries(deliveries):
            grouped = defaultdict(int)
            for item, amount in deliveries:
                grouped[item] += amount
            return dict(grouped)


        def serve_queue(names, limit):
            if limit < 0:
                raise ValueError("Negative limit")
            waiting = deque(names)
            served = []
            while waiting and len(served) < limit:
                served.append(waiting.popleft())
            return served, list(waiting)


        def active_requests(requests):
            return [name for name, done in requests if not done]


        _step_before_depot = step


        def step(state, command):
            cleaned = command.strip().lower()
            if cleaned == "depot":
                completed = state.get("residents", [])
                names = active_requests(
                    [("Oren", "Oren" in completed), ("Tess", "Tess" in completed)]
                )
                served, waiting = serve_queue(names, 2)
                return "Requests: " + (
                    ", ".join(served) if served else "all complete"
                )
            if cleaned in ("help oren", "help tess"):
                name = "Oren" if cleaned == "help oren" else "Tess"
                item, amount = ("rope", 1) if name == "Oren" else ("wood", 3)
                if name in state.get("residents", []):
                    return name + " is already settled."
                if (
                    state["location"] != "outpost"
                    or state["supplies"].get(item, 0) < amount
                ):
                    return (
                        "Bring "
                        + str(amount)
                        + " "
                        + item
                        + " to "
                        + name
                        + " at the outpost."
                    )
                state["supplies"][item] -= amount
                state.setdefault("residents", []).append(name)
                state["turn"] += 1
                if name == "Oren":
                    state["supplies"]["food"] += 2
                    return "Oren repairs the ferry and shares two food packs."
                state.setdefault("buildings", []).append("storehouse")
                return "Tess builds the outpost storehouse."
            return _step_before_depot(state, command)
    """,
)
DEPOT_CHECKS = DATE_CHECKS + (
    scenario(
        "Grouping, filtering, and FIFO preserve caller input",
        """
            names = ["Mira", "Oren", "Mira"]
            result = (
                __expect__(
                    "group_deliveries([('wood', 2), ('rope', 1), ('wood', 3)])",
                    group_deliveries([("wood", 2), ("rope", 1), ("wood", 3)]),
                    {"wood": 5, "rope": 1},
                    "==",
                )
                and __expect__("group_deliveries([])", group_deliveries([]), {}, "==")
                and __expect__(
                    "serve_queue(names, 2)",
                    serve_queue(names, 2),
                    (["Mira", "Oren"], ["Mira"]),
                    "==",
                )
                and __expect__(
                    "serve_queue(names, 0)", serve_queue(names, 0), ([], names), "=="
                )
                and __expect__("names", names, ["Mira", "Oren", "Mira"], "==")
                and __expect__(
                    "active_requests([('bridge', True), ('beacon', False)])",
                    active_requests([("bridge", True), ("beacon", False)]),
                    ["beacon"],
                    "==",
                )
                and __expect__(
                    "step(new_game(), 'depot')",
                    step(new_game(), "depot"),
                    "Requests: Oren, Tess",
                    "==",
                )
            )
        """,
        "A queue serves from the left; build a new queue rather than consuming the input list.",
    ),
    scenario(
        "Residents settle once and the outpost grows",
        """
            state = new_game()
            step(state, "help oren")
            step(state, "help oren")
            step(state, "forest")
            for _ in range(3):
                step(state, "gather")
            step(state, "outpost")
            step(state, "help tess")
            again = step(state, "help tess")
            result = (
                __expect__(
                    "state['residents']", state["residents"], ["Oren", "Tess"], "=="
                )
                and __expect__(
                    "state['supplies']['rope']", state["supplies"]["rope"], 0, "=="
                )
                and __expect__(
                    "state['supplies']['food']", state["supplies"]["food"], 4, "=="
                )
                and __expect__("Wood remaining", state["supplies"]["wood"], 0, "==")
                and __expect__(
                    "state['buildings']", state["buildings"], ["storehouse"], "=="
                )
                and __expect__("again", again, "Tess is already settled.", "==")
                and __expect__(
                    "step(state, 'depot')",
                    step(state, "depot"),
                    "Requests: all complete",
                    "==",
                )
            )
        """,
        (
            "Finish each resident's request once; apply rewards only after "
            "validating supplies and location."
        ),
    ),
)
M9 = milestone(
    chapter="collection-tools",
    title="Run the supply depot",
    capability="depot",
    requires=M8.provides,
    base=DATE_FILES,
    reference=DEPOT_FILES,
    checks=DEPOT_CHECKS,
    story=(
        "More residents arrive. Summarize deliveries and keep service fair by "
        "working in arrival order."
    ),
    teaching="## Match the collection to the job\n\nA grouping accumulator totals repeated keys. "
    "A deque's popleft removes the oldest request. A comprehension can select unfinished "
    "requests without changing the original list. For example, `[n for n in [1, 2, 3] if n > 1]` "
    "creates a separate filtered list.",
    requirements="Keep all earlier game behavior. Add `group_deliveries(deliveries)` for a list "
    "of (item, nonnegative amount) pairs, returning per-item totals in first-seen order; empty "
    "input gives {}. `serve_queue(names, limit)` returns `(served_list, waiting_list)` in FIFO "
    "order, retaining duplicates, without mutating names; limit=0 serves nobody and a negative "
    "limit raises ValueError. `active_requests(requests)` selects names whose (name, done) pair "
    "has a false done flag, retaining order. Expose all functions from game.py.\n\n"
    "New games also have independent empty `residents` and `buildings` lists. `depot` uses "
    "active_requests and serve_queue to list unfinished Oren and Tess requests in that order: "
    "`Requests: Oren, Tess`, one remaining name, or `Requests: all complete`.\n\n"
    "At the outpost, `help oren` spends one rope and awards two food packs; `help tess` spends "
    "three wood and adds `storehouse` to buildings. Each successful request adds the resident's "
    "capitalized name and advances one turn. Repeat requests return `NAME is already settled.` "
    "without another reward or cost. Insufficient supplies or the wrong location leave state "
    "unchanged and explain what is needed. Older saves may omit residents/buildings; treat "
    "missing fields as empty and create them when the first request succeeds.",
    repair_instructions="Repair `dispatch(requests, capacity)` returning (accepted, remaining) "
    "lists. Handle requests in arrival order, keep duplicates, accept up to capacity, and "
    "leave the caller's list unchanged. Capacity is a nonnegative integer; zero accepts none.",
    repair_reference="""
        from collections import deque
        def dispatch(requests, capacity):
            pending = deque(requests)
            accepted = []
            while pending and len(accepted) < capacity:
                accepted.append(pending.popleft())
            return accepted, list(pending)
    """,
    repair_broken="""
        def dispatch(requests, capacity):
            accepted = []
            while requests and len(accepted) <= capacity:
                accepted.append(requests.pop())
            return accepted, requests
    """,
    repair_checks=(
        scenario(
            "Queue boundary, repeats, and caller ownership",
            """
                original = ["A", "B", "A"]
                first = dispatch(original, 2)
                result = (
                    __expect__("first", first, (["A", "B"], ["A"]), "==")
                    and __expect__("original", original, ["A", "B", "A"], "==")
                    and __expect__(
                        "dispatch(original, 0)", dispatch(original, 0), ([], original), "=="
                    )
                    and __expect__("dispatch([], 3)", dispatch([], 3), ([], []), "==")
                )
            """,
            "Copy the input and stop before accepting one more than capacity.",
        ),
    ),
    hints=(
        "Accumulate amounts by item, not by delivery index.",
        "Construct a deque from names and popleft at most limit times.",
        "A filtered comprehension can preserve request order.",
    ),
    repair_hints=(
        "Observe both the returned remainder and the original list.",
        "Use FIFO removal and a strict less-than capacity boundary.",
    ),
    minutes=25,
)

CLASS_FILES = extend(
    DEPOT_FILES,
    """
        from enum import Enum


        class QuestState(Enum):
            OPEN = "open"
            DONE = "done"


        class Expedition:
            def __init__(self):
                self.state = new_game()

            def quest(self):
                return QuestState(self.state["quest"])

            def command(self, text):
                return step(self.state, text)


        def main(argv=None):
            parser = argparse.ArgumentParser(description="Lantern Reach expedition")
            parser.add_argument("--seed", type=int, default=0)
            parser.add_argument("--name", default="Explorer")
            args = parser.parse_args(argv)
            expedition = Expedition()
            expedition.state.update(seed=args.seed, name=args.name)
            print("Lantern Reach | " + args.name)
            print("A quiet valley. A broken beacon. An outpost waiting to become home.")
            print("Mira needs two wood from the forest. Oren and Tess wait at the depot.")
            print(
                "Commands: look, outpost, forest, ridge, gather, inventory, deliver, eat N"
            )
            print(
                "save, load, ledger, decode TEXT, scout, summary, calendar, depot, quit"
            )
            print("Resident requests: help oren, help tess")
            guide = expedition.command("help")
            if guide != "Unknown command.":
                print("More commands: " + guide)
            while True:
                try:
                    command = input("> ")
                except EOFError:
                    break
                if command.strip().lower() == "quit":
                    break
                print(expedition.command(command))
            print("Until next time.")
    """,
)
CLASS_FILES["test_game.py"] = code("""
    import unittest
    from engine import Expedition, QuestState

    class ExpeditionTests(unittest.TestCase):
        def test_independent_games(self):
            left, right = Expedition(), Expedition()
            left.command("forest")
            left.command("gather")
            self.assertEqual(right.state["supplies"]["wood"], 0)

        def test_delivery_once(self):
            game = Expedition()
            game.state["supplies"]["wood"] = 3
            game.command("deliver")
            game.command("deliver")
            self.assertEqual(game.state["supplies"]["wood"], 1)
            self.assertEqual(game.quest(), QuestState.DONE)

        def test_rejected_food(self):
            game = Expedition()
            game.command("eat -1")
            self.assertEqual(game.state["supplies"]["food"], 2)

    if __name__ == "__main__":
        unittest.main()
""")
CLASS_CHECKS = DEPOT_CHECKS + (
    scenario(
        "Independent expedition objects and quest states",
        """
            left, right = (Expedition(), Expedition())
            left.command("forest")
            left.command("gather")
            result = (
                __expect__(
                    "right.state['supplies']['wood']",
                    right.state["supplies"]["wood"],
                    0,
                    "==",
                )
                and left.quest() is QuestState.OPEN
            )
        """,
        "Each instance needs fresh state and quest() must return the named enum member.",
    ),
    scenario(
        "Learner tests reject repeated reward and shared-state bugs",
        """
            import contextlib, io, unittest, test_game, engine

            original = engine.Expedition.command


            def run_tests():
                suite = unittest.defaultTestLoader.loadTestsFromModule(test_game)
                report = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
                return (
                    __expect__("report.testsRun", report.testsRun, 3, ">=")
                    and report.wasSuccessful()
                )


            normal = run_tests()


            def mutant(self, text):
                if text.strip().lower() == "deliver":
                    self.state["quest"] = "open"
                return original(self, text)


            engine.Expedition.command = mutant
            try:
                rejects = not run_tests()
            finally:
                engine.Expedition.command = original
            result = normal and rejects
        """,
        "Write assertions for the second delivery's unchanged stock, not just the first success.",
    ),
)
M10 = milestone(
    chapter="classes-and-tested-tools",
    title="Build the expedition engine",
    capability="classes",
    requires=M9.provides,
    base=DEPOT_FILES,
    reference=CLASS_FILES,
    checks=CLASS_CHECKS,
    story=(
        "Your expedition becomes an object with its own state, and your tests "
        "defend the rules you have built."
    ),
    teaching="## Own state, reuse behavior\n\nA class need not rewrite working rules. "
    "Its constructor can create state and its methods can call the functions you already tested. "
    "For example, `self.balance = 0` in an initializer belongs to each account; a mutable class "
    "attribute would be shared. Test repeated actions and rejection as well as happy paths.",
    requirements="Retain all public functions. Add enum `QuestState` with OPEN='open' and "
    "DONE='done'. `Expedition()` owns fresh `state` from new_game; `command(text)` calls step "
    "and returns its message, and `quest()` returns the corresponding QuestState member. "
    "Refactor main to use an Expedition while retaining the CLI and game commands. "
    "Expose the class and enum from game.py.\n\nCreate `test_game.py` with at least three "
    "unittest tests: independent expedition state, repeated delivery cannot spend wood twice, "
    "and invalid food amounts leave stock unchanged. Import Expedition and QuestState from engine. "
    "Tests must pass the correct engine and fail if every delivery resets the quest to open first. "
    "Running the test file directly should run unittest; importing it must not run the tests.",
    repair_instructions="Repair class `SupplyChest`: each instance starts with its own empty "
    "`items` dictionary. `add(name, amount)` accepts a positive integer, adds to the existing "
    "count, and raises ValueError before mutation for nonpositive amounts. `take(name, amount)` "
    "returns False without mutation if amount is nonpositive or unavailable; otherwise subtract "
    "it and return True, retaining zero-count keys.",
    repair_reference="""
        class SupplyChest:
            def __init__(self):
                self.items = {}
            def add(self, name, amount):
                if amount <= 0:
                    raise ValueError("Positive amounts only")
                self.items[name] = self.items.get(name, 0) + amount
            def take(self, name, amount):
                if amount <= 0 or self.items.get(name, 0) < amount:
                    return False
                self.items[name] -= amount
                return True
    """,
    repair_broken="""
        class SupplyChest:
            items = {}
            def add(self, name, amount):
                self.items[name] = amount
            def take(self, name, amount):
                self.items[name] -= amount
                return self.items[name] >= 0
    """,
    repair_checks=(
        scenario(
            "Independent chests and rejected transfers",
            """
                left, right = (SupplyChest(), SupplyChest())
                left.add("wood", 2)
                left.add("wood", 1)
                rejected = False
                try:
                    left.add("wood", 0)
                except ValueError:
                    rejected = True
                result = (
                    rejected
                    and __expect__("right.items", right.items, {}, "==")
                    and (left.take("wood", 4) is False)
                    and __expect__("left.items['wood']", left.items["wood"], 3, "==")
                    and (left.take("wood", 3) is True)
                    and __expect__("left.items['wood']", left.items["wood"], 0, "==")
                    and (left.take("missing", 1) is False)
                )
            """,
            "Initialize per-instance collections and validate before mutation.",
        ),
    ),
    hints=(
        "Keep the functions and delegate to them from the class methods.",
        "Store the dictionary on self in __init__, not on the class.",
        "Assert exact stock after calling deliver twice.",
    ),
    repair_hints=(
        "Two instances should not share a dictionary.",
        "A failed operation must not already have changed its input.",
    ),
    minutes=40,
)

ARCHIVE_FILES = extend(
    CLASS_FILES,
    """
        import shutil


        def archive_plan(names):
            result = []
            for name in names:
                path = Path(name)
                if (
                    path.is_absolute()
                    or len(path.parts) != 1
                    or name in ("", ".", "..")
                    or "\\\\" in name
                    or "/" in name
                ):
                    raise ValueError("Use a plain file name")
                if name not in result:
                    result.append(name)
            return result


        def archive_files(source, destination, names, dry_run=True):
            selected = archive_plan(names)
            source, destination = Path(source), Path(destination)
            if source.is_symlink() or destination.is_symlink():
                raise ValueError("Use regular directories")
            for name in selected:
                item = source / name
                if item.is_symlink() or not item.is_file():
                    raise ValueError("Missing or linked source")
                if (destination / name).exists() or (
                    destination / name
                ).is_symlink():
                    raise FileExistsError(name)
            if not dry_run:
                destination.mkdir(parents=True, exist_ok=True)
                for name in selected:
                    with (
                        (source / name).open("rb") as incoming,
                        (destination / name).open("xb") as outgoing,
                    ):
                        shutil.copyfileobj(incoming, outgoing)
            return selected


        _step_before_beacon = step


        def step(state, command):
            cleaned = command.strip().lower()
            if cleaned == "beacon":
                if state["quest"] != "done":
                    return "Help Mira repair the frame first."
                state["beacon"] = True
                return "The beacon shines. Lantern Reach is home again."
            if cleaned == "archive":
                try:
                    planned = archive_files(".", "journal-backup", ["save.json"])
                    return (
                        "Archive preview: "
                        + ", ".join(planned)
                        + ". Use archive confirm to write."
                    )
                except (OSError, ValueError):
                    return "Save first and choose an unused backup destination."
            if cleaned == "archive confirm":
                try:
                    archive_files(
                        ".", "journal-backup", ["save.json"], dry_run=False
                    )
                    return "Journal archived."
                except (OSError, ValueError):
                    return "Archive refused; existing files are protected."
            if cleaned == "help":
                return (
                    "look, outpost, forest, ridge, gather, inventory, deliver, eat N, "
                    "save, load, ledger, decode TEXT, scout, summary, calendar, depot, "
                    "help oren, help tess, status, scene, beacon, archive, "
                    "archive confirm, help, quit"
                )
            if cleaned == "scene":
                scenes = {
                    "outpost": "Mira studies the beacon frame. Oren and Tess unload their packs.",
                    "forest": (
                        "Fallen branches lie beneath tall pines. "
                        "Gather wood for the outpost."
                    ),
                    "ridge": "The valley opens below you. The dark beacon points toward home.",
                }
                return scenes[state["location"]]
            if cleaned == "status":
                buildings = state.get("buildings", [])
                residents = state.get("residents", [])
                return (
                    "Residents helped: "
                    + (", ".join(residents) if residents else "none")
                    + " | Buildings: "
                    + (", ".join(buildings) if buildings else "none")
                    + " | Beacon: "
                    + ("lit" if state.get("beacon") else "dark")
                )
            return _step_before_beacon(state, command)
    """,
)
ARCHIVE_CHECKS = CLASS_CHECKS + (
    scenario(
        "Preview is read-only and copying refuses overwrite",
        """
            from pathlib import Path

            Path("journal").mkdir()
            Path("journal/save.json").write_text("journey", encoding="utf-8")
            preview = archive_files("journal", "backup", ["save.json", "save.json"])
            untouched = not Path("backup").exists()
            archive_files("journal", "backup", ["save.json"], dry_run=False)
            refused = False
            try:
                archive_files("journal", "backup", ["save.json"], dry_run=False)
            except FileExistsError:
                refused = True
            invalid = False
            try:
                archive_plan(["../save.json"])
            except ValueError:
                invalid = True
            result = (
                __expect__("preview", preview, ["save.json"], "==")
                and untouched
                and refused
                and invalid
                and __expect__(
                    "Path('backup/save.json').read_text()",
                    Path("backup/save.json").read_text(),
                    "journey",
                    "==",
                )
            )
        """,
        (
            "Validate all names first, keep preview read-only, and use exclusive "
            "creation at the write boundary."
        ),
    ),
    scenario(
        "The core adventure has a real conclusion",
        """
            state = new_game()
            early = step(state, "beacon")
            for command in (
                "forest",
                "gather",
                "gather",
                "outpost",
                "deliver",
                "beacon",
            ):
                ending = step(state, command)
            result = (
                "first" in early
                and state["beacon"] is True
                and __expect__(
                    "ending",
                    ending,
                    "The beacon shines. Lantern Reach is home again.",
                    "==",
                )
            )
        """,
        "The beacon can be restored only after Mira's delivery quest is complete.",
    ),
)
M11 = milestone(
    chapter="careful-automation",
    title="Restore the beacon",
    capability="beacon",
    requires=M10.provides,
    base=CLASS_FILES,
    reference=ARCHIVE_FILES,
    checks=ARCHIVE_CHECKS,
    story=(
        "Mira's frame is ready. Light the beacon and preserve a journal of the "
        "expedition you made possible."
    ),
    teaching="## Preview, validate, then write\n\n"
    "A preview must describe the intended action without creating directories or files. "
    "Checking exists is useful feedback, but another writer can create the file afterwards. "
    "Opening with mode 'x' makes refusal part of the write itself. "
    "These guards protect this tool's intended files; they are not a security sandbox.\n\n"
    "This completes the core adventure. Optional chapters can now add deeper capabilities.",
    requirements="Retain all game behavior. `archive_plan(names)` accepts plain file names "
    "only (no absolute paths, slash/backslash, empty, dot, or parent traversal), returns names "
    "in first-seen order without repeats, and raises ValueError for invalid names. "
    "`archive_files(source, destination, names, dry_run=True)` validates the full plan and source "
    "files; reject linked source files/directories and linked destination directories. Reject "
    "existing destination files with FileExistsError. Preview returns names without writes. "
    "With dry_run=False create the destination if needed, then copy each file using exclusive "
    "creation so even a competing writer cannot be overwritten. Failed multi-file copying may "
    "leave earlier new copies; preserve them and report failure rather than deleting user data.\n\n"
    "Add `beacon`: before quest completion return `Help Mira repair the frame first.`; after "
    "completion set state['beacon']=True and return `The beacon "
    "shines. Lantern Reach is home again.`. "
    "`archive` previews save.json into journal-backup; `archive "
    "confirm` writes it and reports refusal "
    "without destroying existing files. Add `help` listing every core command. Keep the new "
    "beacon field when saving/loading. Add `scene` with a short description of the active location "
    "and `status` showing helped residents, buildings, and whether the beacon is lit. "
    "The player can keep exploring after the ending.",
    repair_instructions="Repair `copy_report(source, destination, preview=True)`. Return the "
    "destination path as text. Preview must perform no writes. For a real copy, open the "
    "destination with exclusive creation so any existing content is preserved and FileExistsError "
    "is raised, even if it appeared just before opening. Paths point to regular files with "
    "existing parent directories; do not silently skip an existing destination.",
    repair_reference="""
        from pathlib import Path


        def copy_report(source, destination, preview=True):
            if not preview:
                with (
                    Path(source).open("rb") as incoming,
                    Path(destination).open("xb") as outgoing,
                ):
                    outgoing.write(incoming.read())
            return str(destination)
    """,
    repair_broken="""
        from pathlib import Path
        def copy_report(source, destination, preview=True):
            Path(destination).write_bytes(Path(source).read_bytes())
            return str(destination)
    """,
    repair_checks=(
        scenario(
            "Preview and conflict protection",
            """
                from pathlib import Path

                Path("source.txt").write_text("new")
                copy_report("source.txt", "target.txt")
                clean = not Path("target.txt").exists()
                Path("target.txt").write_text("keep")
                refused = False
                try:
                    copy_report("source.txt", "target.txt", False)
                except FileExistsError:
                    refused = True
                result = (
                    clean
                    and refused
                    and __expect__(
                        "Path('target.txt').read_text()",
                        Path("target.txt").read_text(),
                        "keep",
                        "==",
                    )
                )
            """,
            "Preview returns the plan only; real writes must use exclusive creation.",
        ),
    ),
    hints=(
        "Separate a pure name-validation function from the copy operation.",
        "Validate every source and destination before creating anything.",
        "Use xb at the final write, and add beacon only after checking quest completion.",
    ),
    repair_hints=(
        "Try preview with a nonexistent destination and inspect the filesystem.",
        "Mode wb replaces existing content; xb refuses it at the actual open.",
    ),
    minutes=40,
)
CORE = (M5, M6, M7, M8, M9, M10, M11)
