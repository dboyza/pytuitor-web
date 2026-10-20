"""Small constructors for fully authored Lantern Reach milestones."""

import ast

from pytuitor_web.models import Check, Lesson, ProjectMilestone, StageContract, code

PROJECT_ID = "lantern-reach"


def public_names(source: str, local_modules=()) -> tuple[str, ...]:
    """Name the authored API for explicit reference-launcher imports."""
    names = []
    for statement in ast.parse(source).body:
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not statement.name.startswith("_"):
                names.append(statement.name)
        elif isinstance(statement, ast.ImportFrom) and statement.module in local_modules:
            names.extend(alias.asname or alias.name for alias in statement.names)
    return tuple(dict.fromkeys(names))


def api_import(module: str, names: tuple[str, ...]) -> str:
    return f"from {module} import (\n" + "".join(f"    {name},\n" for name in names) + ")\n"


def scenario(label: str, source: str, nudge: str) -> Check:
    script = code(source)
    return Check(
        label,
        f"(exec({script!r}, globals()), result)[1]",
        True,
        nudge,
        description=label,
    )


def milestone(
    *,
    chapter: str,
    title: str,
    story: str,
    teaching: str,
    requirements: str,
    reference: dict[str, str],
    checks: tuple[Check, ...],
    repair_instructions: str,
    repair_reference: str,
    repair_broken: str,
    repair_checks: tuple[Check, ...],
    hints: tuple[str, ...],
    repair_hints: tuple[str, ...],
    base: dict[str, str] | None = None,
    requires: tuple[str, ...] = (),
    capability: str,
    stdin: str = "quit\n",
    minutes: int = 25,
) -> ProjectMilestone:
    base = dict(base or {"game.py": ""})
    files = tuple(reference)
    starter = {name: base.get(name, "") for name in files}
    build = StageContract(
        instructions=requirements,
        checks=checks,
        hints=hints,
        stdin=stdin,
        files=files,
        starter_files=starter,
        reference_files=reference,
    )
    repair = StageContract(
        instructions=repair_instructions,
        checks=repair_checks,
        hints=repair_hints,
        stdin="",
        files=("game.py",),
        starter_files={"game.py": code(repair_broken)},
        reference_files={"game.py": code(repair_reference)},
    )
    lesson = Lesson(
        id=f"reach-{capability}",
        track="project",
        title=title,
        subtitle=story,
        minutes=minutes,
        concepts=(capability,),
        body=(
            f"# Lantern Reach: {title}\n\n{story}\n\n"
            "## Your growing game\n\n"
            "Extend your previous working game using the requirements in the Extend tab. "
            "Your source stays yours: different implementations and "
            "extra creative details are welcome. "
            "Keep the documented commands and behavior so future chapters can build on them.\n\n"
            f"{teaching}\n\n"
            "## Check and continue\n\n"
            "Run to play, then Check to test the stated behavior. "
            "A passing Extend saves a working checkpoint. "
            "Repair is a separate incident and cannot overwrite that checkpoint. "
            "Complete both stages, then choose Next.\n\n"
            "Game saves you generate stay in the workspace folder and appear under Other files. "
            "The Your game page lets you replay working versions or download a standalone game."
        ),
        repair=repair.starter_files["game.py"],
        checks=checks,
        hints=hints,
        prediction="",
        choices=(),
        answer=0,
        explanation="",
        solution=reference["game.py"],
        project=True,
        revision=1,
        chapter_id=chapter,
        entrypoint="game.py",
        files=files,
        solution_files=reference,
        repair_files=repair.starter_files,
        stdin=stdin,
        build_stage=build,
        repair_stage=repair,
        project_id=PROJECT_ID,
    )
    return ProjectMilestone(lesson, requires, (*requires, capability), base)
