import pytest

from pytuitor_web.experienced_course import CHAPTERS, LESSONS
from pytuitor_web.legacy import default_input
from pytuitor_web.runner import execute


def test_experienced_course_has_seven_complete_chapters():
    assert len(LESSONS) == 41
    assert len({lesson.id for lesson in LESSONS}) == 41
    assert not any(lesson.project for lesson in LESSONS)
    seen = set()
    for chapter in CHAPTERS:
        units = [lesson for lesson in LESSONS if lesson.chapter_id == chapter.id]
        assert len(units) >= 3
        for lesson in units:
            assert set(lesson.prerequisites) <= seen
            assert not lesson.starter
            assert lesson.body and lesson.hints
            seen.add(lesson.id)
    assert any(len(lesson.files) > 1 for lesson in LESSONS)


@pytest.mark.parametrize("lesson", LESSONS, ids=lambda lesson: lesson.id)
async def test_experienced_references_and_repairs(lesson):
    correct = await execute(
        lesson, lesson.solution, default_input(lesson), files=lesson.solution_files
    )
    assert correct.passed, (correct.error, correct.checks)
    broken = await execute(lesson, lesson.repair, default_input(lesson), files=lesson.repair_files)
    assert not broken.passed, lesson.id


@pytest.mark.parametrize("lesson_id", ["metaclasses", "async-streams"])
async def test_deep_checks_reject_subtle_contract_regressions(lesson_id):
    lesson = next(lesson for lesson in LESSONS if lesson.id == lesson_id)
    if lesson_id == "metaclasses":
        source = lesson.solution.replace(
            '                raise ValueError("Duplicate kind")',
            "                mcls.registry[key] = cls\n"
            '                raise ValueError("Duplicate kind")',
        )
    else:
        source = lesson.solution.replace("if cleaned:", "if cleaned and cleaned not in result:")
    assert source != lesson.solution
    result = await execute(lesson, source)
    assert not result.passed
    assert not result.error, "The mutation must fail behaviorally, not because it cannot run."
