"""Optional conceptual predictions for chapters that lacked a checkpoint."""

# Prompt, choices, correct index, explanation. These never gate either coding stage.
CHECKPOINTS = {
    "nested-collections": (
        "A loop creates one row list before the loop and appends that same list twice. "
        "If the list changes later, how many stored rows reflect the change?",
        ("Both rows", "Only the most recent row", "Neither row"),
        0,
        "Both entries refer to the same list. Create a new row inside each iteration "
        "when rows must be independent.",
    ),
    "json-records": (
        "Which operation parses JSON text already stored in a string?",
        ("json.load(text)", "json.loads(text)", "json.dumps(text)"),
        1,
        "loads parses a string; load reads a file-like object. dumps serializes a Python value.",
    ),
    "regex-validation": (
        "A pattern describes a complete identifier. Which operation rejects extra text "
        "after an otherwise valid identifier?",
        ("search", "match", "fullmatch"),
        2,
        "fullmatch requires the entire input to match. match checks only the beginning; "
        "search can find a match anywhere.",
    ),
    "your-own-modules": (
        "A reusable module prints a greeting at its top level. What happens on its first import?",
        ("The greeting prints", "Only function definitions run", "Python refuses the import"),
        0,
        "Import executes top-level statements. Put demonstrations under a main guard "
        "so importing a utility stays quiet.",
    ),
    "dates-and-deadlines": (
        "What is one day after 2024-02-28?",
        ("2024-03-01", "2024-02-29", "An invalid date"),
        1,
        "2024 is a leap year. Date arithmetic handles month and leap-year boundaries.",
    ),
    "queues-with-deque": (
        "A queue contains A then B. After popleft(), which item remains at the front?",
        ("A", "B", "Neither"),
        1,
        "popleft removes the oldest item from the left. B becomes the next item.",
    ),
    "your-first-class": (
        "Two instances each create self.items = [] in __init__. Appending to one instance's "
        "list changes which lists?",
        ("Both", "Only that instance's list", "Neither"),
        1,
        "Each constructor call creates a fresh list. Assigning one shared list to both "
        "instances would give different behavior.",
    ),
    "copy-with-care": (
        "A backup destination appeared after an existence check. Which open mode refuses "
        "to overwrite it?",
        ("wb", "ab", "xb"),
        2,
        "Exclusive creation with xb refuses an existing destination at the moment of opening. "
        "A previous existence check cannot prevent a competing writer.",
    ),
    "recursion-basics": (
        "A recursive function calls itself with exactly the same input and has no other exit. "
        "What is missing?",
        ("A second return statement", "Progress toward a base case", "A global variable"),
        1,
        "Each recursive step must approach a terminating base case. Repeating the same "
        "unhandled input cannot finish.",
    ),
    "managed-contexts": (
        "A with body raises ValueError. Its __exit__ returns True. What happens to that error?",
        ("It propagates", "It is suppressed", "The body runs again"),
        1,
        "A truthy __exit__ return suppresses the body's exception. Cleanup alone does not "
        "justify hiding a failure.",
    ),
    "test-doubles": (
        "A primary operation successfully returns None. Should an exception-only fallback run?",
        ("Yes, None means failure", "No, no exception occurred", "Always run both operations"),
        1,
        "A successful result can be falsy. Only the documented exception triggers fallback.",
    ),
    "cli-contracts": (
        "An option is declared with type=int and default=10. "
        "What does parsing ['data.txt', '--limit', '5'] store as limit?",
        ("The string '5'", "The integer 5", "The default 10"),
        1,
        "type converts the command-line text before it is stored. "
        "The default applies only when the option is absent.",
    ),
    "web-requests": (
        "A server answers a GET request with status 404. "
        "Your code calls requests.get but never calls raise_for_status(). What happens?",
        (
            "requests.get raises HTTPError",
            "requests.get returns the response normally",
            "requests retries the request",
        ),
        1,
        "requests.get raises only when no response arrives. A 404 is still a response; "
        "raise_for_status() is what turns an error status into an exception.",
    ),
    "method-resolution": (
        "In multiple inheritance, where does super() look for the next method?",
        (
            "Always in the first declared parent",
            "After the current class in the instance's MRO",
            "In every parent independently",
        ),
        1,
        "super continues along the actual method resolution order. This lets cooperative "
        "methods visit shared ancestors once.",
    ),
}


def apply_checkpoints(lessons):
    """Attach optional predictions in authoring, before catalog reorganization."""
    from dataclasses import replace

    result = []
    for lesson in lessons:
        if lesson.id in CHECKPOINTS:
            prompt, choices, answer, explanation = CHECKPOINTS[lesson.id]
            lesson = replace(
                lesson,
                prediction=prompt,
                choices=choices,
                answer=answer,
                explanation=explanation,
            )
        result.append(lesson)
    return tuple(result)
