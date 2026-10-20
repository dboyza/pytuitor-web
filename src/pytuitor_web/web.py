"""Authenticated loopback API and the built browser workbench."""

from __future__ import annotations

import asyncio
import json
import secrets
import threading
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from pydantic import BaseModel, Field

from pytuitor_web.consoles import ConsoleError
from pytuitor_web.service import LearningError, Tutor, stream_check
from pytuitor_web.state import ProfileError
from pytuitor_web.workspace import WorkspaceError

# WebSocket close codes the browser understands; see frontend/src/terminal/ConsoleView.tsx.
CONSOLE_ENDED = 4001
CONSOLE_LAGGING = 4002
CONSOLE_UNKNOWN = 4004
CONSOLE_BACKLOG = 2048


class SignIn(BaseModel):
    token: str = Field(max_length=200)


class Size(BaseModel):
    cols: int = Field(ge=2, le=1000)
    rows: int = Field(ge=1, le=500)


class OpenConsole(Size):
    fresh: bool = False


class RunProgram(BaseModel):
    lesson: str = Field(max_length=200)


class FileText(BaseModel):
    name: str = Field(max_length=240)
    content: str = Field(max_length=2 * 1024 * 1024)


class FileName(BaseModel):
    name: str = Field(max_length=240)
    track: bool = False


class StageChoice(BaseModel):
    stage: str


class Choice(BaseModel):
    choice: int


class Note(BaseModel):
    note: str = Field(max_length=2000)


class Concepts(BaseModel):
    concepts: list[str] = Field(max_length=1000)


class Theme(BaseModel):
    theme: str


class Base(BaseModel):
    checkpoint: str | None = Field(default=None, max_length=64)


class ReviewAnswer(BaseModel):
    code: str | None = Field(default=None, max_length=100000)
    choice: int | None = None


def _download(name: str, data: bytes) -> Response:
    return Response(
        data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


def create_app(tutor: Tutor, origin: str) -> tuple[FastAPI, str]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            tutor.close()

    app = FastAPI(
        title="Pytuitor", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan
    )
    nonce = secrets.token_urlsafe(32)
    cookie = secrets.token_urlsafe(32)
    cookie_name = "pytuitor_" + secrets.token_hex(5)
    expires = time.monotonic() + 600
    consumed = False
    sign_in_lock = threading.Lock()
    socket_origin = "ws" + origin.removeprefix("http")
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"]
    )

    @app.middleware("http")
    async def boundary(request: Request, call_next: Any) -> Response:
        if request.url.path.startswith("/api/"):
            supplied = request.headers.get("origin")
            if supplied is not None and supplied != origin:
                return JSONResponse(
                    {"detail": "This request did not come from the workbench."}, status_code=403
                )
            if request.method not in {"GET", "HEAD"} and (
                supplied != origin or request.headers.get("x-pytuitor") != "1"
            ):
                return JSONResponse(
                    {"detail": "A same-origin workbench request is required."}, status_code=403
                )
            if request.url.path != "/api/session":
                received = request.cookies.get(cookie_name, "")
                if not secrets.compare_digest(received, cookie):
                    return JSONResponse(
                        {"detail": "Open Pytuitor from its launcher to connect this browser."},
                        status_code=401,
                    )
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            f"img-src 'self' data:; font-src 'self' data:; connect-src 'self' {socket_origin}; "
            "frame-ancestors 'none'; base-uri 'none'"
        )
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(LearningError)
    @app.exception_handler(WorkspaceError)
    @app.exception_handler(ConsoleError)
    @app.exception_handler(ProfileError)
    async def refused(request: Request, error: Exception) -> JSONResponse:
        return JSONResponse({"detail": str(error)}, status_code=400)

    @app.post("/api/session")
    def sign_in(body: SignIn, response: Response) -> dict[str, bool]:
        nonlocal consumed
        with sign_in_lock:
            if (
                consumed
                or time.monotonic() > expires
                or not secrets.compare_digest(body.token, nonce)
            ):
                raise HTTPException(
                    401, "This one-time sign-in expired or was already used. Relaunch Pytuitor."
                )
            consumed = True
        response.set_cookie(cookie_name, cookie, httponly=True, samesite="strict", path="/")
        return {"connected": True}

    # Profile ---------------------------------------------------------------------------------

    @app.get("/api/catalog")
    def catalog() -> dict[str, Any]:
        return tutor.catalog()

    @app.get("/api/state")
    def state() -> dict[str, Any]:
        return tutor.state()

    @app.post("/api/onboard")
    def onboard() -> dict[str, Any]:
        tutor.onboard()
        return tutor.state()

    @app.post("/api/familiar")
    def familiar(body: Concepts) -> dict[str, Any]:
        tutor.set_familiar(body.concepts)
        return tutor.state()

    @app.post("/api/settings")
    def settings(body: Theme) -> dict[str, Any]:
        tutor.set_theme(body.theme)
        return tutor.state()

    @app.post("/api/restart")
    def restart() -> dict[str, Any]:
        backup = tutor.restart()
        return {"backup": backup, "state": tutor.state()}

    # Lessons ---------------------------------------------------------------------------------

    @app.post("/api/activities/{lesson_id}/open")
    def open_activity(lesson_id: str) -> dict[str, Any]:
        return tutor.open(lesson_id)

    @app.get("/api/activities/{lesson_id}")
    def activity(lesson_id: str) -> dict[str, Any]:
        return tutor.activity(lesson_id)

    @app.post("/api/activities/{lesson_id}/prediction")
    def prediction(lesson_id: str, body: Choice) -> dict[str, Any]:
        return tutor.predict(lesson_id, body.choice)

    @app.post("/api/activities/{lesson_id}/note")
    def note(lesson_id: str, body: Note) -> dict[str, bool]:
        tutor.note(lesson_id, body.note)
        return {"saved": True}

    @app.post("/api/activities/{lesson_id}/next")
    def following(lesson_id: str) -> dict[str, str | None]:
        return {"next": tutor.following(lesson_id)}

    @app.post("/api/activities/{lesson_id}/stage")
    def switch(lesson_id: str, body: StageChoice) -> dict[str, Any]:
        return tutor.switch(lesson_id, body.stage)

    stage_path = "/api/activities/{lesson_id}/stages/{stage}"

    @app.get(stage_path)
    def stage(lesson_id: str, stage: str) -> dict[str, Any]:
        return tutor.stage(lesson_id, stage)

    @app.get(stage_path + "/poll")
    def poll(lesson_id: str, stage: str) -> dict[str, Any]:
        return tutor.poll(lesson_id, stage)

    @app.get(stage_path + "/file")
    def read_file(lesson_id: str, stage: str, name: str) -> dict[str, str]:
        return tutor.read_file(lesson_id, stage, name)

    @app.put(stage_path + "/file")
    def save_file(lesson_id: str, stage: str, body: FileText) -> dict[str, Any]:
        return tutor.save_file(lesson_id, stage, body.name, body.content)

    @app.post(stage_path + "/files")
    def add_file(lesson_id: str, stage: str, body: FileName) -> dict[str, Any]:
        return tutor.add_file(lesson_id, stage, body.name, body.track)

    @app.post(stage_path + "/files/remove")
    def remove_file(lesson_id: str, stage: str, body: FileName) -> dict[str, Any]:
        return tutor.remove_file(lesson_id, stage, body.name)

    @app.get(stage_path + "/preview")
    def preview(lesson_id: str, stage: str, name: str) -> dict[str, str]:
        return {"content": tutor.read_untracked(lesson_id, stage, name)}

    @app.post(stage_path + "/view")
    def view(lesson_id: str, stage: str, body: FileName) -> dict[str, bool]:
        tutor.save_view(lesson_id, stage, body.name)
        return {"saved": True}

    @app.post(stage_path + "/hint")
    def hint(lesson_id: str, stage: str) -> dict[str, Any]:
        return tutor.hint(lesson_id, stage)

    @app.post(stage_path + "/reference")
    def reference(lesson_id: str, stage: str) -> dict[str, Any]:
        return tutor.reference(lesson_id, stage)

    @app.post(stage_path + "/reset")
    def reset(lesson_id: str, stage: str) -> dict[str, Any]:
        return tutor.reset(lesson_id, stage)

    @app.get(stage_path + "/export")
    def export(lesson_id: str, stage: str) -> Response:
        return _download(*tutor.export_zip(lesson_id, stage))

    @app.post(stage_path + "/check")
    async def check(lesson_id: str, stage: str, request: Request) -> StreamingResponse:
        tutor.lesson(lesson_id)
        queue, task = await stream_check(tutor, lesson_id, stage)

        async def events() -> AsyncIterator[bytes]:
            try:
                while (event := await queue.get()) is not None:
                    yield (json.dumps(event) + "\n").encode()
            finally:
                # A closed browser tab stops the check's process tree.
                task.cancel()
                with suppress(asyncio.CancelledError, Exception):
                    await task

        return StreamingResponse(events(), media_type="application/x-ndjson")

    # Terminals -------------------------------------------------------------------------------

    @app.post(stage_path + "/consoles")
    def open_console(lesson_id: str, stage: str, body: OpenConsole) -> dict[str, Any]:
        return tutor.open_console(lesson_id, stage, body.cols, body.rows, body.fresh)

    @app.get("/api/consoles")
    def consoles() -> list[dict[str, Any]]:
        return tutor.consoles.public()

    @app.post("/api/consoles/{console_id}/run")
    def run(console_id: str, body: RunProgram) -> dict[str, bool]:
        tutor.run(console_id, body.lesson)
        return {"started": True}

    @app.post("/api/consoles/{console_id}/close")
    def close_console(console_id: str) -> dict[str, bool]:
        tutor.consoles.remove(console_id)
        return {"closed": True}

    @app.websocket("/api/consoles/{console_id}/stream")
    async def console_stream(socket: WebSocket, console_id: str) -> None:
        # Browsers always send Origin on WebSocket handshakes; the HTTP middleware does not run.
        if socket.headers.get("origin") != origin or not secrets.compare_digest(
            socket.cookies.get(cookie_name, ""), cookie
        ):
            await socket.close(code=1008)
            return
        loop = asyncio.get_running_loop()
        output: asyncio.Queue[bytes | None] = asyncio.Queue(CONSOLE_BACKLOG)
        lagging = asyncio.Event()

        def deliver(data: bytes | None) -> None:
            try:
                output.put_nowait(data)
            except asyncio.QueueFull:
                lagging.set()

        def listener(data: bytes | None) -> None:
            loop.call_soon_threadsafe(deliver, data)

        try:
            history, live = tutor.consoles.attach(console_id, listener)
        except ConsoleError:
            await socket.close(code=CONSOLE_UNKNOWN)
            return
        await socket.accept()

        async def send() -> None:
            await socket.send_bytes(history)
            while live and not lagging.is_set():
                data = await output.get()
                if data is None:
                    break
                await socket.send_bytes(data)
            # A browser that fell behind reconnects and replays the scrollback instead.
            await socket.close(code=CONSOLE_LAGGING if lagging.is_set() else CONSOLE_ENDED)

        async def receive() -> None:
            while True:
                message = await socket.receive()
                if message["type"] == "websocket.disconnect":
                    return
                if message.get("bytes"):
                    await asyncio.to_thread(tutor.consoles.write, console_id, message["bytes"])
                elif message.get("text"):
                    size = Size.model_validate_json(message["text"])
                    tutor.consoles.resize(console_id, size.cols, size.rows)

        async def guarded(work: Any) -> None:
            with suppress(WebSocketDisconnect, ConsoleError, ValueError, RuntimeError):
                await work

        tasks = [asyncio.create_task(guarded(send())), asyncio.create_task(guarded(receive()))]
        try:
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        finally:
            for task in tasks:
                task.cancel()
            tutor.consoles.detach(console_id, listener)

    # Lantern Reach ---------------------------------------------------------------------------

    @app.get("/api/game")
    def game() -> dict[str, Any]:
        return tutor.game()

    @app.post("/api/game/{milestone_id}/base")
    def base(milestone_id: str, body: Base) -> dict[str, Any]:
        return {**tutor.supplied_base(milestone_id, body.checkpoint), "game": tutor.game()}

    @app.get("/api/game/checkpoints/{identifier}/export")
    def export_checkpoint(identifier: str) -> Response:
        return _download(*tutor.export_checkpoint(identifier))

    @app.post("/api/game/checkpoints/{identifier}/play")
    def play(identifier: str, body: Size) -> dict[str, Any]:
        return tutor.play_checkpoint(identifier, body.cols, body.rows)

    # Optional review -------------------------------------------------------------------------

    @app.get("/api/reviews")
    def reviews() -> dict[str, Any]:
        return tutor.reviews()

    @app.post("/api/reviews/pause")
    def pause() -> dict[str, Any]:
        tutor.pause_reviews()
        return tutor.reviews()

    @app.post("/api/reviews/{chapter}/defer")
    def defer(chapter: str) -> dict[str, Any]:
        tutor.defer_review(chapter)
        return tutor.reviews()

    @app.post("/api/reviews/{chapter}/open")
    def open_review(chapter: str) -> dict[str, Any]:
        return tutor.open_review(chapter)

    task_path = "/api/reviews/{chapter}/tasks/{index}"

    @app.get(task_path)
    def review_task(chapter: str, index: int) -> dict[str, Any]:
        return tutor.review_task(chapter, index)

    @app.put(task_path)
    def save_review(chapter: str, index: int, body: ReviewAnswer) -> dict[str, bool]:
        tutor.save_review(chapter, index, body.code, body.choice)
        return {"saved": True}

    @app.post(task_path + "/check")
    async def check_review(chapter: str, index: int) -> dict[str, Any]:
        return await tutor.check_review(chapter, index)

    @app.post(task_path + "/hint")
    def review_hint(chapter: str, index: int) -> dict[str, str]:
        return {"text": tutor.review_aid(chapter, index, "hint")}

    @app.post(task_path + "/reference")
    def review_reference(chapter: str, index: int) -> dict[str, str]:
        return {"text": tutor.review_aid(chapter, index, "reference")}

    @app.post(task_path + "/next")
    def review_next(chapter: str, index: int) -> dict[str, Any]:
        return tutor.review_next(chapter, index)

    # Browser assets --------------------------------------------------------------------------

    assets = Path(__file__).parent / "static"

    @app.get("/{path:path}")
    def frontend(path: str) -> FileResponse:
        if path.startswith("api/"):
            raise HTTPException(404, "Unknown API endpoint.")
        target = (assets / path).resolve()
        if not target.is_relative_to(assets.resolve()):
            raise HTTPException(404)
        if target.is_file():
            cache = "public, max-age=31536000, immutable" if path.startswith("assets/") else None
            return FileResponse(target, headers={"Cache-Control": cache} if cache else None)
        index = assets / "index.html"
        if not index.exists():
            raise HTTPException(
                503, "Build the browser assets with npm --prefix frontend run build first."
            )
        return FileResponse(index, headers={"Cache-Control": "no-cache"})

    return app, nonce
