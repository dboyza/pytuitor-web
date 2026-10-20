"""Small constructors shared by the experienced chapter authors."""

from dataclasses import replace

from pytuitor_web.legacy import BY_ID as LEGACY
from pytuitor_web.models import Check, Lesson, StageContract, code, lesson_text


def check(
    label,
    expression,
    expected,
    nudge="Compare the actual and expected results for this input.",
):
    return Check(
        label,
        expression,
        expected,
        nudge,
        description=label
        if any(token in expression for token in ("lambda", "exec(", "__import__"))
        else expression,
    )


def unit(
    lesson_id,
    chapter,
    title,
    concept,
    solution,
    checks,
    hints,
    *,
    files=None,
    entrypoint="lesson.py",
):
    solution_files = {name: code(source) for name, source in files[0].items()} if files else None
    return Lesson(
        lesson_id,
        "experienced",
        title,
        concept,
        20,
        (concept,),
        lesson_text(lesson_id),
        "",
        tuple(checks),
        tuple(hints),
        "",
        (),
        0,
        "",
        code(solution),
        revision=4,
        chapter_id=chapter,
        entrypoint=entrypoint,
        files=tuple(solution_files) if solution_files else (entrypoint,),
        solution_files=solution_files,
    )


def legacy(lesson_id, chapter):
    return replace(LEGACY[lesson_id], chapter_id=chapter, revision=4)


def probe(label, source, expected, description, nudge):
    """Keep stateful behavior probes readable in source and in the learner's console."""
    return Check(
        label,
        f"(exec({code(source)!r}, globals()), __probe_result__)[1]",
        expected,
        nudge,
        description=description,
    )


def _check(label, expression, expected, nudge, *, stdin=None, expected_output=None):
    return Check(
        label,
        expression.replace("\n", "\\n"),
        expected,
        nudge,
        stdin=stdin,
        expected_output=expected_output,
        description=label
        if any(token in expression for token in ("lambda", "exec(", "__import__"))
        else expression,
    )


def _probe(label, source, expected, nudge):
    return Check(label, _exec(source), expected, nudge, description=label + ". " + nudge)


def _exec(source, result="result"):
    """Build a readable check expression for a small stateful probe."""
    return f"(exec({code(source)!r}, globals()), {result})[1]"


def _exec_with(source, locals_expression, result="result"):
    """Build a probe expression with a small explicit local environment."""
    return (
        f"(lambda env: (exec({code(source)!r}, globals(), env), "
        f"env[{result!r}])[1])({locals_expression})"
    )


def _repair(instructions, reference, starter, checks, hints, *, files=None):
    reference_files = (
        {"lesson.py": code(reference)}
        if files is None
        else {name: code(source) for name, source in files[0].items()}
    )
    starter_files = (
        {"lesson.py": code(starter)}
        if files is None
        else {name: code(source) for name, source in files[1].items()}
    )
    return StageContract(
        instructions=instructions,
        checks=tuple(checks),
        hints=tuple(hints),
        files=tuple(reference_files),
        starter_files=starter_files,
        reference_files=reference_files,
    )
