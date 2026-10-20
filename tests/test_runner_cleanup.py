"""Execution must finish cleanup even when Windows briefly retains file handles."""

import asyncio
import os
import tempfile
from pathlib import Path

import pytest

from pytuitor_web.curriculum import LESSONS
from pytuitor_web.runner import execute


@pytest.mark.parametrize("winerror", [5, 32], ids=["access-denied", "sharing-violation"])
async def test_timeout_retries_transient_workspace_locks(monkeypatch, winerror):
    cleanup = tempfile.TemporaryDirectory.cleanup
    attempts = []

    def locked_once(directory):
        if Path(directory.name).name.startswith("pytuitor-run-"):
            attempts.append(Path(directory.name))
            if len(attempts) < 3:
                error = PermissionError("Workspace handle is still closing")
                error.winerror = winerror
                raise error
        cleanup(directory)

    monkeypatch.setattr(tempfile.TemporaryDirectory, "cleanup", locked_once)
    result = await execute(LESSONS[0], "while True: pass", timeout=0.3)
    assert "Stopped after" in result.error
    assert len(attempts) == 3
    assert not attempts[0].exists()


@pytest.mark.skipif(os.name != "nt", reason="Native Windows file sharing locks")
async def test_timeout_waits_for_native_file_handle_release(monkeypatch):
    from pytuitor_web._windows import open_path

    cleanup = tempfile.TemporaryDirectory.cleanup
    attempts = []
    lock = None
    release = None

    def locked_once(directory):
        nonlocal lock, release
        if Path(directory.name).name.startswith("pytuitor-run-"):
            attempts.append(Path(directory.name))
            if len(attempts) == 1:
                lock = open_path(Path(directory.name) / "request.json")
                lock.__enter__()
                release = asyncio.get_running_loop().call_later(0.1, unlock)
        cleanup(directory)

    def unlock():
        nonlocal lock
        if lock is not None:
            lock.__exit__(None, None, None)
            lock = None

    monkeypatch.setattr(tempfile.TemporaryDirectory, "cleanup", locked_once)
    try:
        result = await execute(LESSONS[0], "while True: pass", timeout=0.3)
        assert "Stopped after" in result.error
        assert len(attempts) > 1
        assert not attempts[0].exists()
    finally:
        if release is not None:
            release.cancel()
        unlock()


@pytest.mark.parametrize("winerror", [None, 5, 32], ids=["other-error", "access", "sharing"])
async def test_permanent_cleanup_errors_are_not_hidden(monkeypatch, winerror):
    from pytuitor_web import runner

    attempts = []
    error = PermissionError("Persistent cleanup failure")
    if winerror is not None:
        error.winerror = winerror
    cleanup = tempfile.TemporaryDirectory.cleanup
    monkeypatch.setattr(runner, "WORKSPACE_CLEANUP_SECONDS", 0.06)

    def fail(directory):
        attempts.append(directory)
        raise error

    monkeypatch.setattr(tempfile.TemporaryDirectory, "cleanup", fail)
    try:
        with pytest.raises(PermissionError, match="Persistent cleanup failure"):
            async with runner._run_directory():
                pass
        assert len(attempts) == 1 if winerror is None else len(attempts) > 1
    finally:
        for directory in attempts:
            cleanup(directory)


async def test_cancelled_run_retries_cleanup_and_remains_cancelled(monkeypatch):
    from pytuitor_web.runner import ConsoleSession

    ready = asyncio.Event()
    session = ConsoleSession(lambda text: None, lambda waiting: ready.set() if waiting else None)
    cleanup = tempfile.TemporaryDirectory.cleanup
    attempts = []

    def locked_once(directory):
        attempts.append(directory)
        if len(attempts) == 1:
            error = PermissionError("Handle closing")
            error.winerror = 32
            raise error
        cleanup(directory)

    monkeypatch.setattr(tempfile.TemporaryDirectory, "cleanup", locked_once)
    task = asyncio.create_task(execute(LESSONS[0], "input()", check=False, console=session))
    try:
        await asyncio.wait_for(ready.wait(), 10)
        process = session.process
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert process.returncode is not None
        assert session.process is None
        assert len(attempts) == 2
        assert not Path(attempts[0].name).exists()
    finally:
        if not task.done():
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
