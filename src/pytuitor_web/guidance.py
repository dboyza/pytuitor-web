"""Plain-English next steps for common Python errors, without rewriting learner code."""


def error_guidance(error: str) -> str:
    """Explain the next debugging action without rewriting the learner's program."""
    for kind, guidance in (
        (
            "IndentationError",
            "Indentation groups statements. Use four spaces inside each if, loop, function or "
            "class, and align statements in the same block.",
        ),
        (
            "SyntaxError",
            "Python could not read this statement. Check the reported line and the one above "
            "it for missing colons, closing quotes or brackets.",
        ),
        (
            "NameError",
            "This name has no value yet. Check its spelling and whether the assignment or "
            "import runs before this line.",
        ),
        (
            "TypeError",
            "An operation received a value it cannot use. Check the types and the function's "
            "expected arguments; input() always returns text.",
        ),
        (
            "ValueError",
            "The type was acceptable but the value was not. Inspect the input and the "
            "conversion or validation on the reported line.",
        ),
        (
            "IndexError",
            "That position is outside the sequence. Positions begin at zero and end at "
            "len(sequence) - 1; also consider an empty sequence.",
        ),
        (
            "KeyError",
            "That key is missing from the dictionary. Check spelling and decide how absent "
            "data should be handled.",
        ),
        (
            "ModuleNotFoundError",
            "Python could not find an imported module. Check the project file name and import "
            "spelling. Course exercises use the standard library plus the included requests and "
            "pytest packages.",
        ),
        (
            "FileNotFoundError",
            "This run starts with your saved project files in a fresh working directory. "
            "Check the relative path and create any required data file.",
        ),
        (
            "AssertionError",
            "An assertion found a result that did not meet its condition. Compare the actual "
            "value with the requirement before changing the test.",
        ),
    ):
        if kind in error:
            return guidance
    return ""
