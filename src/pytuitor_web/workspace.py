"""Bounded project files and safe exports.

These helpers protect tutor-owned paths from accidental traversal and replacement.
"""

from __future__ import annotations

import contextlib
import os
import re
import shutil
import tempfile
import unicodedata
from pathlib import Path, PurePosixPath

from pytuitor_web.platform_files import is_link

MAX_FILES = 32
MAX_FILE_BYTES = 256 * 1024
MAX_WORKSPACE_BYTES = 1024 * 1024
_RESERVED = {".git", ".venv", "__pycache__"}


class WorkspaceError(ValueError):
    """An operation could not safely complete; its message is learner-facing."""


def validate_files(files: dict[str, str]) -> dict[str, str]:
    """Return a copy after checking paths, collisions, and UTF-8 size limits."""
    return _validate_files(files, MAX_FILES, MAX_WORKSPACE_BYTES)


def _validate_files(files: dict[str, str], file_limit: int, byte_limit: int) -> dict[str, str]:
    if not isinstance(files, dict) or not files or len(files) > file_limit:
        raise WorkspaceError(f"A workspace needs between 1 and {file_limit} files.")
    result: dict[str, str] = {}
    normalized: set[str] = set()
    total = 0
    for name, source in files.items():
        if not isinstance(name, str) or not isinstance(source, str):
            raise WorkspaceError("File names and contents must be text.")
        try:
            name_size = len(name.encode("utf-8"))
        except UnicodeEncodeError as error:
            raise WorkspaceError("File names must be valid UTF-8 text.") from error
        parts = name.split("/")
        if (
            not name
            or name_size > 240
            or PurePosixPath(name).is_absolute()
            or "\\" in name
            or any(char in name for char in '<>:"|?*')
            or any(ord(char) < 32 or ord(char) == 127 for char in name)
            or any(part in {"", ".", ".."} or part.endswith((" ", ".")) for part in parts)
            or any(part.casefold() in _RESERVED for part in parts)
            or any(
                re.fullmatch(
                    r"(?i:con|conin\$|conout\$|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³])",
                    part.split(".")[0].rstrip(),
                )
                for part in parts
            )
        ):
            raise WorkspaceError(f"Use a relative project file name without traversal: {name!r}.")
        folded = unicodedata.normalize("NFC", name).casefold()
        if folded in normalized:
            raise WorkspaceError("File names must also be unique on case-insensitive systems.")
        normalized.add(folded)
        try:
            size = len(source.encode("utf-8"))
        except UnicodeEncodeError as error:
            raise WorkspaceError("File contents must be valid UTF-8 text.") from error
        if size > MAX_FILE_BYTES:
            raise WorkspaceError(f"{name} exceeds the {MAX_FILE_BYTES // 1024} KiB file limit.")
        total += size
        result[name] = source
    for name in normalized:
        if any(parent.as_posix() in normalized for parent in PurePosixPath(name).parents):
            raise WorkspaceError("A project path cannot be both a file and a directory.")
    if total > byte_limit:
        raise WorkspaceError("The workspace exceeds the 1 MiB total size limit.")
    return result


def _destination(path: Path) -> Path:
    path = Path(os.path.abspath(path.expanduser()))
    if any(is_link(parent) for parent in (path, *path.parents)):
        raise WorkspaceError("Choose a destination without symbolic-link directories.")
    if path.exists():
        raise WorkspaceError(f"Destination already exists: {path.name}.")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise WorkspaceError(f"Could not create the parent directory: {error.strerror}.") from error
    return path


def export_workspace(
    destination: Path, files: dict[str, str], *, metadata: dict[str, str] | None = None
) -> Path:
    """Export all files atomically into a new directory, never an existing one."""
    checked = validate_files(files)
    if metadata:
        notes = validate_files(metadata)
        if checked.keys() & notes.keys():
            raise WorkspaceError("Export metadata would overwrite a workspace file.")
        # Tutor-added metadata must not consume the learner's source budget.
        checked = _validate_files(
            checked | notes,
            MAX_FILES + len(notes),
            MAX_WORKSPACE_BYTES + sum(len(text.encode("utf-8")) for text in notes.values()),
        )
    return _export_validated(destination, checked)


def export_stage_backup(destination: Path, extend: dict, repair: dict) -> Path:
    """Atomically back up two separately bounded stages under distinct directories."""
    files = {f"extend/{name}": source for name, source in validate_files(extend).items()}
    if repair:
        files.update({f"repair/{name}": source for name, source in validate_files(repair).items()})
    return _export_validated(destination, files)


def _export_validated(destination: Path, checked: dict[str, str]) -> Path:
    path = _destination(destination)
    staging = Path(tempfile.mkdtemp(prefix=f".{path.name}-", dir=path.parent))
    reserved = False
    try:
        for name, source in checked.items():
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source, encoding="utf-8")
        # Exclusive reservation prevents replacing a directory another export created.
        if os.name == "nt":
            # Windows rename fails if *any* destination exists, including an empty folder.
            staging.rename(path)
        else:
            path.mkdir(mode=0o700)
            reserved = True
            staging.replace(path)
        return path
    except OSError as error:
        if reserved:
            with contextlib.suppress(OSError):
                path.rmdir()
        raise WorkspaceError(f"Could not export the workspace: {error.strerror}.") from error
    finally:
        shutil.rmtree(staging, ignore_errors=True)
