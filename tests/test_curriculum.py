import pytest

from pytuitor_web.curriculum import LESSONS, default_input
from pytuitor_web.runner import execute


@pytest.mark.parametrize("lesson", LESSONS, ids=lambda lesson: lesson.id)
async def test_reference_solution_meets_contract(lesson):
    result = await execute(
        lesson, lesson.solution, default_input(lesson), files=lesson.solution_files
    )
    assert result.passed, (result.error, result.checks, result.output)


@pytest.mark.parametrize("lesson", LESSONS, ids=lambda lesson: lesson.id)
async def test_starter_needs_work(lesson):
    result = await execute(lesson, lesson.starter, default_input(lesson))
    assert not result.passed


async def test_timeout_and_output_limit():
    result = await execute(LESSONS[0], "while True: pass", timeout=0.3)
    assert "Stopped" in result.error
    result = await execute(LESSONS[0], "while True: print('x' * 1000)")
    assert "limit" in result.error.lower()
    assert len(result.output) <= 65536


async def test_errors_are_actionable_and_next_run_recovers():
    result = await execute(LESSONS[0], 'print("oops)')
    assert "SyntaxError" in result.error
    assert "lesson.py" in result.error
    result = await execute(LESSONS[0], "input()")
    assert "type it in the console" in result.error
    result = await execute(LESSONS[0], LESSONS[0].solution)
    assert result.passed


async def test_run_does_not_mark_passing_checks():
    result = await execute(LESSONS[0], LESSONS[0].solution, check=False)
    assert result.output == "Hello, world!\n13\n"
    assert not result.passed
    assert result.checks == []


def _course_order():
    from pytuitor_web.course_map import _OUTLINE
    from pytuitor_web.curriculum import BY_ID

    return [BY_ID[unit] for chapter in _OUTLINE for unit in chapter[5]]


def test_each_bold_term_is_introduced_only_once_in_course_order():
    import re

    introduced = {}
    for lesson in _course_order():
        for term in re.findall(r"\*\*([^*]+)\*\*", lesson.body):
            key = term.lower().removesuffix("s")
            assert key not in introduced, (term, introduced.get(key), lesson.id)
            introduced[key] = lesson.id


def test_prose_cites_lessons_by_their_visible_titles():
    from pytuitor_web.curriculum import BY_ID

    lessons = _course_order()
    titles = {lesson.title for lesson in BY_ID.values()}
    # Single-word IDs such as "comprehensions" are ordinary words, not internal names.
    internal_names = {
        lesson.id.replace("-", " ").capitalize() for lesson in lessons if "-" in lesson.id
    } - titles
    for lesson in lessons:
        body = lesson.body
        for title in sorted(titles, key=len, reverse=True):
            body = body.replace(title, "")
        for name in internal_names:
            assert name not in body, (lesson.id, name)
