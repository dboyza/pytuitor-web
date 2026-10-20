"""A concrete game connection for every focused teaching lesson."""

GAME_CONNECTIONS = {
    "first-light": "Print the explorer's first glimpse of Lantern Reach.",
    "names-and-voices": "Ask for the explorer's name and keep it for the welcome scene.",
    "numbers-from-input": "Turn a typed supply count into a number you can calculate with.",
    "decimal-measurements": "Show a trail distance with a consistent number of decimal places.",
    "choose-a-door": "Choose a route based on both the player's choice and their supplies.",
    "pack-your-bag": "Keep the pack in order and display every item, including repeated supplies.",
    "list-positions": "Inspect a pack's positions without assuming it contains any items.",
    "summary-builtins": "Total the pack's supplies and warn when any supply has run out.",
    "tuples-and-sets": "Distinguish the supplies the explorer carries from the kinds they own.",
    "comparing-sets": "Find required expedition equipment that is missing from the pack.",
    "loop-helpers": "Number choices so the player can follow an ordered set of options.",
    "nested-collections": "Traverse grouped expedition supplies without losing empty groups.",
    "word-counts": "Associate each supply name with the amount stored at the outpost.",
    "dictionary-pairs": "List every stored supply with its amount in a single loop.",
    "editing-collections": "Update the pack when the explorer gathers or spends supplies.",
    "repeat-until-done": "Keep reading game commands until the player decides to leave.",
    "small-superpowers": "Separate reusable game rules from the input-and-print conversation.",
    "clean-labels": "Accept a command even when the player adds spaces or different casing.",
    "function-options": "Give game operations explicit options with sensible defaults.",
    "handle-invalid-input": "Reject an invalid food amount without consuming any supplies.",
    "text-files": "Keep an expedition journal after the current run ends.",
    "paths-and-folders": "Locate game saves deliberately instead of guessing path separators.",
    "json-records": "Save the explorer's nested game state and restore it on a later visit.",
    "csv-tables": "Exchange a supply ledger even when an item name contains a comma.",
    "regex-validation": "Decide whether a complete trail-marker code has the required form.",
    "regex-transformations": "Extract marker codes from a note without changing surrounding prose.",
    "your-own-modules": "Move game rules into a reusable engine while keeping a small launcher.",
    "numeric-tools": "Summarize the outpost's supply counts with a meaningful statistic.",
    "repeatable-randomness": "Repeat a scouting encounter without disturbing other random choices.",
    "command-line-options": "Let players choose an explorer name and a repeatable expedition seed.",
    "dates-and-deadlines": "Advance an in-game calendar across month boundaries correctly.",
    "date-time-formats": "Read a meeting time in a documented format for the supply gathering.",
    "comprehensions": "Select unfinished residents' requests without changing the original list.",
    "counting-and-grouping": "Combine repeated deliveries into totals for the supply depot.",
    "queues-with-deque": "Serve residents in arrival order while keeping the waiting queue intact.",
    "your-first-class": "Give each expedition its own state and related command operations.",
    "object-principles": (
        "Let different kinds of residents answer the same request in their own way."
    ),
    "named-states": "Name a quest's allowed states instead of scattering arbitrary strings.",
    ("tests-for-your-code"): (
        "Prove a quest cannot award its reward twice or share another game's pack."
    ),
    "validate-boundaries": "Check an archive plan before touching any journal files.",
    "copy-with-care": "Preview a journal backup and refuse to overwrite an existing copy.",
    ("python-expressions"): (
        "Keep a valid zero or empty choice instead of replacing every falsy value."
    ),
    ("objects-not-boxes"): (
        "Try a different route without sharing the original expedition's nested pack."
    ),
    "call-contracts": "Make optional game-state replacements clear at their call sites.",
    ("collection-idioms"): (
        "Preserve the order and ownership of expedition records while transforming them."
    ),
    "pattern-matching": "Recognize each command's shape, such as take followed by any items.",
    "recursion-basics": "Explore a cave branch by solving the same problem for a smaller branch.",
    ("recursive-collections"): (
        "Visit every named location in a nested cave map, including empty branches."
    ),
    "callable-tools": "Let a caller choose how route names should be ranked.",
    ("functional-pipelines"): (
        "Compose small route transformations without hiding their order or effects."
    ),
    "functions-with-memory": "Wrap a field action while preserving its arguments and result.",
    ("decorator-factories"): (
        "Configure action recording and understand the order of stacked wrappers."
    ),
    "lazy-by-design": "Read chronicle events only when the player asks for the next result.",
    "iterator-tools": "Stop a chronicle report after enough matching events have been found.",
    ("iterator-recipes"): (
        "Combine and bound event streams without eagerly loading an entire expedition."
    ),
    "adjacent-groups": "Recognize consecutive runs of related expedition events.",
    ("exception-boundaries"): (
        "Report a station-specific failure while retaining the underlying cause."
    ),
    "logging-basics": "Keep a maintainer's log of skipped commands without cluttering the story.",
    ("context-practice"): (
        "Restore the explorer's previous location even when a temporary visit fails."
    ),
    ("managed-contexts"): (
        "Give a station visit explicit entry and exit behavior through the context protocol."
    ),
    "ready-to-ship": "State field-record types and test the behavior at the record boundary.",
    "data-models": "Represent a named supply record with a small data class.",
    ("dataclass-lifecycle"): (
        "Give each record independent notes and validate every updated instance."
    ),
    "sqlite-records": "Keep the outpost's supply ledger in a database that survives restarts.",
    "typed-contracts": "Describe the alternatives accepted by an expedition API precisely.",
    ("practical-object-protocols"): (
        "Make a supply store work naturally with len, iteration, and properties."
    ),
    "class-construction": "Build supply stores through factories that preserve subclasses.",
    ("structural-typing"): (
        "Accept any supply store with the required behavior, including a small test double."
    ),
    ("test-doubles"): (
        "Check report output through an injected writer without printing during the test."
    ),
    "coroutine-basics": "Let independent scout observations make progress cooperatively.",
    "clean-exits": "Close a scouting station on success, failure, or cancellation.",
    "task-groups": "Own all scout tasks until they finish, including siblings of a failed scout.",
    "async-streams": "Receive scouting events through an asynchronous iterator.",
    ("module-boundaries"): (
        "Import the game engine without accidentally starting an interactive expedition."
    ),
    "package-metadata": "Describe how another player can install and launch the exported game.",
    "cli-contracts": "Give help, bad options, and missing story files predictable exit behavior.",
    "resource-paths": "Read the story file selected by the player, including paths with spaces.",
    "descriptors": "Validate a formatter's use count while keeping each instance's state separate.",
    "metaclasses": "Register formatter classes without corrupting the registry on duplicate names.",
    ("method-resolution"): (
        "Let a formatter mixin cooperate with classes added later in the method order."
    ),
    "runtime-inspection": "Describe a formatter's accepted arguments without running it.",
    "installing-packages": "List the packages a shared copy of your game needs to run.",
    "pytest-basics": "Prove the ranger report with pytest, without contacting a real station.",
    "web-requests": "File an expedition report with a ranger station's web API.",
}
