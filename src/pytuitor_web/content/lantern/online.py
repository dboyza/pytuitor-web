"""An optional online milestone; checks use a local practice station, never the internet."""

from pytuitor_web.content.lantern.authoring import milestone, scenario
from pytuitor_web.content.lantern.core import ARCHIVE_CHECKS, ARCHIVE_FILES, M11, extend
from pytuitor_web.models import code

RANGER_SOURCE = """
    def ranger_report(state):
        return {
            "beacon": bool(state.get("beacon", False)),
            "residents": sorted(state.get("residents", [])),
            "buildings": sorted(state.get("buildings", [])),
            "turn": state["turn"],
        }


    def send_report(base_url, state):
        import requests

        response = requests.post(f"{base_url}/reports", json=ranger_report(state), timeout=5)
        response.raise_for_status()
        return response.json()["id"]


    def report_command(state, text):
        import requests

        words = text.split()
        if len(words) != 2:
            return "Usage: report URL"
        try:
            number = send_report(words[1].rstrip("/"), state)
        except requests.RequestException:
            return "The ranger station did not accept the report. Try again later."
        return f"Report filed: #{number}"
"""

RANGER_TESTS = """
    import pytest
    import requests

    from engine import new_game, ranger_report, send_report


    class FakeResponse:
        def __init__(self, status, data):
            self.status_code = status
            self.data = data

        def raise_for_status(self):
            if self.status_code >= 400:
                raise requests.HTTPError(f"status {self.status_code}")

        def json(self):
            return self.data


    def test_new_game_report():
        report = ranger_report(new_game())
        assert report["beacon"] is False
        assert report["residents"] == []


    def test_send_report_returns_id(monkeypatch):
        sent = []

        def fake_post(url, json, timeout):
            sent.append((url, json, timeout))
            return FakeResponse(201, {"id": 4})

        monkeypatch.setattr(requests, "post", fake_post)
        assert send_report("http://station", new_game()) == 4
        assert sent[0][0] == "http://station/reports"


    def test_send_report_rejects_server_error(monkeypatch):
        monkeypatch.setattr(requests, "post", lambda url, json, timeout: FakeResponse(500, {}))
        with pytest.raises(requests.HTTPError):
            send_report("http://station", new_game())
"""

RANGER_FILES = extend(
    {
        **ARCHIVE_FILES,
        "test_ranger.py": code(RANGER_TESTS),
        "requirements.txt": "requests>=2.31\npytest>=8\n",
    },
    RANGER_SOURCE
    + """

    _before_ranger = step


    def step(state, command):
        cleaned = command.strip()
        if cleaned.lower().split()[:1] == ["report"]:
            return report_command(state, cleaned)
        if cleaned.lower() == "help":
            return _before_ranger(state, command) + ", report URL"
        return _before_ranger(state, command)
    """,
)

_STATION = """
    import requests

    timeouts = []
    original_request = requests.Session.request


    def recording(self, method, url, **options):
        timeouts.append(options.get("timeout"))
        return original_request(self, method, url, **options)


    def respond(method, path, query, data):
        if method == "POST" and path == "/reports":
            return (503, {"error": "busy"}) if data.get("turn") == 99 else (201, {"id": 12})
        return 404, {"error": "no such endpoint"}


    requests.Session.request = recording
"""

RANGER_CHECKS = ARCHIVE_CHECKS + (
    scenario(
        "A report reaches the practice station",
        code(_STATION)
        + code(
            """
            try:
                game = new_game()
                game["residents"] = ["Tess", "Oren"]
                with __practice_server__(respond) as (base, seen):
                    reply = step(game, "report " + base)
                    direct = send_report(base, game)
                    body = seen[0]["body"]
            finally:
                requests.Session.request = original_request
            result = (
                __expect__("reply", reply, "Report filed: #12", "==")
                and __expect__("direct", direct, 12, "==")
                and __expect__("body", body, ranger_report(game), "==")
                and __expect__("residents", body["residents"], ["Oren", "Tess"], "==")
                and __expect__("beacon", body["beacon"], False, "==")
                and __expect__("timeouts set", all(t is not None for t in timeouts), True, "==")
            )
            """
        ),
        "POST ranger_report(state) as JSON to BASE/reports with a timeout and return its id.",
    ),
    scenario(
        "Station problems never crash the game",
        code(_STATION)
        + code(
            """
            try:
                game = new_game()
                game["turn"] = 99
                with __practice_server__(respond) as (base, seen):
                    busy = step(game, "report " + base)
                    raised = False
                    try:
                        send_report(base, game)
                    except requests.HTTPError:
                        raised = True
                closed = step(new_game(), "report " + base)
            finally:
                requests.Session.request = original_request
            failure = "The ranger station did not accept the report. Try again later."
            result = (
                __expect__("busy", busy, failure, "==")
                and __expect__("send_report raises HTTPError", raised, True, "==")
                and __expect__("unreachable", closed, failure, "==")
                and __expect__("usage", step(new_game(), "report"), "Usage: report URL", "==")
                and "report URL" in step(new_game(), "help")
            )
            """
        ),
        "Raise HTTPError in send_report; the report command catches RequestException.",
    ),
    scenario(
        "Learner tests prove the report without the internet",
        """
            import engine

            code, collected, report = __pytest_run__("test_ranger.py")
            print(report)


            def ignoring_errors(base_url, state):
                import requests

                response = requests.post(
                    f"{base_url}/reports", json=engine.ranger_report(state), timeout=5
                )
                return response.json().get("id")


            original = engine.send_report
            engine.send_report = ignoring_errors
            try:
                mutant, _, _ = __pytest_run__("test_ranger.py")
            finally:
                engine.send_report = original
            result = (
                __expect__("pytest exit code", code, 0, "==")
                and __expect__("tests collected", collected, 3, ">=")
                and __expect__("tests fail when errors are ignored", mutant != 0, True, "==")
            )
        """,
        "Fake requests.post with monkeypatch; one test must expect HTTPError for a 500 reply.",
    ),
    scenario(
        "Requirements name both packages with versions",
        """
            from pathlib import Path

            entries = {}
            for line in Path("requirements.txt").read_text(encoding="utf-8").splitlines():
                text = line.split("#", 1)[0].strip()
                if not text:
                    continue
                cut = min([text.find(c) for c in "=<>!~" if c in text] or [len(text)])
                entries[text[:cut].strip().lower()] = text[cut:].strip()
            result = __expect__(
                "packages with a version specifier",
                sorted(name for name, specifier in entries.items() if specifier),
                ["pytest", "requests"],
                "==",
            )
        """,
        "List requests and pytest in requirements.txt, each with a version specifier.",
    ),
)

_STATUS_SERVER = """
    import requests

    timeouts = []
    original_request = requests.Session.request


    def recording(self, method, url, **options):
        timeouts.append(options.get("timeout"))
        return original_request(self, method, url, **options)


    def respond(method, path, query, data):
        return {
            "/online/status": (200, {"ok": True}),
            "/busy/status": (503, {"error": "busy"}),
            "/broken/status": (500, {"error": "fault"}),
        }.get(path, (404, {"error": "missing"}))


    requests.Session.request = recording
"""

M22 = milestone(
    chapter="packages-and-web",
    title="Report to the ranger station",
    capability="ranger",
    requires=M11.provides,
    base=ARCHIVE_FILES,
    reference=RANGER_FILES,
    checks=RANGER_CHECKS,
    story=(
        "A ranger station in the next valley tracks expeditions. With the beacon lit, "
        "Lantern Reach can finally report in."
    ),
    teaching="## Keep the game playable offline\n\n"
    "This milestone adds a network feature to a game that must keep working without one. "
    "Import requests inside the functions that need it, so the rest of the game starts even "
    "where requests is not installed. Set a timeout on every request, and turn every network "
    "failure into a calm message instead of a crash.\n\n"
    "Checks start a practice ranger station on your own computer at 127.0.0.1, so no internet "
    "is needed here. Your tests replace requests.post with a fake using pytest's monkeypatch "
    "fixture, so they never touch the network either. Anyone running your exported game "
    "installs its packages with `python -m pip install -r requirements.txt`, which needs "
    "internet.",
    requirements=(
        "Keep all previous game behavior.\n"
        "Add `ranger_report(state)` to your engine, beside the rest of the game's rules.\n"
        "It returns a dictionary with `beacon` (a boolean, `False` when the state has no beacon "
        "key), `residents` and `buildings` (sorted lists, empty when missing), and `turn`.\n"
        "Add `send_report(base_url, state)`, which sends `ranger_report(state)` as JSON in a "
        "POST request to `BASE_URL/reports` with a timeout of at most 10 seconds.\n"
        "It raises `requests.HTTPError` for an error status and otherwise returns the `id` "
        "value from the JSON reply.\n"
        "Import requests inside the functions that use it, so the game still starts without "
        "it.\n"
        "Add a `report URL` command that returns `Report filed: #ID` on success and `Usage: "
        "report URL` when the URL is missing.\n"
        "For any `requests.RequestException`, including an unreachable station, the command "
        "returns `The ranger station did not accept the report. Try again later.`\n"
        "List `report URL` in `help`.\n"
        "Add `test_ranger.py`, importing from `engine`, with at least three pytest tests that "
        "use no network.\n"
        "The tests check `ranger_report` for a new game, check that `send_report` returns the "
        "id using a fake `requests.post` installed with `monkeypatch`, and check that "
        "`send_report` raises `requests.HTTPError` when the fake reply has status 500.\n"
        "Add `requirements.txt` listing `requests` and `pytest`, each with a version specifier "
        "such as `>=2.31`."
    ),
    repair_instructions=(
        "Repair `check_station(base_url)`, which sends a GET request to `BASE_URL/status` with "
        "a timeout of at most 10 seconds.\n"
        "It returns `online` for a success status and `busy` for status 503.\n"
        "For any other error status it raises `requests.HTTPError`.\n"
        "It returns `offline` only when no response arrives, meaning `requests.ConnectionError` "
        "or `requests.Timeout`.\n"
        "Do not hide other errors: catching every exception would report a broken station as "
        "merely offline."
    ),
    repair_reference="""
        import requests


        def check_station(base_url):
            try:
                response = requests.get(f"{base_url}/status", timeout=5)
            except (requests.ConnectionError, requests.Timeout):
                return "offline"
            if response.status_code == 503:
                return "busy"
            response.raise_for_status()
            return "online"
    """,
    repair_broken="""
        import requests


        def check_station(base_url):
            try:
                response = requests.get(f"{base_url}/status")
                response.raise_for_status()
                return "online"
            except Exception:
                return "offline"
    """,
    repair_checks=(
        scenario(
            "Online, busy, broken, and unreachable stations",
            code(_STATUS_SERVER)
            + code(
                """
                try:
                    with __practice_server__(respond) as (base, seen):
                        online = check_station(base + "/online")
                        busy = check_station(base + "/busy")
                        try:
                            check_station(base + "/broken")
                            broken = "no error"
                        except requests.HTTPError:
                            broken = "HTTPError"
                    offline = check_station(base + "/online")
                finally:
                    requests.Session.request = original_request
                result = (
                    __expect__("online", online, "online", "==")
                    and __expect__("busy", busy, "busy", "==")
                    and __expect__("broken", broken, "HTTPError", "==")
                    and __expect__("offline", offline, "offline", "==")
                    and __expect__("timeouts set", None in timeouts, False, "==")
                )
                """
            ),
            "Catch only ConnectionError and Timeout, check 503 yourself, then raise_for_status().",
        ),
    ),
    hints=(
        "Write ranger_report first; it only reads the state you already keep.",
        "Use requests.post(url, json=..., timeout=5), then raise_for_status() and read the id.",
        "In the report command, catch requests.RequestException around send_report.",
        "In test_ranger.py, monkeypatch.setattr(requests, 'post', fake) replaces the network.",
    ),
    repair_hints=(
        "Ask the practice station for /busy and /broken and compare the answers.",
        "except Exception hides every mistake as offline; name only the network errors.",
    ),
    minutes=40,
)

ONLINE = (M22,)
