"""Reject malformed persisted and subprocess state without losing recoverable drafts."""

import json

import pytest

from pytuitor_web.progress_types import check_event
from pytuitor_web.state import ProfileError, Store, fresh_profile


@pytest.mark.parametrize("revision", [True, 0, -1, "5", None])
def test_invalid_revision_preserves_original_profile(tmp_path, revision):
    profile = fresh_profile()
    profile["lessons"]["first-light"] = {"code": "recover me", "revision": revision}
    text = json.dumps(profile)
    path = tmp_path / "profile.json"
    path.write_text(text)
    with pytest.raises(ProfileError, match="left untouched"):
        Store(tmp_path)
    assert path.read_text() == text


@pytest.mark.parametrize(
    "changes",
    [{"number": True}, {"number": 0}, {"status": "unknown"}, {"passed": "yes"}, {"actual": None}],
)
def test_invalid_worker_message_is_rejected(changes):
    event = {
        "number": 1,
        "label": "example",
        "input": "",
        "operation": "function(1)",
        "expected": "2",
        "expected_output": None,
        "nudge": "Check the operation.",
        "status": "finished",
        "passed": True,
        "actual": "2",
        "output": "",
    }
    with pytest.raises(ValueError):
        check_event({**event, **changes})
