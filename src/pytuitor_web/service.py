"""Learning operations shared by every browser request; the profile has one writer at a time."""

from __future__ import annotations

import asyncio
import copy
import hashlib
import io
import os
import shlex
import shutil
import sys
import tempfile
import threading
import zipfile
from collections.abc import Callable
from datetime import date, datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import Any

from pytuitor_web import review_progress
from pytuitor_web.consoles import ConsoleError, Consoles
from pytuitor_web.content.reviews import REVIEWS
from pytuitor_web.course_map import CHAPTERS, SECTIONS
from pytuitor_web.curriculum import ACTIVITIES, BY_ID, LESSONS, Lesson, default_input
from pytuitor_web.guidance import error_guidance
from pytuitor_web.learning_progress import (
    load_report,
    progress_counts,
    report_is_current,
    resume_summary,
    saved_report,
)
from pytuitor_web.models import StageContract
from pytuitor_web.platform_files import is_link
from pytuitor_web.progress_types import CheckEvent, DraftState
from pytuitor_web.project_catalog import BY_MILESTONE, LANTERN_REACH, MILESTONES
from pytuitor_web.project_workspace import ProjectWorkspace
from pytuitor_web.runner import execute
from pytuitor_web.shell import command as shell_command
from pytuitor_web.shell import environment as shell_environment
from pytuitor_web.state import Store
from pytuitor_web.workspace import (
    MAX_FILE_BYTES,
    WorkspaceError,
    export_workspace,
    validate_files,
)

STAGES = ("build", "repair")
# Generated folders stay on disk but never become part of a draft or a check.
IGNORED = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
MAX_LISTED = 200


class LearningError(ValueError):
    """A learner-facing refusal that leaves every draft unchanged."""


def fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "surrogatepass")).hexdigest()[:16]


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S-%f")


class Tutor:
    def __init__(self, directory: Path | None = None):
        self.store = Store(directory)
        self.directory = self.store.directory
        self.lock = threading.RLock()
        self.consoles = Consoles()
        self.workspaces = self.directory / "workspaces"

    def close(self) -> None:
        self.consoles.shutdown()
        self.store.close()

    # Profile and navigation -------------------------------------------------------------------

    def persist(self) -> None:
        try:
            self.store.save()
        except OSError as error:
            raise LearningError(f"Could not save progress: {error}") from error

    def settings(self) -> dict[str, Any]:
        value = self.store.data.get("web")
        if not isinstance(value, dict):
            value = self.store.data["web"] = {}
        return value

    def catalog(self) -> dict[str, Any]:
        from pytuitor_web import __version__
        from pytuitor_web.curriculum import chapter_activities

        categories = []
        for section in SECTIONS:
            chapters = {c.id for c in CHAPTERS if c.section_id == section.id}
            concepts = dict.fromkeys(
                concept
                for lesson in LESSONS
                if lesson.chapter_id in chapters
                for concept in lesson.concepts
            )
            categories.append({"id": section.id, "title": section.title, "concepts": [*concepts]})
        return {
            "version": __version__,
            "counts": {
                "lessons": len(LESSONS),
                "milestones": len(MILESTONES),
                "chapters": len(CHAPTERS),
            },
            "sections": [
                {
                    "id": s.id,
                    "title": s.title,
                    "description": s.description,
                    "optional": s.optional,
                }
                for s in SECTIONS
            ],
            "chapters": [
                {
                    "id": c.id,
                    "number": index,
                    "title": c.title,
                    "outcome": c.outcome,
                    "section_id": c.section_id,
                    "prerequisites": list(c.prerequisites),
                    "activities": [lesson.id for lesson in chapter_activities(c.id)],
                }
                for index, c in enumerate(CHAPTERS, 1)
            ],
            "activities": {
                lesson.id: {
                    "id": lesson.id,
                    "title": lesson.title,
                    "subtitle": lesson.subtitle,
                    "minutes": lesson.minutes,
                    "concepts": list(lesson.concepts),
                    "chapter_id": lesson.chapter_id,
                    "milestone": bool(lesson.project_id),
                    "build_label": lesson.build_label,
                }
                for lesson in ACTIVITIES
            },
            "categories": categories,
        }

    def state(self) -> dict[str, Any]:
        with self.lock:
            store = self.store
            following = store.next_lesson()
            nxt = None
            if following:
                root = self._peek(following)
                note = root.get("resume_note", "")
                nxt = {
                    "id": following.id,
                    "summary": resume_summary(store, following),
                    "note": note if isinstance(note, str) else "",
                    "status": store.status(following),
                }
            core, optional = progress_counts(store, ACTIVITIES)
            return {
                "onboarded": store.data["onboarded"],
                "familiar": list(store.data["familiar"]),
                "last_lesson": store.data.get("last_lesson"),
                "statuses": {lesson.id: store.status(lesson) for lesson in ACTIVITIES},
                "next": nxt,
                "progress": {
                    "core": dict(zip(("completed", "familiar", "total"), core, strict=True)),
                    "optional": dict(
                        zip(("completed", "familiar", "total"), optional, strict=True)
                    ),
                },
                "review_suggested": review_progress.suggested(store),
                "settings": {"theme": self.settings().get("theme", "dark")},
                "data_dir": str(self.directory),
            }

    def onboard(self) -> None:
        with self.lock:
            self.store.data["onboarded"] = True
            self.persist()

    def set_familiar(self, concepts: list[str]) -> None:
        with self.lock:
            previous = list(self.store.data["familiar"])
            self.store.set_familiar(concepts)
            try:
                self.persist()
            except LearningError:
                self.store.data["familiar"] = previous
                raise

    def set_theme(self, theme: str) -> None:
        if theme not in ("dark", "light", "system"):
            raise LearningError("Choose dark, light, or system.")
        with self.lock:
            self.settings()["theme"] = theme
            self.persist()

    def restart(self) -> str | None:
        """Stop every shell, keep a copy of the on-disk workspaces, then clear progress."""
        with self.lock:
            self.consoles.end_matching("")
            self.store.reset()
            if self.workspaces.exists():
                backup = self.directory / "exports" / f"workspaces-before-restart-{_stamp()}"
                backup.parent.mkdir(parents=True, exist_ok=True)
                self.workspaces.rename(backup)
                return str(backup)
            return None

    # Activities -------------------------------------------------------------------------------

    def lesson(self, lesson_id: str) -> Lesson:
        lesson = BY_ID.get(lesson_id)
        if lesson is None or lesson not in ACTIVITIES:
            raise LearningError("That lesson is not in this course.")
        return lesson

    def _peek(self, lesson: Lesson) -> dict:
        """Read progress without creating a draft."""
        if lesson.project_id:
            return (
                self.store.data.get("projects", {})
                .get(lesson.project_id, {})
                .get("milestones", {})
                .get(lesson.id, {})
            )
        return self.store.data["lessons"].get(lesson.id, {})

    def open(self, lesson_id: str) -> dict[str, Any]:
        """Opening a lesson is the only action that changes the resume anchor."""
        with self.lock:
            lesson = self.lesson(lesson_id)
            previous = self.store.data.get("last_lesson")
            self.store.entry(lesson)
            self.store.data["last_lesson"] = lesson.id
            if lesson.project_id:
                self.store.data["projects"][lesson.project_id]["last_milestone"] = lesson.id
            try:
                self.persist()
            except LearningError:
                self.store.data["last_lesson"] = previous
                raise
            return self.activity(lesson_id)

    def activity(self, lesson_id: str) -> dict[str, Any]:
        with self.lock:
            lesson = self.lesson(lesson_id)
            root = self.store.entry(lesson)
            stage = root.get("stage", "build")
            if stage == "repair" and not self.passed(lesson, "build"):
                stage = "build"
            chapter = next(c for c in CHAPTERS if c.id == lesson.chapter_id)
            missing = [
                {"id": key, "title": BY_ID[key].title}
                for key in lesson.prerequisites
                if key in BY_ID and self.store.status(BY_ID[key]) not in ("completed", "familiar")
            ]
            brief = outcome = origin = connection = None
            if lesson.project_id:
                from pytuitor_web.content.lantern.briefs import BRIEFS

                item = BRIEFS[lesson.id.removeprefix("reach-")]
                brief, outcome = item.markdown(), item.outcome
                origin = {
                    "blank": "Your first version starts blank.",
                    "supplied": "Starting from supplied earlier code. "
                    "Skipped milestones stay incomplete.",
                    "learner": "Continuing your own working checkpoint. "
                    "Earlier source is preserved.",
                    "restored": "A historical checkpoint was restored into this draft. "
                    "Check it again.",
                }[root.get("base_origin", "blank")]
            else:
                from pytuitor_web.content.lantern.connections import GAME_CONNECTIONS

                link = GAME_CONNECTIONS.get(lesson.id)
                if link:
                    connection = link[0].lower() + link[1:]
            prediction = None
            if lesson.choices:
                answered = root.get("prediction") is True
                prediction = {
                    "prompt": lesson.prediction,
                    "choices": list(lesson.choices),
                    "answered": answered,
                    "explanation": lesson.explanation if answered else None,
                }
            note = root.get("resume_note", "")
            return {
                "id": lesson.id,
                "title": lesson.title,
                "subtitle": lesson.subtitle,
                "minutes": lesson.minutes,
                "milestone": bool(lesson.project_id),
                "build_label": lesson.build_label,
                "chapter": {"id": chapter.id, "title": chapter.title},
                "body": _body(lesson),
                "brief": brief,
                "outcome": outcome,
                "origin": origin,
                "connection": connection,
                "missing": missing,
                "prediction": prediction,
                "updated": "code" in root and root.get("revision", 1) != lesson.revision,
                "stage": stage,
                "stages": self.stage_flags(lesson),
                "completed": self.store.status(lesson) == "completed",
                "note": note if isinstance(note, str) else "",
                "checkpoint": root.get("checkpoint"),
            }

    def stage_flags(self, lesson: Lesson) -> dict[str, Any]:
        return {
            "build": {"passed": self.passed(lesson, "build")},
            "repair": {
                "passed": self.passed(lesson, "repair"),
                "unlocked": self.passed(lesson, "build"),
            },
            "completed": self.store.status(lesson) == "completed",
        }

    def passed(self, lesson: Lesson, stage: str) -> bool:
        root = self.store.entry(lesson)
        entry = root if stage == "build" else root.get("repair", {})
        result = entry.get("checked_revision") == lesson.revision and "checked_code" in entry
        if lesson.project_id:
            result = result and entry.get("checked_files") == entry.get("files")
        return result

    def entry(self, lesson: Lesson, stage: str) -> DraftState:
        if stage not in STAGES:
            raise LearningError("Choose the Build or Repair stage.")
        root = self.store.entry(lesson)
        return root if stage == "build" else root.setdefault("repair", {})

    def contract(self, lesson: Lesson, stage: str) -> StageContract:
        if lesson.project_id:
            return ProjectWorkspace(self.store, lesson.project_id).contract(
                BY_MILESTONE[lesson.id], stage
            )
        return lesson.stage_contract(stage)

    def draft_files(self, lesson: Lesson, stage: str) -> dict[str, str]:
        entry = self.entry(lesson, stage)
        contract = self.contract(lesson, stage)
        if "files" not in entry:
            defaults = dict(contract.starter_files or {name: "" for name in contract.files})
            defaults[lesson.entrypoint] = entry.get("code", defaults.get(lesson.entrypoint, ""))
            entry["files"] = defaults
        # A curriculum update may add or rename required files. Keep every old draft.
        entry["files"].setdefault(lesson.entrypoint, entry.get("code", ""))
        for name in contract.files:
            entry["files"].setdefault(name, (contract.starter_files or {}).get(name, ""))
        if "code" not in entry:
            entry["revision"] = lesson.revision
        entry["code"] = entry["files"][lesson.entrypoint]
        return entry["files"]

    def required(self, lesson: Lesson, stage: str) -> set[str]:
        return {lesson.entrypoint, *self.contract(lesson, stage).files}

    # On-disk workspaces -----------------------------------------------------------------------

    def workspace(self, lesson: Lesson, stage: str) -> Path:
        path = self.workspaces / lesson.id / stage
        if any(is_link(parent) for parent in (path, *path.parents)):
            raise LearningError("The workspace folder is a symbolic link. Choose another profile.")
        return path

    def write_workspace(self, lesson: Lesson, stage: str) -> None:
        """Make the folder match the draft after the tutor replaced it, such as a reset."""
        path = self.workspace(lesson, stage)
        files = self.draft_files(lesson, stage)
        if path.exists():
            for name in list(self._disk_files(path)):
                if name not in files:
                    (path / name).unlink(missing_ok=True)
        for name, text in files.items():
            self._write_file(path, name, text)

    def _write_file(self, root: Path, name: str, text: str) -> None:
        target = root / PurePosixPath(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        if is_link(target):
            target.unlink()
        temporary = target.with_name(f".{target.name}.pytuitor-{os.getpid()}")
        temporary.write_text(text, encoding="utf-8", newline="")
        os.replace(temporary, target)

    def _disk_files(self, root: Path) -> dict[str, int]:
        """Regular files in the workspace, relative POSIX names to sizes; links are skipped."""
        found: dict[str, int] = {}
        if not root.is_dir():
            return found
        for directory, folders, names in os.walk(root, followlinks=False):
            folders[:] = sorted(
                f for f in folders if f not in IGNORED and not is_link(Path(directory, f))
            )
            for name in sorted(names):
                path = Path(directory, name)
                if is_link(path) or name.startswith(".") and ".pytuitor-" in name:
                    continue
                try:
                    info = path.stat()
                except OSError:
                    continue
                found[path.relative_to(root).as_posix()] = info.st_size
                if len(found) >= MAX_LISTED:
                    return found
        return found

    def sync(self, lesson: Lesson, stage: str) -> dict[str, Any]:
        """Adopt edits made in the terminal; restore missing required files; list the rest."""
        path = self.workspace(lesson, stage)
        files = self.draft_files(lesson, stage)
        required = self.required(lesson, stage)
        changed: list[str] = []
        if not path.exists():
            path.mkdir(parents=True)
            for name, text in files.items():
                self._write_file(path, name, text)
        disk = self._disk_files(path)
        for name in list(files):
            if name not in disk:
                if name in required:
                    self._write_file(path, name, files[name])
                else:
                    files.pop(name)
                    changed.append(name)
                continue
            if disk[name] > MAX_FILE_BYTES:
                continue
            try:
                text = (path / name).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if text != files[name]:
                files[name] = text
                changed.append(name)
        if changed:
            self._draft_changed(lesson, stage)
            self.persist()
        untracked = [
            {"name": name, "size": size} for name, size in disk.items() if name not in files
        ]
        return {"changed": changed, "untracked": untracked}

    def _draft_changed(self, lesson: Lesson, stage: str) -> None:
        entry = self.entry(lesson, stage)
        entry["code"] = entry["files"][lesson.entrypoint]
        if lesson.project_id and entry.get("checked_files") != entry.get("files"):
            root = self.store.entry(lesson)
            root.pop("completed", None)
            root.pop("completed_revision", None)

    def stage(self, lesson_id: str, stage: str) -> dict[str, Any]:
        with self.lock:
            lesson = self.lesson(lesson_id)
            entry = self.entry(lesson, stage)
            contract = self.contract(lesson, stage)
            listing = self.sync(lesson, stage)
            files = self.draft_files(lesson, stage)
            required = self.required(lesson, stage)
            hints = contract.hints
            count = min(entry.get("hints", 0), len(hints))
            instructions = contract.instructions or (
                "Write the whole program in the blank editor using the requirements below. "
                "Run it in the terminal, then Check. Passing unlocks Repair."
                if stage == "build"
                else "This separate program contains a mistake. Run and Check to investigate, "
                f"then fix it. Your {lesson.build_label} draft is saved separately."
            )
            guidance = None
            if stage == "repair":
                from pytuitor_web.repair_pacing import repair_guidance

                guidance = repair_guidance(lesson)
            cases = load_report(entry, lesson.revision)
            view = entry.get("view", {}) if isinstance(entry.get("view"), dict) else {}
            active = view.get("active_file")
            return {
                "stage": stage,
                "label": lesson.build_label if stage == "build" else "Repair",
                "instructions": instructions,
                "guidance": guidance,
                "hints": {"revealed": list(hints[:count]), "total": len(hints)},
                "reference_seen": bool(entry.get("solution_seen")),
                "entrypoint": lesson.entrypoint,
                "run": self.run_command(lesson),
                "files": [
                    {
                        "name": name,
                        "content": text,
                        "hash": fingerprint(text),
                        "required": name in required,
                    }
                    for name, text in sorted(
                        files.items(), key=lambda item: (item[0] != lesson.entrypoint, item[0])
                    )
                ],
                "untracked": listing["untracked"],
                "workspace": str(self.workspace(lesson, stage)),
                "report": (
                    {"cases": cases, "current": report_is_current(entry, lesson.revision)}
                    if cases
                    else None
                ),
                "passed": self.passed(lesson, stage),
                "check_count": len(contract.checks),
                "view": {"active_file": active if active in files else lesson.entrypoint},
                "flags": self.stage_flags(lesson),
            }

    def switch(self, lesson_id: str, stage: str) -> dict[str, Any]:
        with self.lock:
            lesson = self.lesson(lesson_id)
            if stage == "repair" and not self.passed(lesson, "build"):
                raise LearningError(f"Pass the {lesson.build_label} checks to unlock Repair.")
            self.entry(lesson, stage)
            self.store.entry(lesson)["stage"] = stage
            self.persist()
            return self.stage(lesson_id, stage)

    def poll(self, lesson_id: str, stage: str) -> dict[str, Any]:
        with self.lock:
            lesson = self.lesson(lesson_id)
            listing = self.sync(lesson, stage)
            files = self.draft_files(lesson, stage)
            return {
                "files": {name: fingerprint(text) for name, text in files.items()},
                "changed": {name: files[name] for name in listing["changed"] if name in files},
                "untracked": listing["untracked"],
                "flags": self.stage_flags(lesson),
            }

    def read_file(self, lesson_id: str, stage: str, name: str) -> dict[str, str]:
        with self.lock:
            files = self.draft_files(self.lesson(lesson_id), stage)
            if name not in files:
                raise LearningError(f"{name} is not part of this workspace.")
            return {"content": files[name], "hash": fingerprint(files[name])}

    def save_file(self, lesson_id: str, stage: str, name: str, content: str) -> dict[str, Any]:
        with self.lock:
            lesson = self.lesson(lesson_id)
            files = self.draft_files(lesson, stage)
            if name not in files:
                raise LearningError(f"{name} is not part of this workspace.")
            validate_files({**files, name: content})
            files[name] = content
            self._write_file(self.workspace(lesson, stage), name, content)
            self._draft_changed(lesson, stage)
            self.persist()
            return {"hash": fingerprint(content), "flags": self.stage_flags(lesson)}

    def add_file(self, lesson_id: str, stage: str, name: str, track: bool = False) -> dict:
        with self.lock:
            lesson = self.lesson(lesson_id)
            files = self.draft_files(lesson, stage)
            name = name.strip()
            if name in files:
                return self.stage(lesson_id, stage)
            text = ""
            path = self.workspace(lesson, stage) / PurePosixPath(name)
            if track:
                try:
                    if is_link(path) or path.stat().st_size > MAX_FILE_BYTES:
                        raise LearningError(f"{name} is too large or not a regular file.")
                    text = path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError) as error:
                    raise LearningError(f"{name} is not a readable UTF-8 text file.") from error
            validate_files({**files, name: text})
            files[name] = text
            self._write_file(self.workspace(lesson, stage), name, text)
            self._draft_changed(lesson, stage)
            entry = self.entry(lesson, stage)
            entry.setdefault("view", {})["active_file"] = name
            self.persist()
            return self.stage(lesson_id, stage)

    def remove_file(self, lesson_id: str, stage: str, name: str) -> dict[str, Any]:
        with self.lock:
            lesson = self.lesson(lesson_id)
            files = self.draft_files(lesson, stage)
            if name in self.required(lesson, stage):
                raise LearningError(
                    "This file is required by the exercise. You can clear its contents instead."
                )
            backup = self.export_backup(lesson, stage)
            files.pop(name, None)
            (self.workspace(lesson, stage) / PurePosixPath(name)).unlink(missing_ok=True)
            self._draft_changed(lesson, stage)
            self.persist()
            return {**self.stage(lesson_id, stage), "backup": str(backup)}

    def read_untracked(self, lesson_id: str, stage: str, name: str) -> str:
        with self.lock:
            lesson = self.lesson(lesson_id)
            validate_files({name: ""})
            path = self.workspace(lesson, stage) / PurePosixPath(name)
            if is_link(path) or not path.is_file():
                raise LearningError("That file is no longer in the workspace.")
            with path.open("rb") as stream:
                raw = stream.read(64 * 1024 + 1)
            text = raw[: 64 * 1024].decode("utf-8", "replace")
            if b"\0" in raw:
                return "[This file is not text, so it cannot be previewed.]"
            return text + ("\n[Preview shortened.]" if len(raw) > 64 * 1024 else "")

    def save_view(self, lesson_id: str, stage: str, active_file: str) -> None:
        with self.lock:
            lesson = self.lesson(lesson_id)
            entry = self.entry(lesson, stage)
            if active_file in self.draft_files(lesson, stage):
                entry.setdefault("view", {})["active_file"] = active_file
                self.persist()

    def run_command(self, lesson: Lesson) -> str:
        # The tutor's interpreter comes first on the embedded shell's PATH.
        return f"python {shlex.quote(lesson.entrypoint)}"

    # Learning aids ----------------------------------------------------------------------------

    def hint(self, lesson_id: str, stage: str) -> dict[str, Any]:
        with self.lock:
            lesson = self.lesson(lesson_id)
            entry = self.entry(lesson, stage)
            hints = self.contract(lesson, stage).hints
            entry["hints"] = min(entry.get("hints", 0) + 1, len(hints))
            self.persist()
            return {"revealed": list(hints[: entry["hints"]]), "total": len(hints)}

    def reference(self, lesson_id: str, stage: str) -> dict[str, Any]:
        with self.lock:
            lesson = self.lesson(lesson_id)
            entry = self.entry(lesson, stage)
            entry["solution_seen"] = True
            self.persist()
            contract = self.contract(lesson, stage)
            return {
                "files": contract.reference_files or {lesson.entrypoint: lesson.solution},
                "entrypoint": lesson.entrypoint,
            }

    def predict(self, lesson_id: str, choice: int) -> dict[str, Any]:
        with self.lock:
            lesson = self.lesson(lesson_id)
            if not 0 <= choice < len(lesson.choices):
                raise LearningError("Choose one of the listed answers.")
            correct = choice == lesson.answer
            self.store.entry(lesson)["prediction"] = correct
            self.mark_complete(lesson)
            self.persist()
            return {
                "correct": correct,
                "explanation": lesson.explanation if correct else None,
                "flags": self.stage_flags(lesson),
            }

    def mark_complete(self, lesson: Lesson) -> bool:
        complete = self.passed(lesson, "build") and self.passed(lesson, "repair")
        if complete:
            entry = self.store.entry(lesson)
            entry["completed"] = True
            entry["completed_revision"] = lesson.revision
        return complete

    def note(self, lesson_id: str, text: str) -> None:
        with self.lock:
            lesson = self.lesson(lesson_id)
            self.store.entry(lesson)["resume_note"] = text.strip()[:500]
            self.persist()

    def following(self, lesson_id: str) -> str | None:
        with self.lock:
            lesson = self.lesson(lesson_id)
            if not self.passed(lesson, "repair"):
                raise LearningError("Pass the Repair checks to complete the lesson.")
            self.store.data["last_lesson"] = lesson.id
            nxt = self.store.next_lesson()
            return nxt.id if nxt is not None and nxt.id != lesson.id else None

    # Checks -----------------------------------------------------------------------------------

    async def check(
        self, lesson_id: str, stage: str, emit: Callable[[CheckEvent], None]
    ) -> dict[str, Any]:
        with self.lock:
            lesson = self.lesson(lesson_id)
            self.sync(lesson, stage)
            source = dict(self.draft_files(lesson, stage))
            contract = self.contract(lesson, stage)
        result = await execute(
            lesson,
            source[lesson.entrypoint],
            default_input(lesson, stage),
            check=True,
            files=source,
            stage=contract,
            on_check=emit,
        )
        with self.lock:
            entry = self.entry(lesson, stage)
            entry["last_check"] = saved_report(result.checks, source, lesson.revision)
            summary, stale = "", False
            if result.passed:
                if source != self.draft_files(lesson, stage):
                    stale = True
                    summary = "Checks passed for an earlier draft. Check your latest edits again."
                else:
                    if lesson.project_id and stage == "build":
                        try:
                            ProjectWorkspace(self.store, lesson.project_id).checkpoint(
                                BY_MILESTONE[lesson.id], source, result.checks
                            )
                        except (OSError, WorkspaceError) as error:
                            raise LearningError(
                                f"Checks passed, but the checkpoint could not be saved: {error}"
                            ) from error
                    entry["checked_code"] = source[lesson.entrypoint]
                    entry["checked_files"] = source
                    entry["checked_revision"] = lesson.revision
                    if self.mark_complete(lesson):
                        summary = "Both stages passed. Continue when you're ready."
                    else:
                        summary = "Repair is unlocked: investigate and fix a separate program."
            else:
                failed = next((case for case in result.checks if not case.get("passed")), None)
                summary = failed["nudge"] if failed else "Read the error, edit, and Check again."
            self.persist()
            return {
                "passed": result.passed and not stale,
                "error": result.error,
                "guidance": error_guidance(result.error) if result.error else "",
                "summary": summary,
                "cases": result.checks,
                "flags": self.stage_flags(lesson),
            }

    # Reset and export -------------------------------------------------------------------------

    def export_backup(self, lesson: Lesson, stage: str) -> Path:
        files = dict(self.draft_files(lesson, stage))
        directory = self.directory / "exports" / f"{lesson.id}-{stage}-{_stamp()}"
        return export_workspace(directory, files)

    def reset(self, lesson_id: str, stage: str) -> dict[str, Any]:
        """Back up the complete current stage before restoring blank Build or broken Repair."""
        with self.lock:
            lesson = self.lesson(lesson_id)
            self.sync(lesson, stage)
            if lesson.project_id:
                backup = ProjectWorkspace(self.store, lesson.project_id).backup(
                    BY_MILESTONE[lesson.id]
                )
            else:
                backup = self.export_backup(lesson, stage)
            self.consoles.end_matching(self.console_key(lesson, stage))
            root = self.store.entry(lesson)
            root.pop("completed", None)
            root.pop("completed_revision", None)
            if stage == "build":
                for key in (
                    "code",
                    "files",
                    "checked_files",
                    "checked_code",
                    "checked_revision",
                    "hints",
                    "prediction",
                    "view",
                    "last_check",
                ):
                    root.pop(key, None)
                root["revision"] = lesson.revision
                if lesson.project_id:
                    root["files"] = dict(root["base_files"])
                    root["code"] = root["files"][lesson.entrypoint]
            else:
                root["repair"] = {"revision": lesson.revision}
            self.write_workspace(lesson, stage)
            self.persist()
            return {**self.stage(lesson_id, stage), "backup": str(backup)}

    def export_zip(self, lesson_id: str, stage: str) -> tuple[str, bytes]:
        with self.lock:
            lesson = self.lesson(lesson_id)
            self.sync(lesson, stage)
            files = dict(self.draft_files(lesson, stage))
        return f"{lesson.id}-{stage}.zip", _zip(files, f"{lesson.id}-{stage}")

    # Terminals --------------------------------------------------------------------------------

    def console_key(self, lesson: Lesson, stage: str) -> str:
        return f"{lesson.id}/{stage}"

    def open_console(
        self, lesson_id: str, stage: str, cols: int, rows: int, fresh: bool = False
    ) -> dict[str, Any]:
        with self.lock:
            lesson = self.lesson(lesson_id)
            self.sync(lesson, stage)
            key = self.console_key(lesson, stage)
            if not fresh:
                live = [item for item in self.consoles.find(key) if item["alive"]]
                if live:
                    return live[0]
            path = self.workspace(lesson, stage)
            label = lesson.build_label if stage == "build" else "Repair"
        argv, extra = shell_command(self.directory / "shell")
        env = shell_environment(
            {
                **extra,
                "PYTUITOR_TITLE": lesson.title,
                "PYTUITOR_STAGE": label,
                "PYTUITOR_LABEL": lesson.id,
                "PYTUITOR_RUN": self.run_command(lesson),
            }
        )
        return self.consoles.open(key, label, argv, str(path), env, (cols, rows))

    def run(self, console_id: str, lesson_id: str) -> None:
        lesson = self.lesson(lesson_id)
        self.consoles.type_command(console_id, self.run_command(lesson))

    def play_checkpoint(self, identifier: str, cols: int, rows: int) -> dict[str, Any]:
        """Play a working version in a temporary folder; history and drafts stay unchanged."""
        with self.lock:
            payload = ProjectWorkspace(self.store).read_checkpoint(identifier)
        lesson = BY_ID.get(payload["milestone"])
        if lesson is None:
            raise LearningError("This milestone is no longer available. Export it to play it.")
        folder = Path(tempfile.mkdtemp(prefix="pytuitor-play-"))
        for name, text in payload["files"].items():
            self._write_file(folder, name, text)
        env = shell_environment({"PYTUITOR_TITLE": lesson.title})
        argv = [sys.executable, "-X", "utf8", lesson.entrypoint]
        try:
            return self.consoles.open(
                f"play/{identifier}",
                f"Play · {lesson.title}",
                argv,
                str(folder),
                env,
                (cols, rows),
                on_exit=lambda: shutil.rmtree(folder, ignore_errors=True),
            )
        except (OSError, ConsoleError):
            shutil.rmtree(folder, ignore_errors=True)
            raise

    # Lantern Reach ----------------------------------------------------------------------------

    def game(self) -> dict[str, Any]:
        from pytuitor_web.content.lantern.briefs import BRIEFS

        with self.lock:
            workspace = ProjectWorkspace(self.store)
            sections = {chapter.id: chapter.section_id for chapter in CHAPTERS}
            core, optional = progress_counts(self.store, [item.lesson for item in MILESTONES])
            snapshots = workspace.data["checkpoints"]
            milestones = []
            for index, item in enumerate(MILESTONES, 1):
                lesson = item.lesson
                entry = workspace.data["milestones"].get(lesson.id)
                compatible = workspace.compatible(item)
                origin = (
                    "Resume your saved Extend and Repair drafts."
                    if entry
                    else "Starts from your compatible working checkpoint."
                    if compatible
                    else "Starts from labeled supplied earlier code; skipped work stays incomplete."
                    if item.requires
                    else "Start with a blank file and build your first scene."
                )
                milestones.append(
                    {
                        "id": lesson.id,
                        "number": index,
                        "title": lesson.title,
                        "minutes": lesson.minutes,
                        "chapter_id": lesson.chapter_id,
                        "status": self.store.status(lesson),
                        "optional": sections[lesson.chapter_id]
                        in ("python-depth", "specialized-topics", "online-python"),
                        "outcome": BRIEFS[lesson.id.removeprefix("reach-")].outcome,
                        "origin": origin,
                        "supplied_base": bool(item.requires),
                        "started": entry is not None,
                    }
                )
            return {
                "title": LANTERN_REACH.title,
                "description": LANTERN_REACH.description,
                "progress": {
                    "core": dict(zip(("completed", "familiar", "total"), core, strict=True)),
                    "optional": dict(
                        zip(("completed", "familiar", "total"), optional, strict=True)
                    ),
                },
                "last_milestone": workspace.data.get("last_milestone"),
                "milestones": milestones,
                "checkpoints": [
                    {
                        **item,
                        "title": BY_ID[item["milestone"]].title
                        if item["milestone"] in BY_ID
                        else item["milestone"],
                    }
                    for item in reversed(snapshots)
                ],
            }

    def supplied_base(self, milestone_id: str, checkpoint: str | None = None) -> dict:
        with self.lock:
            milestone = BY_MILESTONE.get(milestone_id)
            if milestone is None:
                raise LearningError("That milestone is not part of Lantern Reach.")
            workspace = ProjectWorkspace(self.store)
            for stage in STAGES:
                self.consoles.end_matching(self.console_key(milestone.lesson, stage))
            backup = None
            if milestone.lesson.id in workspace.data["milestones"]:
                for stage in STAGES:
                    if self.workspace(milestone.lesson, stage).exists():
                        self.sync(milestone.lesson, stage)
                backup = workspace.replace_base(milestone, checkpoint)
            else:
                entry = workspace.start(milestone, supplied=checkpoint is None, parent=checkpoint)
                if checkpoint:
                    entry["base_origin"] = "restored"
                self.persist()
            for stage in STAGES:
                if self.workspace(milestone.lesson, stage).exists():
                    self.write_workspace(milestone.lesson, stage)
            return {"backup": str(backup) if backup else None}

    def export_checkpoint(self, identifier: str) -> tuple[str, bytes]:
        with self.lock:
            path = ProjectWorkspace(self.store).export_checkpoint(identifier)
        files = {
            p.relative_to(path).as_posix(): p.read_text(encoding="utf-8")
            for p in sorted(path.rglob("*"))
            if p.is_file()
        }
        return "lantern-reach.zip", _zip(files, "lantern-reach")

    # Optional review --------------------------------------------------------------------------

    def reviews(self) -> dict[str, Any]:
        with self.lock:
            store = self.store
            data = review_progress.review_data(store, create=False)
            suggested = review_progress.suggested(store)
            chapters = []
            for chapter in CHAPTERS:
                item = review_progress.entry(store, chapter.id, create=False)
                count = sum(
                    review_progress.task_entry(store, chapter.id, task, create=False).get("passed")
                    is True
                    for task in REVIEWS[chapter.id]
                )
                chapters.append(
                    {
                        "id": chapter.id,
                        "title": chapter.title,
                        "section_id": chapter.section_id,
                        "label": "Suggested"
                        if review_progress.due(store, chapter.id)
                        else "Available"
                        if review_progress.ready(store, chapter.id)
                        else "Preview",
                        "passed": count,
                        "total": len(REVIEWS[chapter.id]),
                        "finished": item.get("finished") is True,
                        "started": bool(item.get("tasks")),
                        "due": item.get("due"),
                    }
                )
            return {
                "paused": data.get("paused") is True,
                "suggested": suggested,
                "chapters": chapters,
            }

    def pause_reviews(self) -> None:
        with self.lock:
            data = review_progress.review_data(self.store)
            data["paused"] = not data.get("paused", False)
            self.persist()

    def defer_review(self, chapter: str) -> None:
        with self.lock:
            self._review_chapter(chapter)
            item = review_progress.entry(self.store, chapter)
            item["due"] = (date.today() + timedelta(days=1)).isoformat()
            self.persist()

    def _review_chapter(self, chapter: str) -> None:
        if chapter not in REVIEWS:
            raise LearningError("That review session does not exist.")

    def open_review(self, chapter: str) -> dict[str, Any]:
        with self.lock:
            self._review_chapter(chapter)
            if review_progress.entry(self.store, chapter).get("finished"):
                review_progress.restart(self.store, chapter)
                self.persist()
            index = review_progress.entry(self.store, chapter).get("index", 0)
            index = index if type(index) is int and 0 <= index < len(REVIEWS[chapter]) else 0
            title = next(c.title for c in CHAPTERS if c.id == chapter)
            return {
                "chapter": chapter,
                "title": title,
                "index": index,
                "tasks": [
                    {
                        "title": task.title,
                        "kind": task.kind,
                        "passed": review_progress.task_entry(
                            self.store, chapter, task, create=False
                        ).get("passed")
                        is True,
                    }
                    for task in REVIEWS[chapter]
                ],
            }

    def _task(self, chapter: str, index: int):
        self._review_chapter(chapter)
        tasks = REVIEWS[chapter]
        if not 0 <= index < len(tasks):
            raise LearningError("That review task does not exist.")
        return tasks[index]

    def review_task(self, chapter: str, index: int) -> dict[str, Any]:
        with self.lock:
            task = self._task(chapter, index)
            attempt = review_progress.task_entry(self.store, chapter, task, create=False)
            text = attempt.get("code", task.starter)
            choice = attempt.get("choice")
            return {
                "index": index,
                "title": task.title,
                "kind": task.kind,
                "prompt": task.prompt,
                "choices": list(task.choices),
                "code": text if isinstance(text, str) and len(text) <= 100000 else task.starter,
                "choice": choice if type(choice) is int else None,
                "passed": attempt.get("passed") is True,
                "last": index == len(REVIEWS[chapter]) - 1,
            }

    def save_review(self, chapter: str, index: int, code: str | None, choice: int | None):
        with self.lock:
            task = self._task(chapter, index)
            attempt = review_progress.task_entry(self.store, chapter, task)
            if code is not None:
                attempt["code"] = code[:100000]
            if choice is not None:
                attempt["choice"] = choice
            attempt.pop("passed", None)
            self.persist()

    async def check_review(self, chapter: str, index: int) -> dict[str, Any]:
        with self.lock:
            task = self._task(chapter, index)
            attempt = review_progress.task_entry(self.store, chapter, task)
            source = attempt.get("code", task.starter)
            choice = attempt.get("choice")
        cases: list[CheckEvent] = []
        error = ""
        if task.kind == "predict":
            passed = choice == task.answer
            feedback = ("Correct. " if passed else "Not quite. ") + task.explanation
        else:
            result = await execute(task.lesson(), source)
            passed, cases, error = result.passed, result.checks, result.error
            feedback = (
                "Every check passed."
                if passed
                else next((c["nudge"] for c in cases if not c.get("passed")), error)
            )
        with self.lock:
            attempt = review_progress.task_entry(self.store, chapter, task)
            if attempt.get("code", task.starter) != source or attempt.get("choice") != choice:
                return {
                    "passed": False,
                    "feedback": "Your answer changed during the check. Check again.",
                    "cases": cases,
                    "error": error,
                }
            old = copy.deepcopy(attempt)
            attempt["passed"] = bool(passed)
            if not passed:
                attempt["assisted"] = True
            try:
                self.persist()
            except LearningError:
                attempt.clear()
                attempt.update(old)
                raise
            return {
                "passed": bool(passed),
                "feedback": feedback,
                "cases": cases,
                "error": error,
                "guidance": error_guidance(error) if error else "",
            }

    def review_aid(self, chapter: str, index: int, kind: str) -> str:
        with self.lock:
            task = self._task(chapter, index)
            review_progress.task_entry(self.store, chapter, task)["assisted"] = True
            self.persist()
            if kind == "reference":
                return task.reference
            return task.hint or "Trace each statement in order and note the changing values."

    def review_next(self, chapter: str, index: int) -> dict[str, Any]:
        with self.lock:
            task = self._task(chapter, index)
            if not review_progress.task_entry(self.store, chapter, task).get("passed"):
                raise LearningError("Pass this task before continuing.")
            item = review_progress.entry(self.store, chapter)
            if index == len(REVIEWS[chapter]) - 1:
                review_progress.complete(self.store, chapter)
                self.persist()
                return {"finished": True, "due": item.get("due")}
            item["index"] = index + 1
            self.persist()
            return {"finished": False, "index": index + 1}


def _body(lesson: Lesson) -> str:
    """Drop a leading title and subtitle that the page header already shows."""
    head, _, rest = lesson.body.lstrip().partition("\n")
    if head.removeprefix("# ").removeprefix("Lantern Reach: ") != lesson.title:
        return lesson.body
    rest = rest.lstrip("\n")
    return rest[len(lesson.subtitle) :].lstrip("\n") if rest.startswith(lesson.subtitle) else rest


def _zip(files: dict[str, str], folder: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, text in sorted(validate_files(files).items()):
            archive.writestr(f"{folder}/{name}", text)
    return buffer.getvalue()


async def stream_check(
    tutor: Tutor, lesson_id: str, stage: str
) -> tuple[asyncio.Queue[dict | None], asyncio.Task]:
    """Start a check whose running and finished cases arrive on a queue, ending with None."""
    queue: asyncio.Queue[dict | None] = asyncio.Queue()

    async def work() -> None:
        try:
            outcome = await tutor.check(
                lesson_id, stage, lambda case: queue.put_nowait({"type": "case", "case": case})
            )
            queue.put_nowait({"type": "done", **outcome})
        except (LearningError, WorkspaceError, OSError) as error:
            queue.put_nowait({"type": "failed", "detail": str(error)})
        finally:
            queue.put_nowait(None)

    return queue, asyncio.create_task(work())
