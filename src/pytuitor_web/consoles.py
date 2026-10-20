"""Embedded shells: each is a real PTY on this computer, streamed to the signed-in browser."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
import time
import uuid
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Any

SCROLLBACK = 512 * 1024
TOTAL = 12
# Runs as the new session leader so the shell gets a controlling terminal and job control.
ACQUIRE = (
    "import fcntl, os, sys, termios\n"
    "fcntl.ioctl(0, termios.TIOCSCTTY, 0)\n"
    "os.execvpe(sys.argv[1], sys.argv[1:], os.environ)\n"
)

Listener = Callable[[bytes | None], None]


class ConsoleError(ValueError):
    pass


class _PosixPty:
    def __init__(self, argv: list[str], cwd: str, env: dict[str, str], size: tuple[int, int]):
        master, slave = os.openpty()
        try:
            _set_size(master, *size)
            self.process = subprocess.Popen(
                [sys.executable, "-c", ACQUIRE, *argv],
                cwd=cwd,
                env=env,
                stdin=slave,
                stdout=slave,
                stderr=slave,
                start_new_session=True,
            )
        except BaseException:
            os.close(master)
            raise
        finally:
            os.close(slave)
        self.fd = master

    def read(self) -> bytes:
        try:
            return os.read(self.fd, 65536)
        except OSError:
            return b""

    def write(self, data: bytes) -> None:
        view = memoryview(data)
        with suppress(OSError):
            while view:
                view = view[os.write(self.fd, view) :]

    def resize(self, cols: int, rows: int) -> None:
        _set_size(self.fd, cols, rows)

    def busy(self) -> bool:
        """A foreground job other than the shell itself owns the terminal."""
        try:
            return os.tcgetpgrp(self.fd) != self.process.pid
        except OSError:
            return False

    def wait(self) -> int:
        code = self.process.wait()
        os.close(self.fd)
        return code

    def hang_up(self) -> None:
        """Hang up the shell's session the way closing a terminal window does."""
        try:
            os.killpg(self.process.pid, signal.SIGHUP)
        except ProcessLookupError:
            return

        def escalate() -> None:
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                with suppress(ProcessLookupError):
                    os.killpg(self.process.pid, signal.SIGKILL)

        threading.Thread(target=escalate, daemon=True).start()


class _WindowsPty:
    def __init__(self, argv: list[str], cwd: str, env: dict[str, str], size: tuple[int, int]):
        from winpty import PtyProcess

        cols, rows = _clamp(*size)
        self.process = PtyProcess.spawn(argv, cwd=cwd, env=env, dimensions=(rows, cols))

    def read(self) -> bytes:
        try:
            return self.process.read(65536).encode("utf-8", "replace")
        except EOFError:
            return b""

    def write(self, data: bytes) -> None:
        with suppress(OSError, EOFError):
            self.process.write(data.decode("utf-8", "replace"))

    def resize(self, cols: int, rows: int) -> None:
        cols, rows = _clamp(cols, rows)
        self.process.setwinsize(rows, cols)

    def busy(self) -> bool:
        return False

    def wait(self) -> int:
        while self.process.isalive():
            time.sleep(0.1)
        return self.process.exitstatus or 0

    def hang_up(self) -> None:
        with suppress(Exception):
            self.process.terminate(force=True)


@dataclass
class Console:
    id: str
    key: str
    title: str
    number: int
    pty: _PosixPty | _WindowsPty
    on_exit: Callable[[], None] | None = None
    buffer: bytearray = field(default_factory=bytearray)
    listeners: set[Listener] = field(default_factory=set)
    exit_code: int | None = None
    ended: bool = False

    def public(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "key": self.key,
            "title": self.title,
            "number": self.number,
            "alive": not self.ended,
            "exit_code": self.exit_code,
        }


def _trim(buffer: bytearray) -> None:
    """Drop the oldest output, cutting at a line break so replay starts cleanly."""
    excess = len(buffer) - SCROLLBACK
    if excess <= 0:
        return
    newline = buffer.find(b"\n", excess)
    del buffer[: newline + 1 if 0 <= newline < excess + 4096 else excess]


class Consoles:
    def __init__(self) -> None:
        self._items: dict[str, Console] = {}
        self._lock = threading.Lock()

    def public(self) -> list[dict[str, Any]]:
        with self._lock:
            return [item.public() for item in self._items.values()]

    def find(self, key: str) -> list[dict[str, Any]]:
        with self._lock:
            return [item.public() for item in self._items.values() if item.key == key]

    def open(
        self,
        key: str,
        title: str,
        argv: list[str],
        cwd: str,
        env: dict[str, str],
        size: tuple[int, int],
        on_exit: Callable[[], None] | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            if sum(not item.ended for item in self._items.values()) >= TOTAL:
                raise ConsoleError(
                    f"{TOTAL} terminals are already open. Close one in another lesson first."
                )
            ended = [item.id for item in self._items.values() if item.ended]
            for old in ended[: max(0, len(ended) - TOTAL)]:
                self._items.pop(old)
            taken = {item.number for item in self._items.values() if item.key == key}
            number = next(n for n in range(1, len(taken) + 2) if n not in taken)
            pty = (_WindowsPty if os.name == "nt" else _PosixPty)(argv, cwd, env, size)
            console = Console(uuid.uuid4().hex, key, title, number, pty, on_exit)
            self._items[console.id] = console
        threading.Thread(target=self._pump, args=(console,), daemon=True).start()
        return console.public()

    def _pump(self, console: Console) -> None:
        while data := console.pty.read():
            with self._lock:
                console.buffer += data
                _trim(console.buffer)
                listeners = list(console.listeners)
            for listener in listeners:
                listener(data)
        code = console.pty.wait()
        with self._lock:
            console.exit_code = code
            console.ended = True
            listeners = list(console.listeners)
            console.listeners.clear()
        for listener in listeners:
            listener(None)
        if console.on_exit:
            console.on_exit()

    def attach(self, console_id: str, listener: Listener) -> tuple[bytes, bool]:
        """Return the scrollback and whether later output will stream to the listener."""
        with self._lock:
            console = self._get(console_id)
            if not console.ended:
                console.listeners.add(listener)
            return bytes(console.buffer), not console.ended

    def detach(self, console_id: str, listener: Listener) -> None:
        with self._lock:
            console = self._items.get(console_id)
            if console:
                console.listeners.discard(listener)

    def write(self, console_id: str, data: bytes) -> None:
        with self._lock:
            console = self._get(console_id)
            if console.ended:
                return
        console.pty.write(data)

    def type_command(self, console_id: str, command: str) -> None:
        """Interrupt a running program, clear the typed line, then enter the command."""
        with self._lock:
            console = self._get(console_id)
            if console.ended:
                raise ConsoleError("This terminal has ended. Open a new one to run your program.")
        if console.pty.busy():
            console.pty.write(b"\x03")
            deadline = time.monotonic() + 1.5
            while console.pty.busy() and time.monotonic() < deadline:
                time.sleep(0.03)
        console.pty.write(b"\x15" + command.encode() + b"\r")

    def resize(self, console_id: str, cols: int, rows: int) -> None:
        with self._lock:
            console = self._get(console_id)
            if not console.ended:
                console.pty.resize(cols, rows)

    def end(self, console_id: str) -> None:
        with self._lock:
            console = self._get(console_id)
            if console.ended:
                return
        console.pty.hang_up()

    def remove(self, console_id: str) -> None:
        self.end(console_id)
        with self._lock:
            self._items.pop(console_id, None)

    def end_matching(self, prefix: str) -> None:
        with self._lock:
            owned = [item.id for item in self._items.values() if item.key.startswith(prefix)]
        for console_id in owned:
            self.remove(console_id)

    def shutdown(self) -> None:
        with self._lock:
            owned = list(self._items)
        for console_id in owned:
            self.end(console_id)

    def _get(self, console_id: str) -> Console:
        console = self._items.get(console_id)
        if console is None:
            raise ConsoleError("That terminal is no longer available. Open a new one.")
        return console


def _clamp(cols: int, rows: int) -> tuple[int, int]:
    return max(2, min(cols, 1000)), max(1, min(rows, 500))


def _set_size(fd: int, cols: int, rows: int) -> None:
    import fcntl
    import struct
    import termios

    cols, rows = _clamp(cols, rows)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
