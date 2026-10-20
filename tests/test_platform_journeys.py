"""Behavioral coverage for Windows and Unix execution and persistence boundaries."""

import asyncio
import json
import os
import subprocess
import sys

import pytest

from pytuitor_web.curriculum import LESSONS
from pytuitor_web.execution_policy import start_process
from pytuitor_web.runner import execute
from pytuitor_web.state import Store
from pytuitor_web.workspace import WorkspaceError, export_workspace, validate_files


@pytest.mark.parametrize(
    "name",
    [
        "CON.py",
        "CONIN$",
        "CONOUT$.txt",
        "aux",
        "NUL.txt",
        "Com1/data.py",
        "lpt².log",
        "a?.py",
        "a*.py",
        'a".py',
        "a|b.py",
        "a<b.py",
    ],
)
def test_reject_windows_devices_and_invalid_characters_on_every_platform(name):
    with pytest.raises(WorkspaceError):
        validate_files({name: ""})


async def test_unicode_paths_input_output_and_generated_files(tmp_path):
    source = "from pathlib import Path\nname = input('Name: ')\nprint('Hello, ' + name)\n"
    source += "Path('résumé.txt').write_text(name + '\\n', encoding='utf-8')\n"
    result = await execute(LESSONS[0], source, "Zoë 🐍\n", check=False)
    assert not result.error
    assert result.output == "Name: Hello, Zoë 🐍\n"
    assert result.files["résumé.txt"] == "Zoë 🐍\n"
    destination = export_workspace(tmp_path / "project café", result.files)
    assert (destination / "résumé.txt").read_text(encoding="utf-8") == "Zoë 🐍\n"


@pytest.mark.parametrize("cancel", [False, True], ids=["parent-exits", "cancelled"])
async def test_process_tree_stops_descendants(tmp_path, process_is_running, cancel):
    pid_file = tmp_path / "grandchild.pid"
    child = (
        "import os, pathlib, time; "
        f"pathlib.Path({str(pid_file)!r}).write_text(str(os.getpid())); time.sleep(60)"
    )
    wait_for_child = (
        f"from pathlib import Path\nwhile not Path({str(pid_file)!r}).exists(): time.sleep(.01)"
    )
    parent = (
        "import subprocess, sys, time; "
        f"subprocess.Popen([sys.executable, '-c', {child!r}], "
        "stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); "
        + ("time.sleep(60)" if cancel else f"exec({wait_for_child!r})")
    )
    tree = await start_process(
        sys.executable,
        "-c",
        parent,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    async def run():
        try:
            await tree.process.wait()
        finally:
            await tree.close()

    task = asyncio.create_task(run())
    async with asyncio.timeout(15):
        while not pid_file.exists():
            await asyncio.sleep(0.02)
        if cancel:
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        else:
            await task
        pid = int(pid_file.read_text())
        while process_is_running(pid):
            await asyncio.sleep(0.02)
    assert not process_is_running(tree.process.pid)


def test_profile_lock_is_released_after_process_crash(tmp_path):
    code = (
        "import os, sys; from pathlib import Path; from pytuitor_web.state import Store; "
        "store = Store(Path(sys.argv[1])); store.data['onboarded'] = True; "
        "store.save(); os._exit(7)"
    )
    result = subprocess.run([sys.executable, "-c", code, str(tmp_path)], timeout=15)
    assert result.returncode == 7
    store = Store(tmp_path)
    assert store.data["onboarded"]
    assert not store.durability_warning
    store.close()


@pytest.mark.skipif(os.name != "nt", reason="Native Windows write-through replacement")
def test_windows_failed_replace_preserves_profile(tmp_path, monkeypatch):
    import ctypes

    from pytuitor_web import _windows

    store = Store(tmp_path)
    store.save()
    before = store.path.read_bytes()

    def deny(*args):
        ctypes.set_last_error(5)
        return False

    monkeypatch.setattr(_windows, "_move", deny)
    store.data["onboarded"] = True
    with pytest.raises(OSError):
        store.save()
    assert store.path.read_bytes() == before
    assert not list(tmp_path.glob(".profile-*"))
    store.close()
    assert not json.loads(before)["onboarded"]


@pytest.mark.skipif(os.name != "nt", reason="Native Windows junctions")
def test_windows_junctions_are_not_export_destinations_or_run_files(tmp_path):
    from pytuitor_web.run_files import collect_run_files

    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "private.txt").write_text("private")
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    junction = workspace / "junction"
    subprocess.run(
        ["cmd.exe", "/d", "/c", "mklink", "/J", str(junction), str(outside)],
        check=True,
        capture_output=True,
    )
    try:
        with pytest.raises(WorkspaceError, match="symbolic"):
            export_workspace(junction / "export", {"main.py": ""})
        files, notice = collect_run_files(workspace)
        assert files == {}
        assert "symbolic links" in notice
    finally:
        junction.rmdir()


@pytest.mark.skipif(os.name != "nt", reason="Controller-owned Windows Job Objects")
async def test_windows_controller_crash_stops_its_worker(tmp_path, process_is_running):
    pid_file = tmp_path / "worker.pid"
    worker = (
        "import os, pathlib, time; "
        f"pathlib.Path({str(pid_file)!r}).write_text(str(os.getpid())); time.sleep(60)"
    )
    controller = (
        "import asyncio, os, sys\n"
        "from pathlib import Path\n"
        "from pytuitor_web.execution_policy import start_process\n"
        "async def main():\n"
        f"    await start_process(sys.executable, '-c', {worker!r})\n"
        f"    while not Path({str(pid_file)!r}).exists():\n"
        "        await asyncio.sleep(.01)\n"
        "    os._exit(7)\n"
        "asyncio.run(main())\n"
    )
    process = await asyncio.create_subprocess_exec(sys.executable, "-c", controller)
    async with asyncio.timeout(15):
        await process.wait()
        assert process.returncode == 7
        pid = int(pid_file.read_text())
        while process_is_running(pid):
            await asyncio.sleep(0.02)
