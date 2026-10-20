"""Filesystem operations with explicit Windows and Unix guarantees."""

import os
import stat
from pathlib import Path
from typing import BinaryIO


def lock_profile(stream: BinaryIO) -> None:
    if os.name == "nt":
        import msvcrt

        stream.seek(0, os.SEEK_END)
        if not stream.tell():
            stream.write(b"\0")
            stream.flush()
        stream.seek(0)
        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl

        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)


def replace_profile(source: str, destination: Path) -> None:
    if os.name == "nt":
        from pytuitor_web._windows import replace_profile as replace_windows

        replace_windows(source, destination)
    else:
        os.replace(source, destination)


def sync_directory(directory: Path) -> None:
    if os.name == "nt":
        return  # replace_profile uses MoveFileExW with MOVEFILE_WRITE_THROUGH.
    descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def is_link(path: Path) -> bool:
    """Include Windows junctions and other reparse points, even on Python 3.11."""
    try:
        information = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(information.st_mode) or bool(
        getattr(information, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
    )
