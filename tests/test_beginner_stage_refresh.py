import pytest

from pytuitor_web.beginner_course import LESSONS
from pytuitor_web.beginner_stage_refresh import BUILD_INSTRUCTIONS, REPAIR_STAGES
from pytuitor_web.curriculum import default_input
from pytuitor_web.runner import execute

EXCLUDED = {
    "first-light",
    "names-and-voices",
    "numbers-from-input",
    "decimal-measurements",
    "choose-a-door",
}
OWNED = tuple(lesson for lesson in LESSONS if lesson.id not in EXCLUDED)


def test_refresh_covers_exact_owned_units_with_explicit_stage_contracts():
    assert len(OWNED) == 38
    assert set(BUILD_INSTRUCTIONS) == set(REPAIR_STAGES) == {lesson.id for lesson in OWNED}
    for lesson in OWNED:
        build = lesson.stage_contract("build")
        repair = lesson.stage_contract("repair")
        assert build.instructions and repair.instructions
        assert isinstance(build.instructions, str) and isinstance(repair.instructions, str)
        assert lesson.revision > 4
        for stage in (build, repair):
            assert set(stage.files) == set(stage.starter_files) == set(stage.reference_files)
        assert all(source == "" for source in build.starter_files.values())
        assert build.reference_files != repair.reference_files
        assert not any(
            line.strip() in {"## Build", "## Repair", "## Exercise"}
            for line in lesson.body.splitlines()
        )


@pytest.mark.parametrize("lesson", OWNED, ids=lambda lesson: lesson.id)
async def test_each_refreshed_stage_reference_passes(lesson):
    for stage_name in ("build", "repair"):
        stage = lesson.stage_contract(stage_name)
        result = await execute(
            lesson,
            stage.reference_files[lesson.entrypoint],
            default_input(lesson, stage_name),
            files=stage.reference_files,
            stage=stage,
        )
        assert result.passed, (lesson.id, stage_name, result.error, result.checks)


@pytest.mark.parametrize("lesson", OWNED, ids=lambda lesson: lesson.id)
async def test_repair_starter_fails_and_build_reference_does_not_transfer(lesson):
    repair = lesson.stage_contract("repair")
    broken = await execute(
        lesson,
        repair.starter_files[lesson.entrypoint],
        default_input(lesson, "repair"),
        files=repair.starter_files,
        stage=repair,
    )
    assert not broken.passed
    assert any(not item["passed"] for item in broken.checks)

    build = lesson.stage_contract("build")
    copied = await execute(
        lesson,
        build.reference_files[lesson.entrypoint],
        default_input(lesson, "repair"),
        files=build.reference_files,
        stage=repair,
    )
    assert not copied.passed
