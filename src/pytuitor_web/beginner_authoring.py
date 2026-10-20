"""Small constructors for beginner stage authoring."""

from dataclasses import replace

from pytuitor_web.models import Check, StageContract, code


def _check(
    label: str,
    expression: str,
    expected: object,
    *,
    stdin: str | None = None,
    output: str | None = None,
    nudge: str = "",
    description: str | None = None,
) -> Check:
    return Check(
        label,
        expression,
        expected,
        nudge,
        stdin=stdin,
        expected_output=output,
        description=description
        or (label if "lambda" in expression or "__import__" in expression else expression),
    )


def _scenario_check(
    label: str, script: str, expected: object, *, description: str, nudge: str
) -> Check:
    """Run a multi-step check and inspect result in the worker's fresh namespace."""
    return _check(
        label,
        f"(exec({code(script)!r}), result)[1]",
        expected,
        description=description,
        nudge=nudge,
    )


def _stage(
    instructions: str,
    reference: str,
    starter: str,
    checks: tuple[Check, ...],
    hints: tuple[str, ...],
    *,
    stdin: str = "",
    files: tuple[str, ...] = ("lesson.py",),
    starter_files: dict[str, str] | None = None,
    reference_files: dict[str, str] | None = None,
) -> StageContract:
    if starter_files is None:
        starter_files = {"lesson.py": code(starter)}
    if reference_files is None:
        reference_files = {"lesson.py": code(reference)}
    return StageContract(
        instructions=instructions,
        checks=tuple(check if check.nudge else replace(check, nudge=hints[0]) for check in checks),
        hints=tuple(hints),
        stdin=stdin,
        files=tuple(files),
        starter_files=starter_files,
        reference_files=reference_files,
    )
