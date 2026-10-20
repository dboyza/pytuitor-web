"""Shared subprocess boundaries, independent of the UI and third-party packages."""

import asyncio
import contextlib
import os
import signal
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytuitor_web._windows import Job

OUTPUT_BYTES = 64 * 1024
EXECUTION_SECONDS = 5.0
WORKER_LIMITS = {
    "cpu_seconds": 4,
    "file_bytes": 1024 * 1024,
    "memory_bytes": 512 * 1024 * 1024,
    "output_bytes": OUTPUT_BYTES,
}


def clean_environment(home: str, *, temporary: bool = False) -> dict[str, str]:
    """Do not forward credentials, Python overrides, or installer configuration."""
    environment = {
        "PATH": os.defpath,
        "HOME": home,
        "PYTHONIOENCODING": "utf-8",
        "PIP_CONFIG_FILE": os.devnull,
        # Practice servers run locally; never route them through a configured proxy.
        "NO_PROXY": "127.0.0.1,localhost",
    }
    if os.name == "nt":
        for name in ("SystemRoot", "WINDIR", "COMSPEC", "PATHEXT"):
            if name in os.environ:
                environment[name] = os.environ[name]
        environment["USERPROFILE"] = home
        environment["TEMP"] = home
        environment["TMP"] = home
    if temporary:
        environment["TMPDIR"] = home
    return environment


@dataclass
class ProcessTree:
    process: asyncio.subprocess.Process
    job: "Job | None" = None

    async def close(self) -> None:
        process = self.process
        if process.stdin is not None:
            process.stdin.close()
        try:
            if self.job is not None:
                self.job.terminate()
            with contextlib.suppress(ProcessLookupError):
                if os.name == "nt":
                    process.kill()  # Also stop an outer venv redirector, if present.
                else:
                    os.killpg(process.pid, signal.SIGKILL)
            if self.job is not None:
                async with asyncio.timeout(5):
                    while not self.job.empty():
                        await asyncio.sleep(0.01)
                    await process.wait()
            else:
                await process.wait()
        finally:
            if self.job is not None:
                self.job.close()


async def start_process(*arguments: str, limits: dict | None = None, **options) -> ProcessTree:
    """Install cleanup before a launcher can start any requested Python code."""
    arguments = (arguments[0], "-X", "utf8", *arguments[1:])
    job = None
    if os.name == "nt":
        from pytuitor_web._windows import Job

        job = Job(limits)
        arguments = (
            arguments[0],
            "-I",
            "-X",
            "utf8",
            str(Path(__file__).with_name("_windows.py")),
            job.name,
            *arguments,
        )
    try:
        process = await asyncio.create_subprocess_exec(
            *arguments, start_new_session=os.name != "nt", **options
        )
        return ProcessTree(process, job)
    except BaseException:
        if job is not None:
            job.close()
        raise
