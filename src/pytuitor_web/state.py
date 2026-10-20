"""Versioned local profiles with atomic writes and a single-writer lock."""

import errno
import json
import os
import tempfile
from pathlib import Path

from platformdirs import user_data_path

from pytuitor_web.curriculum import BY_ID, CHAPTERS, CONCEPTS, SECTIONS, Lesson, chapter_activities
from pytuitor_web.platform_files import lock_profile, replace_profile, sync_directory
from pytuitor_web.progress_types import LessonProgress


class ProfileError(Exception):
    pass


def fresh_profile() -> dict:
    return {
        "version": 4,
        "onboarded": False,
        "familiar": [],
        "lessons": {},
        "last_lesson": None,
        "projects": {},
    }


class Store:
    def __init__(self, directory: Path | None = None):
        self.directory = (
            (directory or user_data_path("pytuitor-web", appauthor=False)).expanduser().resolve()
        )
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / "profile.json"
        self._lock = (self.directory / "profile.lock").open("a+b")
        try:
            lock_profile(self._lock)
        except OSError as exc:
            self._lock.close()
            if exc.errno in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                raise ProfileError(
                    "This profile is already open in another Pytuitor window."
                ) from exc
            raise ProfileError(f"Could not lock the profile at {self.directory}: {exc}") from exc
        self._migration_original = None
        self.durability_warning = ""
        self.data = fresh_profile()
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                self._validate(data)
                if data["version"] < 4:
                    self._migration_original = self.path.read_bytes()
                self.data.update(data)
                self.data["version"] = 4
                for legacy_key in ("background", "goal", "diagnostic"):
                    self.data.pop(legacy_key, None)
            except (OSError, ValueError, TypeError, KeyError) as exc:
                self.close()
                raise ProfileError(
                    f"Cannot read profile at {self.path}. Your file was left untouched. "
                    "Use --data-dir with another directory to start a separate profile."
                ) from exc

    @staticmethod
    def _validate(data: object) -> None:
        if not isinstance(data, dict) or data.get("version") not in (1, 2, 3, 4):
            raise ValueError("Unsupported profile version")
        if "track" in data and data["track"] not in ("beginner", "experienced", "custom"):
            raise ValueError("Invalid legacy track")
        if not isinstance(data.get("onboarded"), bool):
            raise ValueError("Invalid onboarding state")
        if data.get("background", "new") not in ("new", "cs", "python"):
            raise ValueError("Invalid background")
        if data.get("goal", "build") not in ("build", "depth", "confidence"):
            raise ValueError("Invalid goal")
        if data.get("last_lesson") is not None and not isinstance(data["last_lesson"], str):
            raise ValueError("Invalid resume state")
        if not isinstance(data.get("familiar"), list) or not all(
            isinstance(item, str) for item in data["familiar"]
        ):
            raise ValueError("Invalid concepts")
        if not isinstance(data.get("lessons"), dict):
            raise ValueError("Invalid lessons")
        for entry in data["lessons"].values():
            if not isinstance(entry, dict):
                raise ValueError("Invalid lesson progress")
            if entry.get("stage", "build") not in ("build", "repair"):
                raise ValueError("Invalid exercise stage")
            repair = entry.get("repair", {})
            if not isinstance(repair, dict):
                raise ValueError("Invalid repair progress")
            for stage_data in (entry, repair):
                for key in ("revision", "checked_revision", "completed_revision"):
                    if key in stage_data and (
                        type(stage_data[key]) is not int or stage_data[key] < 1
                    ):
                        raise ValueError("Invalid exercise revision")
                if "solution_seen" in stage_data and type(stage_data["solution_seen"]) is not bool:
                    raise ValueError("Invalid reference state")
                for files_key in ("files", "checked_files"):
                    if files_key in stage_data:
                        from pytuitor_web.workspace import validate_files

                        file_map = stage_data[files_key]
                        if not isinstance(file_map, dict) or not all(
                            isinstance(value, str) for value in file_map.values()
                        ):
                            raise ValueError("Invalid project draft")
                        # An oversized draft can still be recovered and exported manually.
                        # Execution enforces content limits without locking the learner out.
                        validate_files(dict.fromkeys(file_map, ""))
            for key in ("code", "checked_code"):
                if key in repair and not isinstance(repair[key], str):
                    raise ValueError("Invalid repair draft")
            if "hints" in repair and (type(repair["hints"]) is not int or repair["hints"] < 0):
                raise ValueError("Invalid repair hints")
            for key in ("code", "input", "checked_code"):
                if key in entry and not isinstance(entry[key], str):
                    raise ValueError("Invalid draft")
            if "completed" in entry and not isinstance(entry["completed"], bool):
                raise ValueError("Invalid completion")
            if "prediction" in entry and not isinstance(entry["prediction"], bool):
                raise ValueError("Invalid prediction")
            if "hints" in entry and (type(entry["hints"]) is not int or entry["hints"] < 0):
                raise ValueError("Invalid hints")
        if not isinstance(data.get("diagnostic", {}), dict):
            raise ValueError("Invalid diagnostic")
        if not all(isinstance(value, bool) for value in data.get("diagnostic", {}).values()):
            raise ValueError("Invalid diagnostic answer")
        if "projects" in data:
            from pytuitor_web.project_workspace import validate_projects

            validate_projects(data["projects"])

    def close(self) -> None:
        if not self._lock.closed:
            self._lock.close()

    def reset(self) -> None:
        previous = self.data
        self.data = fresh_profile()
        try:
            self.save()
        except OSError:
            self.data = previous
            raise

    def save(self) -> None:
        self.durability_warning = ""
        if self._migration_original is not None:
            backup = self.directory / "profile-before-v4.json"
            try:
                with backup.open("xb") as stream:
                    stream.write(self._migration_original)
                    stream.flush()
                    os.fsync(stream.fileno())
            except FileExistsError:
                pass
            self._migration_original = None
        fd, temporary = tempfile.mkstemp(prefix=".profile-", dir=self.directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
                json.dump(self.data, stream, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            replace_profile(temporary, self.path)
            # The rename is committed. A sync failure is a durability warning,
            # not a failed transaction that should restore stale in-memory data.
            try:
                sync_directory(self.directory)
            except OSError as error:
                self.durability_warning = (
                    "Progress was written, but its directory could not be synced: " + str(error)
                )
        finally:
            Path(temporary).unlink(missing_ok=True)

    def entry(self, lesson: Lesson) -> LessonProgress:
        if lesson.project_id:
            from pytuitor_web.project_catalog import BY_MILESTONE
            from pytuitor_web.project_workspace import ProjectWorkspace

            return ProjectWorkspace(self, lesson.project_id).entry(BY_MILESTONE[lesson.id])
        return self.data["lessons"].setdefault(lesson.id, {})

    def status(self, lesson: Lesson) -> str:
        if lesson.project_id:
            entry = (
                self.data.get("projects", {})
                .get(lesson.project_id, {})
                .get("milestones", {})
                .get(lesson.id, {})
            )
            if entry.get("completed") and entry.get("completed_revision") == lesson.revision:
                return "completed"
            return "in progress" if entry else "new"
        entry = self.data["lessons"].get(lesson.id, {})
        if entry.get("completed"):
            return "completed"
        if all(concept in self.data["familiar"] for concept in lesson.concepts):
            return "familiar"
        if "code" in entry:
            return "in progress"
        return "new"

    def chapter_next_lesson(self, chapter_id: str) -> Lesson | None:
        return next(
            (
                lesson
                for lesson in chapter_activities(chapter_id)
                if self.status(lesson) not in ("completed", "familiar")
            ),
            None,
        )

    def next_lesson(self) -> Lesson | None:
        """Resume the active chapter, with optional sections entered explicitly."""
        last = BY_ID.get(self.data.get("last_lesson"))
        chapters = {chapter.id: chapter for chapter in CHAPTERS}
        active = chapters.get(last.chapter_id) if last else None
        if active:
            if self.status(last) not in ("completed", "familiar"):
                return last
            pending = self.chapter_next_lesson(active.id)
            if pending:
                return pending
        optional = {section.id for section in SECTIONS if section.optional}
        if active and active.section_id in optional:
            candidates = [
                chapter for chapter in CHAPTERS if chapter.section_id == active.section_id
            ]
        else:
            candidates = [chapter for chapter in CHAPTERS if chapter.section_id not in optional]
        if active in candidates:
            position = candidates.index(active)
            candidates = candidates[position + 1 :] + candidates[: position + 1]
        for chapter in candidates:
            pending = self.chapter_next_lesson(chapter.id)
            if pending:
                return pending
        return None

    def set_familiar(self, concepts: list[str]) -> None:
        self.data["familiar"] = [concept for concept in concepts if concept in CONCEPTS]
