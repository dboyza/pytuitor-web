from collections import Counter
from dataclasses import fields, replace

import pytest

from pytuitor_web.beginner_course import LESSONS as BEGINNER_LESSONS
from pytuitor_web.curriculum import (
    CHAPTERS,
    CONCEPTS,
    LESSONS,
    SECTIONS,
    chapter_lessons,
    default_input,
)
from pytuitor_web.experienced_course import LESSONS as EXPERIENCED_LESSONS
from pytuitor_web.models import Lesson, StageContract
from pytuitor_web.runner import execute


def test_catalog_has_complete_chapters_and_ordered_prerequisites():
    assert len(LESSONS) == len({lesson.id for lesson in LESSONS}) == 84
    assert not any(lesson.project for lesson in LESSONS)
    assert Counter(lesson.track for lesson in LESSONS) == {"beginner": 43, "experienced": 41}
    assert len(CHAPTERS) == 22
    assert len(SECTIONS) == 6
    assert [section.optional for section in SECTIONS] == [False, False, False, True, True, True]
    seen = set()
    for lesson in LESSONS:
        assert set(lesson.prerequisites) <= seen, lesson.id
        assert lesson.body.strip() and lesson.checks and lesson.hints
        assert lesson.entrypoint in lesson.files
        assert set(lesson.concepts) <= set(CONCEPTS)
        seen.add(lesson.id)
    seen_chapters = set()
    for chapter in CHAPTERS:
        units = chapter_lessons(chapter.id)
        assert 2 <= len(units) <= 6
        assert chapter.section_id in {section.id for section in SECTIONS}
        assert set(chapter.prerequisites) <= seen_chapters
        seen_chapters.add(chapter.id)
    assert tuple(unit for chapter in CHAPTERS for unit in chapter_lessons(chapter.id)) == LESSONS
    section_order = [section.id for section in SECTIONS]
    positions = [section_order.index(chapter.section_id) for chapter in CHAPTERS]
    assert positions == sorted(positions)


def test_reorganization_preserves_every_authored_exercise_contract():
    authored = {lesson.id: lesson for lesson in (*BEGINNER_LESSONS, *EXPERIENCED_LESSONS)}
    assert {lesson.id for lesson in LESSONS} == authored.keys()
    unchanged_fields = {field.name for field in fields(Lesson)} - {
        "chapter_id",
        "prerequisites",
        "concepts",
    }
    for lesson in LESSONS:
        for name in unchanged_fields:
            assert getattr(lesson, name) == getattr(authored[lesson.id], name), (lesson.id, name)


def test_specialties_have_relevant_independent_preparation():
    chapters = {chapter.id: chapter for chapter in CHAPTERS}
    assert "async-work" not in chapters["distributable-tools"].prerequisites
    assert "distributable-tools" not in chapters["python-machinery"].prerequisites
    assert "iterators-and-streaming" in chapters["exceptions-and-contexts"].prerequisites
    assert "decorators" in chapters["exceptions-and-contexts"].prerequisites
    assert "classes-and-tested-tools" in chapters["exceptions-and-contexts"].prerequisites
    optional = {section.id for section in SECTIONS if section.optional}
    for chapter in CHAPTERS:
        if chapter.section_id not in optional:
            assert all(chapters[item].section_id not in optional for item in chapter.prerequisites)
    assert not chapter_lessons("missing")


def test_stage_contracts_have_required_files_and_content():
    for lesson in LESSONS:
        for stage_name in ("build", "repair"):
            contract = lesson.stage_contract(stage_name)
            assert lesson.entrypoint in contract.files
            assert contract.checks and contract.hints
            assert contract.starter_files
            assert contract.reference_files
            assert set(contract.files) <= set(contract.starter_files)
            assert set(contract.files) <= set(contract.reference_files)


@pytest.mark.parametrize(
    "identifier",
    (
        "first-light",
        "names-and-voices",
        "numbers-from-input",
        "decimal-measurements",
        "choose-a-door",
    ),
)
async def test_foundations_have_independent_stage_references(identifier):
    lesson = next(item for item in LESSONS if item.id == identifier)
    build = lesson.stage_contract("build")
    repair = lesson.stage_contract("repair")
    assert build.instructions and repair.instructions
    assert build.reference_files != repair.reference_files
    for stage_name, contract in (("build", build), ("repair", repair)):
        result = await execute(
            lesson,
            contract.reference_files[lesson.entrypoint],
            default_input(lesson, stage_name),
            files=contract.reference_files,
            stage=contract,
        )
        assert result.passed, (identifier, stage_name, result.error, result.checks)
    broken = await execute(
        lesson,
        repair.starter_files[lesson.entrypoint],
        default_input(lesson, "repair"),
        files=repair.starter_files,
        stage=repair,
    )
    assert not broken.passed


def test_explicit_empty_stage_values_do_not_fall_back_to_build_defaults():
    lesson = next(item for item in LESSONS if item.id == "names-and-voices")
    current = lesson.stage_contract("repair")
    explicit = replace(
        lesson,
        repair_stage=StageContract(
            checks=current.checks,
            hints=(),
            stdin="",
            files=current.files,
            starter_files=current.starter_files,
            reference_files=current.reference_files,
        ),
    )
    assert explicit.stage_contract("repair").hints == ()
    assert default_input(explicit, "repair") == ""


def test_every_chapter_has_an_optional_conceptual_checkpoint():
    for chapter in CHAPTERS:
        questions = [
            lesson for lesson in LESSONS if lesson.chapter_id == chapter.id and lesson.choices
        ]
        assert questions, chapter.id
        for lesson in questions:
            assert lesson.prediction and lesson.explanation
            assert 0 <= lesson.answer < len(lesson.choices)
