"""Authored debugging scope guidance, not measured learner completion times."""

# Short concepts ask for a focused investigation; larger protocols keep their full scenario.
FOCUSED = frozenset(
    {
        "first-light",
        "names-and-voices",
        "numbers-from-input",
        "decimal-measurements",
        "choose-a-door",
        "small-superpowers",
        "clean-labels",
        "function-options",
        "handle-invalid-input",
        "objects-not-boxes",
        "python-expressions",
        "call-contracts",
    }
)

CHAPTER_FOCUS = {
    "first-programs": "Trace the values and the printed result.",
    "lists-and-sets": "Compare the collection before and after each operation.",
    "loops-and-dictionaries": "Trace one iteration, then a repeated or empty case.",
    "functions-and-input": "Follow the arguments, return value, and boundary cases.",
    "files-and-data": "Check what is read, written, and preserved.",
    "text-patterns": "Compare a valid match with a near miss.",
    "modules-and-library-tools": "Check the library call and its edge cases.",
    "dates-and-times": "Test a calendar boundary as well as an ordinary date.",
    "collection-tools": "Check ordering, repeated items, and empty input.",
    "classes-and-tested-tools": "Follow instance state through successful and refused operations.",
    "careful-automation": "Check refusal and preview behavior before changes are applied.",
    "python-semantics": "Follow object identity, lifetime, and mutation.",
    "recursion-and-callables": "Trace a base case and one nested call.",
    "decorators": "Check forwarding, returned values, and preserved metadata.",
    "iterators-and-streaming": "Follow consumption one item at a time.",
    "exceptions-and-contexts": "Compare success, failure, and cleanup paths.",
    "dataclasses-and-types": "Check each instance, its fields, and validation boundaries.",
    "object-protocols-and-testing": "Exercise the protocol through its public operations.",
    "async-work": "Trace results, cancellation, and cleanup around each await.",
    "distributable-tools": "Check imports and explicit command arguments independently.",
    "python-machinery": "Trace lookup and binding at the class and instance levels.",
    "packages-and-web": "Compare a success, an error status, and a missing response.",
}


def repair_guidance(lesson):
    if lesson.id in FOCUSED:
        scope, minutes = "Focused repair", "3-5"
    elif lesson.project:
        scope, minutes = "Scenario repair", "8-12"
    else:
        scope, minutes = "Concept repair", "5-8"
    focus = CHAPTER_FOCUS[lesson.chapter_id]
    return f"{scope} · allow about {minutes} minutes, at your own pace. {focus}"
