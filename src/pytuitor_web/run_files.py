"""Bounded run snapshots that refuse links and keep traversed directories pinned."""

import os
import stat
from collections import Counter
from contextlib import contextmanager
from pathlib import Path

from pytuitor_web.platform_files import is_link


@contextmanager
def open_directory(name: str | Path, *, parent: int | Path | None = None):
    if os.name == "nt":
        from pytuitor_web._windows import open_path

        path = Path(parent) / name if parent is not None else Path(name)
        with open_path(path, directory=True):
            yield path
    else:
        descriptor = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        try:
            yield descriptor
        finally:
            os.close(descriptor)


@contextmanager
def open_file(name: str, *, parent: int | Path):
    if os.name == "nt":
        from pytuitor_web._windows import open_path

        with open_path(Path(parent) / name) as stream:
            yield stream
    else:
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        with os.fdopen(descriptor, "rb") as stream:
            yield stream


def collect_run_files(directory: Path) -> tuple[dict[str, str], str]:
    """Read a bounded text snapshot without following links or special files."""
    from pytuitor_web.workspace import MAX_FILE_BYTES, MAX_FILES, WorkspaceError, validate_files

    snapshot: dict[str, str] = {}
    skipped: Counter[str] = Counter()
    inspected = 0

    def scan(descriptor: int | Path, prefix: str = "", depth: int = 0) -> None:
        nonlocal inspected
        if depth > 16:
            skipped["deep folders"] += 1
            return
        with os.scandir(descriptor) as entries:
            for entry in entries:
                inspected += 1
                if inspected > 512:
                    skipped["scan limit"] += 1
                    return
                if entry.name == "__pycache__":
                    continue
                name = prefix + entry.name
                try:
                    if entry.is_symlink() or (os.name == "nt" and is_link(Path(entry.path))):
                        skipped["symbolic links"] += 1
                        continue
                    validate_files({name: ""})
                    if entry.is_dir(follow_symlinks=False):
                        with open_directory(entry.name, parent=descriptor) as child:
                            scan(child, name + "/", depth + 1)
                        continue
                    if len(snapshot) >= MAX_FILES:
                        skipped["file-count limit"] += 1
                        continue
                    with open_file(entry.name, parent=descriptor) as stream:
                        information = os.fstat(stream.fileno())
                        if not stat.S_ISREG(information.st_mode):
                            skipped["non-text file types"] += 1
                            continue
                        if information.st_size > MAX_FILE_BYTES:
                            skipped["oversized files"] += 1
                            continue
                        content = stream.read(MAX_FILE_BYTES + 1)
                    if len(content) > MAX_FILE_BYTES:
                        skipped["oversized files"] += 1
                        continue
                    if b"\0" in content:
                        skipped["binary files"] += 1
                        continue
                    source = content.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
                    validate_files({**snapshot, name: source})
                    snapshot[name] = source
                except UnicodeDecodeError:
                    skipped["binary files"] += 1
                except WorkspaceError:
                    skipped["invalid names or workspace limits"] += 1
                except OSError:
                    skipped["unreadable files or folders"] += 1

    try:
        with open_directory(directory) as descriptor:
            scan(descriptor)
    except FileNotFoundError:
        return {}, ""
    except OSError:
        return {}, "Run files were unavailable or the workspace was replaced with a symbolic link."
    notice = "Some run files were omitted: " + ", ".join(sorted(skipped)) + "." if skipped else ""
    return snapshot, notice
