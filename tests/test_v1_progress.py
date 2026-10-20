import json

import pytest

from pytuitor_web.curriculum import LESSONS
from pytuitor_web.state import Store


def test_version_two_migration_backs_up_original_and_preserves_stage_drafts(tmp_path):
    profile = {
        "version": 2,
        "onboarded": True,
        "track": "beginner",
        "familiar": [],
        "lessons": {
            "first-light": {
                "code": "# build",
                "repair": {"code": "# repair"},
                "stage": "repair",
                "completed": True,
            }
        },
    }
    raw = json.dumps(profile)
    (tmp_path / "profile.json").write_text(raw)
    store = Store(tmp_path)
    assert store.data["version"] == 4
    assert store.data["lessons"] == profile["lessons"]
    store.save()
    assert (tmp_path / "profile-before-v4.json").read_text() == raw
    store.close()


@pytest.mark.parametrize(
    "reviews",
    [
        {"chapter": {"level": 0, "due": "2026-01-01T00:00:00+00:00"}},
        {"chapter": {"level": 0}},
        {"chapter": {"level": -1, "due": "2026-01-01"}},
    ],
)
def test_retired_practice_and_study_data_is_preserved_but_ignored(tmp_path, reviews):
    store = Store(tmp_path)
    retired = {
        "reviews": reviews,
        "feedback_enabled": True,
        "feedback": [{"lesson": LESSONS[0].id, "event": "hint", "stage": "build"}],
    }
    store.data.update(retired)
    store.data["last_lesson"] = "practice-retired-project"
    store.data["lessons"]["practice-retired-project"] = {"code": "# saved practice draft"}
    store.save()
    store.close()

    store = Store(tmp_path)
    assert store.next_lesson() == LESSONS[0]
    store.entry(LESSONS[0])["code"] = "# new course draft"
    store.save()
    saved = json.loads((tmp_path / "profile.json").read_text())
    assert all(saved[key] == value for key, value in retired.items())
    assert saved["lessons"]["practice-retired-project"]["code"] == "# saved practice draft"
    assert saved["lessons"][LESSONS[0].id]["code"] == "# new course draft"
    store.close()


def test_new_profiles_omit_retired_features(tmp_path):
    store = Store(tmp_path)
    assert not {"reviews", "feedback_enabled", "feedback"} & store.data.keys()
    store.close()
