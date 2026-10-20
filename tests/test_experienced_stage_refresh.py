import re

import pytest

from pytuitor_web.experienced_course import LESSONS
from pytuitor_web.runner import execute


def test_experienced_stage_refresh_owns_exactly_41_units():
    assert len(LESSONS) == 41
    assert len({lesson.id for lesson in LESSONS}) == 41
    assert all(lesson.build_stage is not None for lesson in LESSONS)
    assert all(lesson.repair_stage is not None for lesson in LESSONS)
    assert all(
        not re.search(r"^## (?:Build|Repair|Exercise)$", lesson.body, re.MULTILINE)
        for lesson in LESSONS
    )


@pytest.mark.parametrize("lesson", LESSONS, ids=lambda lesson: lesson.id)
async def test_each_stage_is_self_contained_and_cross_stage_specific(lesson):
    build = lesson.stage_contract("build")
    repair = lesson.stage_contract("repair")

    assert build.instructions and repair.instructions
    assert build.checks and repair.checks
    assert build.hints and repair.hints
    assert set(build.files) <= set(build.starter_files)
    assert set(build.files) <= set(build.reference_files)
    assert set(repair.files) <= set(repair.starter_files)
    assert set(repair.files) <= set(repair.reference_files)
    assert build.reference_files != repair.reference_files

    build_result = await execute(
        lesson,
        build.reference_files[lesson.entrypoint],
        files=build.reference_files,
        stage=build,
    )
    assert build_result.passed, (lesson.id, "build", build_result.error, build_result.checks)

    repair_result = await execute(
        lesson,
        repair.reference_files[lesson.entrypoint],
        files=repair.reference_files,
        stage=repair,
    )
    assert repair_result.passed, (lesson.id, "repair", repair_result.error, repair_result.checks)

    broken_result = await execute(
        lesson,
        repair.starter_files[lesson.entrypoint],
        files=repair.starter_files,
        stage=repair,
    )
    assert not broken_result.passed, lesson.id

    build_as_repair = await execute(
        lesson,
        build.reference_files[lesson.entrypoint],
        files=build.reference_files,
        stage=repair,
    )
    assert not build_as_repair.passed, (lesson.id, "Build reference solved Repair")


def test_compatibility_fields_project_build_and_repair_stages():
    for lesson in LESSONS:
        build = lesson.stage_contract("build")
        repair = lesson.stage_contract("repair")
        assert lesson.solution_files == build.reference_files
        assert lesson.repair_files == repair.starter_files
        assert lesson.solution == build.reference_files[lesson.entrypoint]
        assert lesson.repair == repair.starter_files[lesson.entrypoint]
        assert lesson.checks == build.checks
        assert lesson.hints == build.hints
