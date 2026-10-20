"""Native process observations shared by cancellation and recovery journeys."""

import os

import pytest


@pytest.fixture
def process_is_running():
    def alive(pid):
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes

            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
            kernel.OpenProcess.restype = wintypes.HANDLE
            kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
            kernel.CloseHandle.argtypes = [wintypes.HANDLE]
            handle = kernel.OpenProcess(0x1000, False, pid)
            if not handle:
                assert ctypes.get_last_error() == 87  # No such process.
                return False
            try:
                code = wintypes.DWORD()
                assert kernel.GetExitCodeProcess(handle, ctypes.byref(code))
                return code.value == 259  # STILL_ACTIVE
            finally:
                kernel.CloseHandle(handle)
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        # Linux may retain an orphan as a zombie briefly after it has stopped.
        from pathlib import Path

        status = Path(f"/proc/{pid}/stat")
        try:
            return status.read_text().split(")", 1)[1].split()[0] != "Z"
        except FileNotFoundError:
            return True

    return alive
