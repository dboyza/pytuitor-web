"""From an arrival scene to a playable expedition, using only taught syntax."""

from pytuitor_web.content.lantern.authoring import milestone, scenario
from pytuitor_web.models import Check, code

ARRIVAL = code("""
    name = input("Explorer name: ")
    food = int(input("Food packs: "))
    distance = float(input("Trail distance: "))
    route = input("Route (ridge/river): ")
    print("Welcome to Lantern Reach, " + name + "!")
    print(f"Supplies: {food * 3} days")
    print(f"Trail: {distance:.1f} km")
    if route == "ridge" and food >= 2:
        print("Take the ridge.")
    else:
        print("Take the river.")
""")
ARRIVAL_CHECKS = (
    Check(
        "Enough food for the ridge",
        "__expect__('Final four lines', __stdout__.rstrip()[-77:], "
        "'Welcome to Lantern Reach, Ada!\\nSupplies: 6 days\\nTrail: 2.5 "
        "km\\nTake the ridge.')",
        True,
        "Two food packs are enough for the ridge.",
        stdin="Ada\n2\n2.5\nridge\n",
        description="The final four lines welcome Ada, report supplies and "
        "distance, and take the ridge.",
    ),
    Check(
        "The river is the safe fallback",
        "__stdout__.splitlines()[-3:]",
        ["Supplies: 3 days", "Trail: 1.2 km", "Take the river."],
        "A ridge request with fewer than two packs takes the river.",
        stdin="Jo\n1\n1.25\nridge\n",
    ),
    Check(
        "A river choice stays a river choice",
        "__stdout__.splitlines()[-1]",
        "Take the river.",
        "Check the route as well as the food.",
        stdin="Ren\n4\n0\nriver\n",
    ),
)
M1 = milestone(
    chapter="first-programs",
    title="Arrival at Lantern Reach",
    capability="arrival",
    story="You reach a quiet valley. An old beacon stands dark above a small outpost.",
    teaching="## Put the ingredients together\n\nA game can begin with four "
    "questions and a decision. "
    "For a different example, a ferry ticket might cost `passengers * 4`; format its distance with "
    "`f'{distance:.1f}'`. The number after the dot requests one decimal place. "
    "Convert input before calculating, and use `and` when both conditions must hold.",
    requirements="Write `game.py` from scratch. Read, in order: explorer name, nonnegative whole "
    "food-pack count, nonnegative decimal trail distance, and route (`ridge` or `river`). "
    "Inputs are valid at this milestone. Prompts are your choice.\n\n"
    "Finish with four lines: `Welcome to Lantern Reach, NAME!`, `Supplies: N days` (three days "
    "per pack), `Trail: D km` (one decimal), then `Take the ridge.` only when the route is "
    "`ridge` and there are at least two packs; otherwise `Take the river.`. "
    "Use only the values, input, calculations, formatting, and decisions taught so far.",
    reference={"game.py": ARRIVAL},
    checks=ARRIVAL_CHECKS,
    repair_instructions="A ferry keeper's sign is wrong. Keep the given `seats = 4` and "
    "`travellers = 4`. Calculate free seats without changing either value. Print exactly "
    "`Free seats: 0` and then `Full` when free seats are zero, otherwise `Space available`. "
    "Repair both the calculation and boundary decision.",
    repair_reference="""
        seats = 4
        travellers = 4
        free = seats - travellers
        print(f"Free seats: {free}")
        if free == 0:
            print("Full")
        else:
            print("Space available")
    """,
    repair_broken="""
        seats = 4
        travellers = 4
        free = seats + travellers
        print(f"Free seats: {free}")
        if free < 0:
            print("Full")
        else:
            print("Space available")
    """,
    repair_checks=(
        Check(
            "Exactly full ferry",
            "[seats, travellers, free]",
            [4, 4, 0],
            "Free seats are the seats remaining after the travellers board.",
            expected_output="Free seats: 0\nFull",
        ),
    ),
    hints=(
        "Read four answers in the requested order; input returns text.",
        "Multiply the converted food count by three and format the distance to one decimal.",
        "Both the ridge choice and food >= 2 are needed for the ridge message.",
    ),
    repair_hints=(
        "Compare the meaning of available seats with the calculation.",
        "An exactly full ferry has zero seats remaining, not a negative number.",
    ),
    stdin="Ada\n2\n2.5\nridge\n",
    minutes=15,
)

PACK = ARRIVAL + code("""
    pack = ["rope", "food", "food"]
    required = {"rope", "lamp", "food"}
    total = 0
    print("Your pack:")
    for item in pack:
        print(item)
        total = total + 1
    unique = set(pack)
    missing = required - unique
    print(f"Packed items: {total}")
    print(f"Unique supplies: {len(unique)}")
    print("Lamp missing:", "lamp" in missing)
""")
M2 = milestone(
    chapter="lists-and-sets",
    title="Pack for the trail",
    capability="pack",
    requires=("arrival",),
    base=M1.lesson.solution_files,
    story=(
        "The outpost keeper lends you a pack. Repeated food packs matter, but "
        "equipment requirements are unique."
    ),
    teaching="## Order and membership answer different questions\n\n"
    "A list such as `['map', 'map', 'cup']` retains both maps and their order. "
    "A set answers which kinds are present. `required - present` finds missing kinds. "
    "Keep the list when repeated items have meaning.",
    requirements="Retain the four-input arrival scene and its final four messages. After it, "
    "create `pack = ['rope', 'food', 'food']` and `required = {'rope', 'lamp', 'food'}`. "
    "Create `unique` as the unique packed kinds and `missing` as required kinds absent from "
    "the pack. Print `Your pack:` followed by each item in list order, including repeats. "
    "Finish with `Packed items: 3`, `Unique supplies: 2`, and `Lamp missing: True`. "
    "Derive these values from the collections, without changing `pack` or `required`.",
    reference={"game.py": PACK},
    checks=(
        Check(
            "Ordered pack and missing equipment",
            "[pack, sorted(unique), sorted(missing)]",
            [["rope", "food", "food"], ["food", "rope"], ["lamp"]],
            "Lists preserve repeats; set difference finds missing required kinds.",
        ),
        Check(
            "A visible packing scene",
            "'Your pack:\\nrope\\nfood\\nfood' in __stdout__",
            True,
            "Loop over the list, not the set.",
            expected_output="Packed items: 3\nUnique supplies: 2\nLamp missing: True",
        ),
        Check(
            "Arrival still works",
            "'Supplies: 6 days' in __stdout__ and 'Take the ridge.' in __stdout__",
            True,
            "Keep the previous arrival scene before the new packing scene.",
        ),
    ),
    repair_instructions="Repair the trading post's inventory report. Keep `incoming = "
    "['wood', 'wood', 'stone']` and `wanted = {'wood', 'cloth'}`. `shared` must contain kinds "
    "both wanted and incoming; `missing` must contain wanted kinds absent from incoming. "
    "Print all incoming items in order, including duplicates, then `Missing kinds: 1`. "
    "Do not change either input collection.",
    repair_reference="""
        incoming = ["wood", "wood", "stone"]
        wanted = {"wood", "cloth"}
        shared = set(incoming) & wanted
        missing = wanted - set(incoming)
        for item in incoming:
            print(item)
        print(f"Missing kinds: {len(missing)}")
    """,
    repair_broken="""
        incoming = ["wood", "wood", "stone"]
        wanted = {"wood", "cloth"}
        shared = set(incoming) | wanted
        missing = set(incoming) - wanted
        for item in set(incoming):
            print(item)
        print(f"Missing kinds: {len(missing)}")
    """,
    repair_checks=(
        Check(
            "Delivery keeps order and correct set direction",
            "[incoming, sorted(shared), sorted(missing)]",
            [["wood", "wood", "stone"], ["wood"], ["cloth"]],
            (
                "Compare shared kinds with missing wanted kinds; retain the original "
                "list for printing."
            ),
            expected_output="wood\nwood\nstone\nMissing kinds: 1",
        ),
    ),
    hints=(
        "Keep your previous code, then add a list and a set.",
        "Use a loop over pack for printing and counting.",
        "Calculate required - set(pack), then test whether lamp belongs to the result.",
    ),
    repair_hints=(
        "Union answers a different question from shared membership.",
        "Subtract incoming kinds from wanted kinds, and print the original list.",
    ),
    stdin="Ada\n2\n2.5\nridge\n",
    minutes=20,
)

OUTPOST = code("""
    supplies = {"food": 2, "rope": 1, "wood": 0}
    location = "outpost"
    locations = ["outpost", "forest", "ridge"]
    print("Lantern Reach")
    print("Commands: look, forest, ridge, outpost, gather, inventory, quit")
    command = input("> ")
    while command != "quit":
        if command == "look":
            print("Location:", location)
        elif command in locations:
            location = command
            print("Location:", location)
        elif command == "gather":
            if location == "forest":
                supplies["wood"] = supplies["wood"] + 1
                print("Gathered wood.")
            else:
                print("Visit the forest to gather wood.")
        elif command == "inventory":
            print("Wood:", supplies["wood"])
        else:
            print("Unknown command.")
        command = input("> ")
    print("Until next time.")
""")
M3 = milestone(
    chapter="loops-and-dictionaries",
    title="Open the outpost",
    capability="outpost",
    requires=("arrival", "pack"),
    base=M2.lesson.solution_files,
    story="Your pack now belongs to an explorer who can move, gather, and return to the outpost.",
    teaching="## Turn a scene into a command loop\n\n"
    "This milestone deliberately replaces the one-shot arrival questions with a repeatable "
    "game. Preserve their setting and supply idea, not their old input sequence. "
    "For example, a shop can keep `stock = {'cups': 2}` and update "
    "`stock['cups'] = stock['cups'] + 1` inside a loop. Initialize state before the loop "
    "so it survives the next command.",
    requirements=(
        "Refactor `game.py` into a repeatable game with no arrival questions. "
        "Initialize `supplies` to `{'food': 2, 'rope': 1, 'wood': 0}`, "
        "`location` to `outpost`, and `locations` to `['outpost', 'forest', "
        "'ridge']`. Print `Lantern Reach` and a command guide. Read one "
        "command at a time until `quit`, then print `Until next time.`. `look` "
        "prints `Location: LOCATION`. A location name travels there and prints "
        "that line. `gather` adds one wood only in the forest and prints "
        "`Gathered wood.`; elsewhere print `Visit the forest to gather wood.`. "
        "`inventory` prints `Wood: N`. Unknown commands print `Unknown "
        "command.` without changing state. Input is lowercase and ends with "
        "quit at this stage. Use top-level loops and dictionaries, without "
        "functions."
    ),
    reference={"game.py": OUTPOST},
    checks=(
        Check(
            "Travel and gather twice",
            "[location, supplies]",
            ["outpost", {"food": 2, "rope": 1, "wood": 2}],
            "Initialize supplies once and carry them across commands.",
            stdin="forest\ngather\ngather\noutpost\nquit\n",
        ),
        Check(
            "Unsafe gathering and unknown commands preserve state",
            "[location, supplies['wood']]",
            ["outpost", 0],
            "Only gathering in the forest changes wood.",
            stdin="gather\nnowhere\nlook\nquit\n",
        ),
        Check(
            "The player can see their pack",
            "'Wood: 1' in __stdout__",
            True,
            "Display the current count, not a fixed starting value.",
            stdin="forest\ngather\ninventory\nquit\n",
            expected_output="Until next time.",
        ),
    ),
    repair_instructions="The quartermaster processes repeated deliveries. Keep `deliveries = "
    "['wood', 'stone', 'wood']`. Build `counts` with the total for each kind, without changing "
    "deliveries. Build `running` with the number of deliveries processed after each item: "
    "`[1, 2, 3]`. Repair the lifetime and update order of the accumulators.",
    repair_reference="""
        deliveries = ["wood", "stone", "wood"]
        counts = {}
        running = []
        total = 0
        for item in deliveries:
            if item not in counts:
                counts[item] = 0
            counts[item] = counts[item] + 1
            total = total + 1
            running.append(total)
    """,
    repair_broken="""
        deliveries = ["wood", "stone", "wood"]
        counts = {}
        running = []
        total = 0
        for item in deliveries:
            counts[item] = 0
            counts[item] = counts[item] + 1
            running.append(total)
            total = total + 1
    """,
    repair_checks=(
        Check(
            "Repeated supplies and running totals",
            "[deliveries, counts, running]",
            [["wood", "stone", "wood"], {"wood": 2, "stone": 1}, [1, 2, 3]],
            "Keep previous counts and append the total after processing each delivery.",
        ),
    ),
    hints=(
        "Replace the four questions with initial game state and a command loop.",
        "Use membership in locations to handle travel, with separate branches for actions.",
        "Only initialize counts before the loop; read the next command at its end.",
    ),
    repair_hints=(
        "A repeated kind already has a count worth preserving.",
        "The running total describes the state after this delivery.",
    ),
)

ENGINE = code("""
    def new_game():
        return {
            "location": "outpost",
            "supplies": {"food": 2, "rope": 1, "wood": 0},
            "quest": "open",
            "turn": 0,
        }


    def describe(state):
        return "Location: " + state["location"]


    def step(state, command):
        command = command.strip().lower()
        if command == "look":
            return describe(state)
        if command in ("outpost", "forest", "ridge"):
            state["location"] = command
            state["turn"] += 1
            return describe(state)
        if command == "gather":
            if state["location"] != "forest":
                return "Visit the forest to gather wood."
            state["supplies"]["wood"] += 1
            state["turn"] += 1
            return "Gathered wood."
        if command == "inventory":
            return "Wood: " + str(state["supplies"]["wood"])
        if command == "deliver":
            if state["quest"] == "done":
                return "Mira already has her wood."
            if state["location"] != "outpost" or state["supplies"]["wood"] < 2:
                return "Bring two wood to Mira at the outpost."
            state["supplies"]["wood"] -= 2
            state["quest"] = "done"
            state["turn"] += 1
            return "Mira repairs the beacon frame."
        if command.startswith("eat "):
            try:
                amount = int(command[4:])
            except ValueError:
                return "Choose a positive whole food amount."
            if amount <= 0 or amount > state["supplies"]["food"]:
                return "Choose an available positive food amount."
            state["supplies"]["food"] -= amount
            state["turn"] += 1
            return "Shared a meal."
        return "Unknown command."


    def main():
        state = new_game()
        print("Lantern Reach")
        print(
            "Explore: outpost, forest, ridge. "
            "Actions: look, gather, inventory, deliver, eat N, quit"
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


    main()
""")
CORE_CHECKS = (
    scenario(
        "A complete delivery quest",
        """
            state = new_game()
            first = step(state, " FOREST ")
            step(state, "gather")
            step(state, "gather")
            step(state, "outpost")
            message = step(state, "deliver")
            result = (
                __expect__("first", first, "Location: forest", "==")
                and __expect__(
                    "Mira's quest after delivery", state["quest"], "done", "=="
                )
                and __expect__("Wood remaining", state["supplies"]["wood"], 0, "==")
                and __expect__("Turns used", state["turn"], 5, "==")
                and __expect__(
                    "message", message, "Mira repairs the beacon frame.", "=="
                )
            )
        """,
        "Normalize commands and consume exactly two wood only for the first valid delivery.",
    ),
    scenario(
        "Rejected actions and independent games",
        """
            import copy

            state = new_game()
            other = new_game()
            original = copy.deepcopy(state)
            for command in (
                "eat nope",
                "eat 0",
                "eat -1",
                "eat 99",
                "deliver",
                "gather",
                "nonsense",
            ):
                step(state, command)
            unchanged = __expect__("state", state, original, "==")
            step(state, "eat 1")
            result = (
                unchanged
                and __expect__("other", other, original, "==")
                and __expect__(
                    "state['supplies']['food']", state["supplies"]["food"], 1, "=="
                )
            )
        """,
        "Validate before updating state and create new nested collections for each game.",
    ),
    scenario(
        "Delivery cannot be claimed twice",
        """
            state = new_game()
            state["supplies"]["wood"] = 3
            step(state, "deliver")
            second = step(state, "deliver")
            result = __expect__(
                "Wood remaining", state["supplies"]["wood"], 1, "=="
            ) and __expect__("second", second, "Mira already has her wood.", "==")
        """,
        "Check completion before spending the supplies again.",
    ),
)
M4 = milestone(
    chapter="functions-and-input",
    title="Help the first resident",
    capability="quests",
    requires=("arrival", "pack", "outpost"),
    base=M3.lesson.solution_files,
    story=(
        "Mira needs two pieces of wood to mend the beacon frame. Your game now "
        "supports a small, complete quest."
    ),
    teaching="## Separate a rule from the conversation\n\n"
    "A reusable operation returns text; the input loop prints it. "
    "For example, `def greeting(name): return 'Hello, ' + name` lets a caller use the "
    "message without printing immediately. Keep game state in an "
    "argument instead of hidden globals. "
    "Validate a requested amount before subtracting it. A failed conversion raises ValueError; "
    "an exhausted input stream raises EOFError.\n\n"
    "This milestone replaces the old top-level loop with functions, "
    "while retaining travel and gathering.",
    requirements="In `game.py`, implement `new_game()` returning a fresh dictionary with "
    "`location='outpost'`, `supplies={'food': 2, 'rope': 1, 'wood': 0}`, `quest='open'`, "
    "and `turn=0`. `describe(state)` returns `Location: LOCATION`. "
    "`step(state, command)` strips whitespace and lowercases the command, updates state "
    "only for valid actions, and returns a message without printing. Retain look, travel "
    "(`outpost`, `forest`, `ridge`), gather, inventory, and their previous messages. "
    "Travel, successful gathering, eating, and first delivery each add "
    "one turn; other actions do not.\n\n"
    "`deliver` at the outpost with at least two wood consumes two, sets quest to `done`, "
    "and returns `Mira repairs the beacon frame.`. An already completed quest returns "
    "`Mira already has her wood.`; otherwise return `Bring two wood to Mira at the outpost.`. "
    "`eat N` accepts a positive integer no larger than available food, subtracts it, and "
    "returns `Shared a meal.`. Invalid or unavailable amounts leave all state unchanged "
    "and return a helpful message. Unknown commands return `Unknown command.`.\n\n"
    "`main()` creates a game, prints a title and command guide, loops over input and prints "
    "step's result, and ends on a normalized quit command or EOF. Finish with `Until next time.`. "
    "Call main at the bottom; quiet imports are introduced in the modules chapter.",
    reference={"game.py": ENGINE},
    checks=CORE_CHECKS,
    repair_instructions="Repair `transfer(stock, requested='1')` for a separate supply desk. "
    "stock is a dictionary with integer `food`. Convert requested text to a positive integer. "
    "Return `False` without any mutation for malformed, zero, negative, or excessive requests. "
    "For a valid request, subtract food and return `True`. The default request transfers one. "
    "Do not print and do not hide errors unrelated to number conversion.",
    repair_reference="""
        def transfer(stock, requested="1"):
            try:
                amount = int(requested)
            except ValueError:
                return False
            if amount <= 0 or amount > stock["food"]:
                return False
            stock["food"] -= amount
            return True
    """,
    repair_broken="""
        def transfer(stock, requested="1"):
            amount = int(requested)
            stock["food"] -= amount
            if amount < 0 or stock["food"] < 0:
                return False
            return True
    """,
    repair_checks=(
        scenario(
            "Invalid transfers preserve stock",
            """
                stock = {"food": 3}
                replies = [transfer(stock, value) for value in ("bad", "0", "-2", "4")]
                result = (
                    __expect__("replies", replies, [False] * 4, "==")
                    and __expect__("stock", stock, {"food": 3}, "==")
                    and (transfer(stock) is True)
                    and __expect__("stock['food']", stock["food"], 2, "==")
                )
            """,
            "Finish validation before subtracting food; catch ValueError for invalid text.",
        ),
    ),
    hints=(
        "Extract state creation and returned messages before changing quest behavior.",
        "Use a separate check for already completed quests before consuming resources.",
        "Try converting the amount, validate its range, then make the state change.",
    ),
    repair_hints=(
        "Inspect stock after a failed request, not just the returned boolean.",
        "Conversion, range validation, and mutation belong in that order.",
    ),
    minutes=35,
)
FOUNDATIONS = (M1, M2, M3, M4)
