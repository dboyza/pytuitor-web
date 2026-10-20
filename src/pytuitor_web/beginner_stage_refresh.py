"""Beginner stage catalog, assembled from chapter-sized authoring files."""

from pytuitor_web.content import (
    beginner_b_automation,
    beginner_b_collections,
    beginner_b_data,
    beginner_b_functions,
    beginner_b_tools,
)

CHAPTER_CONTENT = (
    beginner_b_collections,
    beginner_b_functions,
    beginner_b_data,
    beginner_b_tools,
    beginner_b_automation,
)
BUILD_INSTRUCTIONS = {
    key: value for chapter in CHAPTER_CONTENT for key, value in chapter.BUILD_INSTRUCTIONS.items()
}
REPAIR_STAGES = {
    key: value for chapter in CHAPTER_CONTENT for key, value in chapter.REPAIR_STAGES.items()
}
