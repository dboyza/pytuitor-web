"""Local, optional review scheduling, separate from course completion."""

from datetime import date, timedelta

from pytuitor_web.content.reviews import REVIEWS
from pytuitor_web.curriculum import chapter_activities

INTERVALS = (2, 7, 21, 45)


def review_data(store, *, create=True):
    value = store.data.get("reviews")
    if not isinstance(value, dict):
        value = {}
        if create:
            store.data["reviews"] = value
    if not isinstance(value.get("chapters"), dict):
        if not create:
            return {**value, "chapters": {}}
        value["chapters"] = {}
    return value


def entry(store, chapter, *, create=True):
    if not create:
        chapters = review_data(store, create=False)["chapters"]
        item = chapters.get(chapter, {})
        return item if isinstance(item, dict) else {}
    chapters = review_data(store)["chapters"]
    if not isinstance(chapters.get(chapter), dict):
        chapters[chapter] = {}
    item = chapters[chapter]
    if not isinstance(item.get("tasks"), dict):
        item["tasks"] = {}
    return item


def ready(store, chapter):
    return all(
        store.status(unit) in ("completed", "familiar") for unit in chapter_activities(chapter)
    )


def due(store, chapter, today=None):
    today = today or date.today()
    item = entry(store, chapter, create=False)
    if not ready(store, chapter):
        return False
    try:
        target = date.fromisoformat(item.get("due", today.isoformat()))
    except (ValueError, TypeError):
        target = today
    return target <= today


def suggested(store, today=None):
    if review_data(store, create=False).get("paused") is True:
        return None
    return next((chapter for chapter in REVIEWS if due(store, chapter, today)), None)


def task_entry(store, chapter, task, *, create=True):
    if not create:
        tasks = entry(store, chapter, create=False).get("tasks", {})
        if not isinstance(tasks, dict):
            return {}
        item = tasks.get(task.id, {})
        return item if isinstance(item, dict) else {}
    tasks = entry(store, chapter)["tasks"]
    if not isinstance(tasks.get(task.id), dict):
        tasks[task.id] = {}
    return tasks[task.id]


def complete(store, chapter, today=None):
    item = entry(store, chapter)
    if item.get("finished") or not all(
        task_entry(store, chapter, task).get("passed") is True for task in REVIEWS[chapter]
    ):
        return False
    count = item.get("sessions", 0)
    count = count if isinstance(count, int) and 0 <= count <= 100000 else 0
    assisted = any(task_entry(store, chapter, task).get("assisted") for task in REVIEWS[chapter])
    interval = INTERVALS[0 if assisted else min(count, len(INTERVALS) - 1)]
    item.update(
        finished=True,
        sessions=count + 1,
        due=((today or date.today()) + timedelta(days=interval)).isoformat(),
    )
    return True


def restart(store, chapter):
    item = entry(store, chapter)
    for task in REVIEWS[chapter]:
        task_entry(store, chapter, task).pop("passed", None)
        task_entry(store, chapter, task).pop("assisted", None)
    item.update(finished=False, index=0)
