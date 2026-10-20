"""Standard-library Win32 operations, imported only on Windows.

The tutor owns the kill-on-close job; the launcher joins before starting user code.
This also covers interpreters reached through Windows virtual-environment redirectors.
"""

import ctypes
import os
import subprocess
import sys
import uuid
from contextlib import contextmanager
from ctypes import wintypes
from pathlib import Path

kernel = ctypes.WinDLL("kernel32", use_last_error=True)
SIZE_T = ctypes.c_size_t


def _function(name, arguments, result=wintypes.BOOL):
    function = getattr(kernel, name)
    function.argtypes = arguments
    function.restype = result
    return function


_close = _function("CloseHandle", [wintypes.HANDLE])
_create_job = _function("CreateJobObjectW", [ctypes.c_void_p, wintypes.LPCWSTR], wintypes.HANDLE)
_set_job = _function(
    "SetInformationJobObject", [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
)
_assign_job = _function("AssignProcessToJobObject", [wintypes.HANDLE, wintypes.HANDLE])
_open_job = _function(
    "OpenJobObjectW", [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR], wintypes.HANDLE
)
_terminate_job = _function("TerminateJobObject", [wintypes.HANDLE, wintypes.UINT])
_query_job = _function(
    "QueryInformationJobObject",
    [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p],
)
_current_process = _function("GetCurrentProcess", [], wintypes.HANDLE)
_move = _function("MoveFileExW", [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD])
_create_file = _function(
    "CreateFileW",
    [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ],
    wintypes.HANDLE,
)
_file_info = _function("GetFileInformationByHandle", [wintypes.HANDLE, ctypes.c_void_p])


class BasicLimits(ctypes.Structure):
    _fields_ = [
        ("process_time", ctypes.c_int64),
        ("job_time", ctypes.c_int64),
        ("flags", wintypes.DWORD),
        ("minimum_working_set", SIZE_T),
        ("maximum_working_set", SIZE_T),
        ("active_processes", wintypes.DWORD),
        ("affinity", SIZE_T),
        ("priority", wintypes.DWORD),
        ("scheduling", wintypes.DWORD),
    ]


class ExtendedLimits(ctypes.Structure):
    _fields_ = [
        ("basic", BasicLimits),
        ("io_counters", ctypes.c_uint64 * 6),
        ("process_memory", SIZE_T),
        ("job_memory", SIZE_T),
        ("peak_process_memory", SIZE_T),
        ("peak_job_memory", SIZE_T),
    ]


class FileInformation(ctypes.Structure):
    _fields_ = [
        ("attributes", wintypes.DWORD),
        ("creation", wintypes.FILETIME),
        ("access", wintypes.FILETIME),
        ("write", wintypes.FILETIME),
        ("volume", wintypes.DWORD),
        ("size_high", wintypes.DWORD),
        ("size_low", wintypes.DWORD),
        ("links", wintypes.DWORD),
        ("index_high", wintypes.DWORD),
        ("index_low", wintypes.DWORD),
    ]


def replace_profile(source: str, destination: Path) -> None:
    # Same-volume replacement, with write-through rather than Unix directory fsync.
    if not _move(str(source), str(destination), 0x1 | 0x8):
        raise ctypes.WinError(ctypes.get_last_error())


@contextmanager
def open_path(path: Path, *, directory: bool = False):
    """Pin an entry against rename, refuse reparse points, and own its handle."""
    import msvcrt

    handle = _create_file(
        str(path),
        0 if directory else 0x80000000,
        0x1 | 0x2,
        None,
        3,
        0x00200000 | 0x02000000,
        None,
    )
    if handle == wintypes.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        information = FileInformation()
        if not _file_info(handle, ctypes.byref(information)):
            raise ctypes.WinError(ctypes.get_last_error())
        if information.attributes & 0x400:
            raise OSError("Symbolic links and reparse points are not run files")
        if bool(information.attributes & 0x10) != directory:
            raise OSError("The run-file entry changed type")
        if directory:
            yield None
        else:
            descriptor = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
            handle = None  # The file descriptor now owns it.
            with os.fdopen(descriptor, "rb") as stream:
                yield stream
    finally:
        if handle is not None:
            _close(handle)


class Accounting(ctypes.Structure):
    _fields_ = [
        ("times", ctypes.c_int64 * 4),
        ("page_faults", wintypes.DWORD),
        ("total_processes", wintypes.DWORD),
        ("active_processes", wintypes.DWORD),
        ("terminated_processes", wintypes.DWORD),
    ]


class Job:
    """A controller-owned process tree, independent of interpreter launcher PIDs."""

    def __init__(self, limits=None):
        self.name = "Local\\Pytuitor-" + uuid.uuid4().hex
        self.handle = _create_job(None, self.name)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        information = ExtendedLimits()
        information.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if limits:
            information.basic.flags |= 0x2 | 0x200  # CPU time and job memory.
            information.basic.process_time = limits["cpu_seconds"] * 10_000_000
            information.job_memory = limits["memory_bytes"]
        if not _set_job(self.handle, 9, ctypes.byref(information), ctypes.sizeof(information)):
            error = ctypes.get_last_error()
            self.close()
            raise ctypes.WinError(error)

    def terminate(self):
        if not _terminate_job(self.handle, 1):
            raise ctypes.WinError(ctypes.get_last_error())

    def empty(self):
        information = Accounting()
        if not _query_job(
            self.handle, 1, ctypes.byref(information), ctypes.sizeof(information), None
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        return information.active_processes == 0

    def close(self):
        if self.handle is not None:
            _close(self.handle)
            self.handle = None


def launch() -> None:
    job = _open_job(0x1, False, sys.argv[1])  # JOB_OBJECT_ASSIGN_PROCESS
    if not job:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        if not _assign_job(job, _current_process()):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        # Only the tutor retains ownership. If it exits, no child can keep the
        # job alive; a controller crash during this handshake cannot run code.
        _close(job)
    code = subprocess.call(sys.argv[2:])
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(ctypes.c_int(code).value)


if __name__ == "__main__":
    launch()
