"""Unified course catalog; authoring provenance does not determine navigation."""

from dataclasses import replace

from pytuitor_web.beginner_course import CHAPTERS as BEGINNER_CHAPTERS
from pytuitor_web.beginner_course import LESSONS as BEGINNER_LESSONS
from pytuitor_web.course_map import CHAPTER_UNITS
from pytuitor_web.course_map import CHAPTERS as CHAPTERS
from pytuitor_web.course_map import SECTIONS as SECTIONS
from pytuitor_web.experienced_course import CHAPTERS as EXPERIENCED_CHAPTERS
from pytuitor_web.experienced_course import LESSONS as EXPERIENCED_LESSONS
from pytuitor_web.legacy import LESSONS as LEGACY_LESSONS
from pytuitor_web.legacy import default_input as legacy_input
from pytuitor_web.models import Check as Check
from pytuitor_web.models import Lesson as Lesson
from pytuitor_web.project_catalog import BY_CHAPTER, MILESTONES

_AUTHORED_LESSONS = (*BEGINNER_LESSONS, *EXPERIENCED_LESSONS)
_AUTHORED_BY_ID = {lesson.id: lesson for lesson in _AUTHORED_LESSONS}


def _assemble_lessons() -> tuple[Lesson, ...]:
    units = []
    for chapter in CHAPTERS:
        previous = tuple(CHAPTER_UNITS[item][-1] for item in chapter.prerequisites)
        for identifier in CHAPTER_UNITS[chapter.id]:
            units.append(
                replace(_AUTHORED_BY_ID[identifier], chapter_id=chapter.id, prerequisites=previous)
            )
            previous = (identifier,)
    return tuple(units)


LESSONS = _assemble_lessons()

BY_ID = {
    lesson.id: lesson
    for lesson in (*LEGACY_LESSONS, *LESSONS, *(item.lesson for item in MILESTONES))
}
ACTIVITIES = tuple(
    unit
    for chapter in CHAPTERS
    for unit in (
        *(lesson for lesson in LESSONS if lesson.chapter_id == chapter.id),
        BY_CHAPTER[chapter.id].lesson,
    )
)
CONCEPTS = tuple(dict.fromkeys(c for lesson in LESSONS for c in lesson.concepts))
TRACKS = {"beginner": "Beginner", "experienced": "Experienced", "custom": "Custom"}


def track_lessons(track: str) -> list[Lesson]:
    """Legacy authoring provenance, retained for imports and old profile tools."""
    return [lesson for lesson in _AUTHORED_LESSONS if track == "custom" or lesson.track == track]


def track_chapters(track: str):
    """Legacy authoring chapters; use CHAPTERS for learner navigation."""
    return [
        chapter
        for chapter in (*BEGINNER_CHAPTERS, *EXPERIENCED_CHAPTERS)
        if track == "custom" or chapter.track == track
    ]


def chapter_lessons(chapter_id: str) -> list[Lesson]:
    return [lesson for lesson in LESSONS if lesson.chapter_id == chapter_id]


def chapter_activities(chapter_id: str) -> list[Lesson]:
    """Recommended lessons followed by the cumulative milestone."""
    return [lesson for lesson in ACTIVITIES if lesson.chapter_id == chapter_id]


def default_input(lesson: Lesson, stage: str = "build") -> str:
    contract = lesson.stage_contract(stage)
    has_override = (stage == "build" and lesson.build_stage is not None) or (
        stage == "repair" and lesson.repair_stage is not None
    )
    return contract.stdin if has_override else contract.stdin or legacy_input(lesson)
