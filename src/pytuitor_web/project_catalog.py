"""Canonical growing-project catalog, separate from historical lesson identities."""

from dataclasses import replace

from pytuitor_web.content.lantern.authoring import PROJECT_ID
from pytuitor_web.content.lantern.core import CORE
from pytuitor_web.content.lantern.depth import DEPTH
from pytuitor_web.content.lantern.foundations import FOUNDATIONS
from pytuitor_web.content.lantern.online import ONLINE
from pytuitor_web.content.lantern.specialized import SPECIALIZED
from pytuitor_web.course_map import CHAPTER_UNITS
from pytuitor_web.models import ProjectDefinition

MILESTONES = tuple(
    replace(
        milestone,
        lesson=replace(milestone.lesson, prerequisites=CHAPTER_UNITS[milestone.lesson.chapter_id]),
    )
    for milestone in (*FOUNDATIONS, *CORE, *DEPTH, *SPECIALIZED, *ONLINE)
)
BY_MILESTONE = {milestone.lesson.id: milestone for milestone in MILESTONES}
BY_CHAPTER = {milestone.lesson.chapter_id: milestone for milestone in MILESTONES}
LANTERN_REACH = ProjectDefinition(
    PROJECT_ID,
    "Lantern Reach",
    "Explore a valley, help its residents, and restore an outpost in the game you build.",
    MILESTONES,
)
