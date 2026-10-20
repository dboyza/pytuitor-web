"""Browser API journeys against a scratch profile, through the same boundary the workbench uses."""

import json
import os
import time

import pytest
from fastapi.testclient import TestClient

from pytuitor_web.curriculum import BY_ID
from pytuitor_web.service import Tutor
from pytuitor_web.web import create_app

ORIGIN = "http://testserver"
HEADERS = {"origin": ORIGIN, "x-pytuitor": "1"}


@pytest.fixture
def client(tmp_path):
    tutor = Tutor(tmp_path / "profile")
    app, token = create_app(tutor, ORIGIN)
    with TestClient(app) as browser:
        assert browser.post("/api/session", json={"token": token}, headers=HEADERS).status_code
        browser.tutor = tutor
        yield browser


def post(client, path, body=None):
    response = client.post(path, json=body or {}, headers=HEADERS)
    assert response.status_code == 200, response.text
    return response.json()


def check(client, lesson, stage):
    response = client.post(f"/api/activities/{lesson}/stages/{stage}/check", headers=HEADERS)
    assert response.status_code == 200, response.text
    events = [json.loads(line) for line in response.text.splitlines()]
    assert events[-1]["type"] == "done", events[-1]
    return events


def save(client, lesson, stage, name, content):
    response = client.put(
        f"/api/activities/{lesson}/stages/{stage}/file",
        json={"name": name, "content": content},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_requests_need_the_session_cookie_and_same_origin(tmp_path):
    tutor = Tutor(tmp_path / "profile")
    app, token = create_app(tutor, ORIGIN)
    with TestClient(app) as browser:
        assert browser.get("/api/state").status_code == 401
        forged = {"origin": "http://evil.example", "x-pytuitor": "1"}
        assert browser.post("/api/session", json={"token": token}, headers=forged).status_code == 403
        assert browser.post("/api/session", json={"token": "wrong"}, headers=HEADERS).status_code
        assert browser.post("/api/session", json={"token": token}, headers=HEADERS).is_success
        assert browser.get("/api/state").is_success
        again = browser.post("/api/session", json={"token": token}, headers=HEADERS)
        assert again.status_code == 401
        assert browser.post("/api/onboard", json={}, headers={"origin": ORIGIN}).status_code == 403


def test_build_then_repair_completes_a_lesson(client):
    lesson = BY_ID["first-light"]
    state = post(client, "/api/onboard")
    assert state["onboarded"] and state["next"]["id"] == "first-light"
    activity = post(client, "/api/activities/first-light/open")
    assert activity["stage"] == "build" and not activity["stages"]["build"]["passed"]
    stage = client.get("/api/activities/first-light/stages/build").json()
    assert stage["files"][0]["name"] == lesson.entrypoint
    assert os.path.isfile(os.path.join(stage["workspace"], lesson.entrypoint))

    events = check(client, "first-light", "build")
    assert not events[-1]["passed"] and any(e["type"] == "case" for e in events)
    assert client.post(
        "/api/activities/first-light/stage", json={"stage": "repair"}, headers=HEADERS
    ).status_code == 400

    reference = post(client, "/api/activities/first-light/stages/build/reference")["files"]
    for name, text in reference.items():
        save(client, "first-light", "build", name, text)
    done = check(client, "first-light", "build")[-1]
    assert done["passed"] and done["flags"]["repair"]["unlocked"]

    repair = post(client, "/api/activities/first-light/stage", {"stage": "repair"})
    assert repair["label"] == "Repair" and repair["guidance"]
    assert not check(client, "first-light", "repair")[-1]["passed"]
    fixed = lesson.stage_contract("repair").reference_files
    for name, text in fixed.items():
        save(client, "first-light", "repair", name, text)
    done = check(client, "first-light", "repair")[-1]
    assert done["passed"] and done["flags"]["completed"]
    assert post(client, "/api/activities/first-light/next")["next"] == "names-and-voices"
    assert client.get("/api/state").json()["statuses"]["first-light"] == "completed"


def test_terminal_edits_sync_into_the_draft_and_extra_files_stay_untracked(client):
    post(client, "/api/onboard")
    post(client, "/api/activities/first-light/open")
    stage = client.get("/api/activities/first-light/stages/build").json()
    folder = stage["workspace"]
    with open(os.path.join(folder, stage["entrypoint"]), "w", encoding="utf-8") as stream:
        stream.write("print('from the shell')\n")
    with open(os.path.join(folder, "notes.txt"), "w", encoding="utf-8") as stream:
        stream.write("scratch\n")
    poll = client.get("/api/activities/first-light/stages/build/poll").json()
    assert poll["changed"] == {stage["entrypoint"]: "print('from the shell')\n"}
    assert poll["untracked"] == [{"name": "notes.txt", "size": 8}]
    tracked = post(
        client, "/api/activities/first-light/stages/build/files", {"name": "notes.txt", "track": 1}
    )
    assert "notes.txt" in {item["name"] for item in tracked["files"]}
    os.remove(os.path.join(folder, stage["entrypoint"]))
    client.get("/api/activities/first-light/stages/build/poll")
    assert os.path.exists(os.path.join(folder, stage["entrypoint"]))


def test_reset_backs_up_and_restores_a_blank_build(client):
    post(client, "/api/onboard")
    post(client, "/api/activities/first-light/open")
    save(client, "first-light", "build", "lesson.py", "print('draft')\n")
    reset = post(client, "/api/activities/first-light/stages/build/reset")
    assert reset["files"][0]["content"] == ""
    assert os.path.isdir(reset["backup"])
    with open(os.path.join(reset["workspace"], "lesson.py"), encoding="utf-8") as stream:
        assert stream.read() == ""


def test_embedded_terminal_runs_the_program_in_the_workspace(client):
    post(client, "/api/onboard")
    post(client, "/api/activities/first-light/open")
    save(client, "first-light", "build", "lesson.py", "print('hello from', 6 * 7)\n")
    console = post(
        client, "/api/activities/first-light/stages/build/consoles", {"cols": 100, "rows": 30}
    )
    again = post(
        client, "/api/activities/first-light/stages/build/consoles", {"cols": 100, "rows": 30}
    )
    assert again["id"] == console["id"]
    post(client, f"/api/consoles/{console['id']}/run", {"lesson": "first-light"})
    with client.websocket_connect(
        f"/api/consoles/{console['id']}/stream", headers={"origin": ORIGIN}
    ) as socket:
        seen = b""
        deadline = time.monotonic() + 15
        while b"hello from 42" not in seen and time.monotonic() < deadline:
            seen += socket.receive_bytes()
        assert b"hello from 42" in seen
    post(client, f"/api/consoles/{console['id']}/close")


def test_milestone_pass_saves_a_checkpoint_that_can_be_exported(client):
    from pytuitor_web.project_catalog import MILESTONES

    first = MILESTONES[0].lesson
    post(client, "/api/onboard")
    post(client, f"/api/activities/{first.id}/open")
    for name, text in first.stage_contract("build").reference_files.items():
        save(client, first.id, "build", name, text)
    assert check(client, first.id, "build")[-1]["passed"]
    game = client.get("/api/game").json()
    assert len(game["checkpoints"]) == 1
    archive = client.get(f"/api/game/checkpoints/{game['checkpoints'][0]['id']}/export")
    assert archive.headers["content-type"] == "application/zip" and archive.content[:2] == b"PK"


def test_review_prediction_and_code_tasks(client):
    from pytuitor_web.content.reviews import REVIEWS

    post(client, "/api/onboard")
    chapter = "first-programs"
    session = post(client, f"/api/reviews/{chapter}/open")
    assert len(session["tasks"]) == len(REVIEWS[chapter])
    for index, task in enumerate(REVIEWS[chapter]):
        path = f"/api/reviews/{chapter}/tasks/{index}"
        answer = {"choice": task.answer} if task.kind == "predict" else {"code": task.reference}
        assert client.put(path, json=answer, headers=HEADERS).is_success
        assert post(client, path + "/check")["passed"]
        result = post(client, path + "/next")
    assert result["finished"]
