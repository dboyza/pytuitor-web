"""Bounded, optional presentation state; never evidence of course completion."""

from __future__ import annotations

import hashlib
import json

from pytuitor_web.progress_types import check_event


def source_fingerprint(files: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def saved_report(checks, files, revision):
    cases = []
    for check in checks[:128]:
        case = dict(check)
        for key in (
            "input",
            "operation",
            "expected",
            "actual",
            "nudge",
            "output",
            "expected_output",
        ):
            if isinstance(case.get(key), str):
                limit = 2000 if key == "output" else 1200
                if len(case[key]) > limit:
                    case[key] = (
                        case[key][:limit]
                        + "\n[Saved preview shortened; check again for full evidence.]"
                    )
        cases.append(case)
    return {"revision": revision, "source": source_fingerprint(files), "cases": cases}


def load_report(entry, revision):
    report = entry.get("last_check")
    if not isinstance(report, dict) or report.get("revision") != revision:
        return []
    cases = report.get("cases")
    if not isinstance(cases, list) or not 0 < len(cases) <= 128:
        return []
    try:
        if len(json.dumps(report)) > 1024 * 1024:
            return []
        return [check_event(case) for case in cases if case.get("status") == "finished"]
    except (ValueError, TypeError, AttributeError):
        return []


def report_is_current(entry, revision):
    report = entry.get("last_check", {})
    return (
        isinstance(report, dict)
        and report.get("revision") == revision
        and report.get("source") == source_fingerprint(entry.get("files", {}))
    )


def resume_summary(store, lesson):
    if lesson.project_id:
        root = (
            store.data.get("projects", {})
            .get(lesson.project_id, {})
            .get("milestones", {})
            .get(lesson.id, {})
        )
    else:
        root = store.data["lessons"].get(lesson.id, {})
    if not root:
        return "Start with the explanation and exercise requirements."
    stage = root.get("stage", "build")
    entry = root if stage == "build" else root.get("repair", {})
    label = lesson.build_label if stage == "build" else "Repair"
    cases = load_report(entry, lesson.revision)
    if cases and report_is_current(entry, lesson.revision):
        remaining = sum(not case.get("passed", False) for case in cases)
        if remaining:
            return (
                f"{label} · {remaining} {'check remains' if remaining == 1 else 'checks remain'}."
            )
        return f"{label} checked · ready for {'Repair' if stage == 'build' else 'Next'}."
    if cases:
        return f"{label} · draft changed since the last check."
    return f"{label} · resume your saved work."


def progress_counts(store, lessons):
    """Separate optional work without treating familiar topics as earned completion."""
    from pytuitor_web.course_map import CHAPTERS, SECTIONS

    optional = {section.id for section in SECTIONS if section.optional}
    optional_chapters = {chapter.id for chapter in CHAPTERS if chapter.section_id in optional}
    groups = (
        [lesson for lesson in lessons if lesson.chapter_id not in optional_chapters],
        [lesson for lesson in lessons if lesson.chapter_id in optional_chapters],
    )
    return tuple(
        (
            sum(store.status(lesson) == "completed" for lesson in group),
            sum(store.status(lesson) == "familiar" for lesson in group),
            len(group),
        )
        for group in groups
    )


def safe_view(entry, files):
    """Discard damaged presentation metadata while keeping every source draft loadable."""
    original = entry.get("view", {})
    if not isinstance(original, dict):
        return {}
    result = {}
    if isinstance(original.get("active_file"), str) and original["active_file"] in files:
        result["active_file"] = original["active_file"]
    if original.get("pane") in ("lesson", "editor", "console"):
        result["pane"] = original["pane"]
    if original.get("focus") in (
        "reading-panel",
        "editor",
        "file-tree",
        "exercise-scroll",
        "results-scroll",
    ):
        result["focus"] = original["focus"]
    for key in ("reading", "exercise", "results"):
        value = original.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 100000:
            result[key] = value
    positions = original.get("positions", {})
    if isinstance(positions, dict):
        result["positions"] = {
            name: {
                key: list(value)
                for key, value in position.items()
                if key in ("cursor", "scroll")
                and isinstance(value, (list, tuple))
                and len(value) == 2
                and all(type(v) is int and 0 <= v <= 100000 for v in value)
            }
            for name, position in positions.items()
            if name in files and isinstance(position, dict)
        }
    if type(original.get("selected")) is int and 1 <= original["selected"] <= 128:
        result["selected"] = original["selected"]
    result["details"] = original.get("details") is True
    return result
