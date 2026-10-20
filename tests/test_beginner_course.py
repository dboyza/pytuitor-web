"""Behavioral checks for the complete beginner course."""

import ast
import re

import pytest

from pytuitor_web.beginner_course import CHAPTERS, LESSONS
from pytuitor_web.runner import execute


def test_beginner_course_has_six_coherent_chapters():
    assert len(LESSONS) == 43
    assert not any(lesson.project for lesson in LESSONS)
    seen = set()
    for lesson in LESSONS:
        assert set(lesson.prerequisites) <= seen
        seen.add(lesson.id)
        assert lesson.starter == ""
        assert lesson.body.strip()
        assert len(lesson.hints) >= 2
    for chapter in CHAPTERS:
        units = [lesson for lesson in LESSONS if lesson.chapter_id == chapter.id]
        assert len(units) >= 5
    assert any(len(lesson.files) > 1 for lesson in LESSONS)


@pytest.mark.parametrize("lesson", LESSONS, ids=lambda lesson: lesson.id)
async def test_beginner_reference_passes_and_repair_has_a_real_defect(lesson):
    reference = await execute(lesson, lesson.solution, lesson.stdin, files=lesson.solution_files)
    assert reference.passed, (lesson.id, reference.error, reference.checks)
    repair = await execute(lesson, lesson.repair, lesson.stdin, files=lesson.repair_files)
    assert not repair.passed, lesson.id


def test_beginner_worked_examples_have_valid_python_syntax():
    for lesson in LESSONS:
        for block in re.findall(r"```python\n(.*?)```", lesson.body, re.DOTALL):
            ast.parse(block, filename=lesson.id + ".md")
