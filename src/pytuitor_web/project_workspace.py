"""Durable project lineage, independent drafts, and portable source exports."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import tempfile
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from pytuitor_web.models import ProjectMilestone
from pytuitor_web.platform_files import is_link, replace_profile, sync_directory
from pytuitor_web.workspace import WorkspaceError, export_stage_backup, export_workspace, validate_files

if TYPE_CHECKING:
    from pytuitor_web.state import Store


class ProjectError(WorkspaceError):
    """An actionable project operation failure that preserves existing drafts."""


def _encoded(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()


def validate_projects(projects: object) -> None:
    if not isinstance(projects, dict):
        raise ValueError("Invalid project progress")
    for key, project in projects.items():
        if not isinstance(key, str) or not isinstance(project, dict):
            raise ValueError("Invalid project record")
        if project.get("last_milestone") is not None and not isinstance(
            project["last_milestone"], str
        ):
            raise ValueError("Invalid project resume state")
        milestones = project.get("milestones", {})
        if not isinstance(milestones, dict):
            raise ValueError("Invalid milestone progress")
        # Reuse the existing complete stage-record validation without importing Store at load time.
        from pytuitor_web.state import Store

        Store._validate({"version": 3, "onboarded": True, "familiar": [], "lessons": milestones})
        for entry in milestones.values():
            capabilities = entry.get("base_capabilities", [])
            if not isinstance(capabilities, list) or not all(
                isinstance(item, str) for item in capabilities
            ):
                raise ValueError("Invalid inherited capabilities")
            if type(entry.get("supported_base", False)) is not bool:
                raise ValueError("Invalid project provenance")
            if "base_files" in entry:
                validate_files(entry["base_files"])
            if entry.get("base_origin", "blank") not in (
                "blank",
                "supplied",
                "learner",
                "restored",
            ):
                raise ValueError("Invalid project base origin")
            if entry.get("parent") is not None and not re.fullmatch(
                r"[a-f0-9]{64}", str(entry["parent"])
            ):
                raise ValueError("Invalid parent checkpoint")
            if entry.get("checkpoint") is not None and not re.fullmatch(
                r"[a-f0-9]{64}", str(entry["checkpoint"])
            ):
                raise ValueError("Invalid working checkpoint")
        checkpoints = project.get("checkpoints", [])
        if not isinstance(checkpoints, list):
            raise ValueError("Invalid checkpoint history")
        for item in checkpoints:
            if not isinstance(item, dict) or not re.fullmatch(
                r"[a-f0-9]{64}", str(item.get("id", ""))
            ):
                raise ValueError("Invalid checkpoint identity")
            if not isinstance(item.get("milestone"), str) or type(item.get("revision")) is not int:
                raise ValueError("Invalid checkpoint revision")
            if not isinstance(item.get("capabilities"), list) or not all(
                isinstance(x, str) for x in item["capabilities"]
            ):
                raise ValueError("Invalid checkpoint capabilities")
            if (
                type(item.get("bytes", 0)) is not int
                or item.get("bytes", 0) < 0
                or type(item.get("supported", False)) is not bool
                or not isinstance(item.get("created", ""), str)
            ):
                raise ValueError("Invalid checkpoint metadata")


class ProjectWorkspace:
    def __init__(self, store: Store, project_id: str = "lantern-reach"):
        self.store = store
        self.project_id = project_id

    @property
    def data(self) -> dict:
        return self.store.data.setdefault("projects", {}).setdefault(
            self.project_id, {"milestones": {}, "checkpoints": []}
        )

    @property
    def directory(self) -> Path:
        path = self.store.directory / "projects" / self.project_id / "checkpoints"
        if any(is_link(parent) for parent in (path, *path.parents)):
            raise ProjectError(
                "Project storage contains a symbolic link. Choose a regular profile directory."
            )
        return path

    def read_checkpoint(self, identifier: str) -> dict:
        if not re.fullmatch(r"[a-f0-9]{64}", identifier):
            raise ProjectError("Invalid checkpoint identity.")
        path = self.directory / f"{identifier}.json"
        try:
            if is_link(path) or path.stat().st_size > 8 * 1024 * 1024:
                raise ValueError("unsafe snapshot file")
            payload = json.loads(path.read_bytes())
            if hashlib.sha256(_encoded(payload)).hexdigest() != identifier:
                raise ValueError("snapshot contents changed")
            validate_files(payload["files"])
            if payload["project"] != self.project_id:
                raise ValueError("wrong project")
            return payload
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise ProjectError(
                "This checkpoint is missing or damaged. Your draft is preserved; "
                "choose another checkpoint or a supplied base."
            ) from error

    def compatible(self, milestone: ProjectMilestone) -> list[dict]:
        from pytuitor_web.project_catalog import BY_MILESTONE, MILESTONES

        positions = {item.lesson.id: index for index, item in enumerate(MILESTONES)}

        return [
            item
            for item in reversed(self.data["checkpoints"])
            if set(milestone.requires) <= set(item["capabilities"])
            and item["milestone"] != milestone.lesson.id
            and item["milestone"] in BY_MILESTONE
            and positions[item["milestone"]] < positions[milestone.lesson.id]
            and item["revision"] == BY_MILESTONE[item["milestone"]].lesson.revision
        ]

    def contract(self, milestone: ProjectMilestone, stage: str):
        """Also protect optional capabilities carried in from the chosen parent."""
        contract = milestone.lesson.stage_contract(stage)
        if stage != "build":
            return contract
        from pytuitor_web.project_catalog import MILESTONES

        inherited = set(self.entry(milestone).get("base_capabilities", []))
        extra = inherited - set(milestone.provides)
        checks = list(contract.checks)
        labels = {check.label for check in checks}
        for other in MILESTONES:
            if other.provides[-1] not in extra:
                continue
            for check in other.lesson.stage_contract("build").checks:
                if check.label not in labels:
                    checks.append(check)
                    labels.add(check.label)
        return replace(contract, checks=tuple(checks))

    def entry(self, milestone: ProjectMilestone) -> dict:
        entries = self.data["milestones"]
        if milestone.lesson.id in entries:
            return entries[milestone.lesson.id]
        return self.start(milestone)

    def start(
        self, milestone: ProjectMilestone, *, supplied: bool = False, parent: str | None = None
    ) -> dict:
        entries = self.data["milestones"]
        if milestone.lesson.id in entries:
            raise ProjectError(
                "This milestone already has a draft. Back it up before choosing another base."
            )
        candidates = self.compatible(milestone)
        parent = parent or (candidates[0]["id"] if candidates and not supplied else None)
        base = dict(milestone.base_files)
        origin = "supplied" if milestone.requires else "blank"
        supported = bool(milestone.requires)
        capabilities: list[str] = []
        if parent:
            payload = self.read_checkpoint(parent)
            if not set(milestone.requires) <= set(payload["capabilities"]):
                raise ProjectError(
                    "That checkpoint lacks this milestone's preparation. Choose a compatible base."
                )
            base = dict(payload["files"])
            origin = "learner"
            supported = payload["supported"]
            capabilities = payload["capabilities"]
        # New required files start blank unless an explicit earlier-code scaffold exists.
        for name in milestone.lesson.files:
            base.setdefault(name, milestone.base_files.get(name, ""))
        validate_files(base)
        entry = {
            "files": dict(base),
            "code": base[milestone.lesson.entrypoint],
            "revision": milestone.lesson.revision,
            "stage": "build",
            "base_files": dict(base),
            "base_origin": origin,
            "parent": parent,
            "supported_base": supported,
            "base_capabilities": capabilities,
        }
        entries[milestone.lesson.id] = entry
        return entry

    def checkpoint(
        self, milestone: ProjectMilestone, files: dict[str, str], checks: list[dict]
    ) -> dict:
        files = validate_files(files)
        entry = self.entry(milestone)
        if not checks or not all(case.get("passed") is True for case in checks):
            raise ProjectError("A working checkpoint needs a complete passing check result.")
        if len(checks) != len(self.contract(milestone, "build").checks):
            raise ProjectError("The check result is incomplete. Check the current draft again.")
        if entry.get("files") != files:
            raise ProjectError("The draft changed after checking. Check the current files again.")
        payload = {
            "project": self.project_id,
            "milestone": milestone.lesson.id,
            "revision": milestone.lesson.revision,
            "parent": entry.get("parent"),
            "capabilities": list(
                dict.fromkeys([*entry.get("base_capabilities", []), *milestone.provides])
            ),
            "supported": bool(entry.get("supported_base") or entry.get("solution_seen")),
            "reference_seen": bool(entry.get("solution_seen")),
            "base_origin": entry["base_origin"],
            "files": dict(files),
            "checks": [{"label": case["label"], "passed": True} for case in checks],
        }
        raw = _encoded(payload)
        identifier = hashlib.sha256(raw).hexdigest()
        directory = self.directory
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / f"{identifier}.json"
        if target.exists():
            self.read_checkpoint(identifier)
        else:
            descriptor, temporary = tempfile.mkstemp(prefix=".checkpoint-", dir=directory)
            try:
                with os.fdopen(descriptor, "wb") as stream:
                    stream.write(raw)
                    stream.flush()
                    os.fsync(stream.fileno())
                replace_profile(temporary, target)
                sync_directory(directory)
            finally:
                Path(temporary).unlink(missing_ok=True)
        metadata = {
            "id": identifier,
            "milestone": milestone.lesson.id,
            "revision": milestone.lesson.revision,
            "capabilities": payload["capabilities"],
            "created": datetime.now(UTC).isoformat(),
            "supported": payload["supported"],
            "bytes": len(raw),
        }
        previous = copy.deepcopy(self.data)
        if not any(item["id"] == identifier for item in self.data["checkpoints"]):
            self.data["checkpoints"].append(metadata)
        entry["checkpoint"] = identifier
        entry["checked_files"] = dict(files)
        entry["checked_code"] = files[milestone.lesson.entrypoint]
        entry["checked_revision"] = milestone.lesson.revision
        try:
            self.store.save()
        except OSError:
            self.store.data["projects"][self.project_id] = previous
            raise
        return metadata

    def backup(self, milestone: ProjectMilestone) -> Path:
        entry = self.entry(milestone)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        return export_stage_backup(
            self.store.directory / "exports" / f"{milestone.lesson.id}-attempt-{stamp}",
            entry["files"],
            entry.get("repair", {}).get("files", {}),
        )

    def replace_base(self, milestone: ProjectMilestone, identifier: str | None = None) -> Path:
        if identifier:
            payload = self.read_checkpoint(identifier)
            if not set(milestone.requires) <= set(payload["capabilities"]):
                raise ProjectError("That checkpoint cannot prepare this milestone.")
        backup = self.backup(milestone)
        old = copy.deepcopy(self.data["milestones"][milestone.lesson.id])
        del self.data["milestones"][milestone.lesson.id]
        try:
            fresh = self.start(milestone, supplied=identifier is None, parent=identifier)
            if identifier:
                fresh["base_origin"] = "restored"
            self.store.save()
        except (OSError, ProjectError):
            self.data["milestones"][milestone.lesson.id] = old
            raise
        return backup

    def export_checkpoint(self, identifier: str, destination: Path | None = None) -> Path:
        payload = self.read_checkpoint(identifier)
        files = dict(payload["files"])
        # Tutor metadata lives under reserved, collision-checked names.
        for name in ("PYTUITOR-EXPORT.md", "pytuitor-checkpoint.json"):
            if name in files:
                raise ProjectError(f"Rename {name} in your draft before exporting with provenance.")
        metadata = {}
        metadata["PYTUITOR-EXPORT.md"] = (
            "# Lantern Reach\n\nRun with Python 3.11 or newer:\n\n"
            "```sh\npython game.py\n```\n\n"
            "The game runs offline without Pytuitor.\n"
            "Available commands appear when the game starts.\n"
            "Earlier milestones are deliberately smaller games.\n\n"
            f"Milestone: {payload['milestone']} (revision {payload['revision']}).\n"
            "Supplied earlier code or revealed reference in this lineage: "
            f"{payload['supported']}.\n"
        )
        metadata["pytuitor-checkpoint.json"] = (
            json.dumps(
                {key: value for key, value in payload.items() if key != "files"}
                | {"snapshot": identifier},
                indent=2,
            )
            + "\n"
        )
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        return export_workspace(
            destination or self.store.directory / "exports" / f"lantern-reach-{stamp}",
            files,
            metadata=metadata,
        )
