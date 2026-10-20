"""Experienced course assembly; contracts live beside their chapter content."""

from dataclasses import replace

from pytuitor_web.checkpoints import apply_checkpoints
from pytuitor_web.content import (
    experienced_composition,
    experienced_concurrency,
    experienced_delivery,
    experienced_design,
    experienced_internals,
    experienced_online,
    experienced_semantics,
)
from pytuitor_web.experienced_stages import apply as apply_stage_refresh
from pytuitor_web.models import Chapter

CHAPTERS = (
    Chapter(
        "python-semantics",
        "experienced",
        "Think in Python",
        "Write clear functions without aliasing or argument surprises.",
    ),
    Chapter(
        "python-composition",
        "experienced",
        "Compose and stream",
        "Compose decorators, lazy pipelines, and reliable resource cleanup.",
    ),
    Chapter(
        "python-design",
        "experienced",
        "Design and verify",
        "Model data, express protocols, and test behavior at boundaries.",
    ),
    Chapter(
        "python-concurrency",
        "experienced",
        "Coordinate async work",
        "Schedule work, preserve order, and clean up on cancellation.",
    ),
    Chapter(
        "python-delivery",
        "experienced",
        "Build distributable tools",
        "Separate modules, validate metadata, and expose a predictable CLI.",
    ),
    Chapter(
        "python-internals",
        "experienced",
        "Understand the machinery",
        "Use descriptors and class hooks, and inspect Python execution.",
    ),
    Chapter(
        "python-online",
        "experienced",
        "Packages, tests, and web APIs",
        "Install packages, test with pytest, and call web APIs safely.",
    ),
)

LESSONS = tuple(
    lesson
    for chapter in (
        experienced_semantics,
        experienced_composition,
        experienced_design,
        experienced_concurrency,
        experienced_delivery,
        experienced_internals,
        experienced_online,
    )
    for lesson in chapter.LESSONS
)
EXTRA_CHECKS = {
    key: checks
    for chapter in (
        experienced_semantics,
        experienced_composition,
        experienced_design,
        experienced_concurrency,
        experienced_delivery,
        experienced_internals,
        experienced_online,
    )
    for key, checks in chapter.EXTRA_CHECKS.items()
}

LESSONS = tuple(
    replace(lesson, checks=lesson.checks + EXTRA_CHECKS.get(lesson.id, ())) for lesson in LESSONS
)

# Stage contracts are the active authored exercise source; legacy fields above
# are projected for profile and import compatibility.
LESSONS = apply_stage_refresh(LESSONS)


# A path is an ordered course; prerequisites explain the prior unit without gating it.
LESSONS = tuple(
    replace(lesson, prerequisites=(LESSONS[index - 1].id,) if index else ())
    for index, lesson in enumerate(LESSONS)
)


LESSONS = apply_checkpoints(LESSONS)
