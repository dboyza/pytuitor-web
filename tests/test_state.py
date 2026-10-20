import json

import pytest

from pytuitor_web.curriculum import LESSONS
from pytuitor_web.state import ProfileError, Store


def test_familiar_is_distinct_and_revisitable(tmp_path):
    store = Store(tmp_path)
    lesson = LESSONS[0]
    store.set_familiar(list(lesson.concepts))
    assert store.status(lesson) == "familiar"
    assert store.next_lesson().id != lesson.id
    store.entry(lesson)["code"] = "work in progress"
    store.save()
    store.close()
    restored = Store(tmp_path)
    assert restored.entry(lesson)["code"] == "work in progress"
    restored.set_familiar([])
    assert restored.status(lesson) == "in progress"
    assert restored.next_lesson().id == lesson.id
    restored.close()


def test_second_writer_is_rejected(tmp_path):
    store = Store(tmp_path)
    with pytest.raises(ProfileError, match="already open"):
        Store(tmp_path)
    store.close()
    Store(tmp_path).close()


def test_legacy_profile_keeps_drafts_and_completion(tmp_path):
    original = {
        "version": 1,
        "onboarded": True,
        "track": "experienced",
        "background": "cs",
        "goal": "depth",
        "diagnostic": {"values": True},
        "familiar": ["Conditions"],
        "lessons": {"first-light": {"code": 'print("Mine")', "completed": True}},
    }
    (tmp_path / "profile.json").write_text(json.dumps(original))
    store = Store(tmp_path)
    assert store.data["version"] == 4
    assert store.data["lessons"] == original["lessons"]
    assert store.data["familiar"] == original["familiar"]
    assert "diagnostic" not in store.data
    store.save()
    store.close()
    restored = Store(tmp_path)
    assert restored.status(LESSONS[0]) == "completed"
    restored.close()


def test_failed_reset_preserves_profile(tmp_path, monkeypatch):
    store = Store(tmp_path)
    store.entry(LESSONS[0])["code"] = "precious draft"
    store.save()
    before = store.path.read_text()

    def cannot_save():
        raise OSError("Disk is full")

    monkeypatch.setattr(store, "save", cannot_save)
    with pytest.raises(OSError, match="Disk is full"):
        store.reset()
    assert store.entry(LESSONS[0])["code"] == "precious draft"
    assert store.path.read_text() == before
    store.close()


@pytest.mark.parametrize(
    "contents",
    ["broken json", json.dumps({"version": 999}), json.dumps({"version": 1, "track": []})],
)
def test_invalid_profile_is_preserved(tmp_path, contents):
    path = tmp_path / "profile.json"
    path.write_text(contents)
    with pytest.raises(ProfileError, match="left untouched"):
        Store(tmp_path)
    assert path.read_text() == contents
