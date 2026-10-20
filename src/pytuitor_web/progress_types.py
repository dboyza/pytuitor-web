"""Typed profile and worker-message boundaries; JSON is validated when read."""

from typing import Literal, NotRequired, TypedDict

StageName = Literal["build", "repair"]


class DraftState(TypedDict, total=False):
    code: str
    files: dict[str, str]
    revision: int
    checked_code: str
    checked_files: dict[str, str]
    checked_revision: int
    hints: int
    solution_seen: bool


class LessonProgress(DraftState, total=False):
    stage: StageName
    repair: DraftState
    completed: bool
    completed_revision: int
    prediction: bool
    input: str


class CheckEvent(TypedDict):
    number: int
    label: str
    input: str
    operation: str
    expected: str
    expected_output: str | None
    nudge: str
    status: Literal["running", "finished"]
    passed: NotRequired[bool]
    actual: NotRequired[str]
    output: NotRequired[str]
    observations: NotRequired[list[dict]]


def check_event(value: object) -> CheckEvent:
    """Reject malformed child-process messages before they reach UI state."""
    from typing import cast

    if not isinstance(value, dict):
        raise ValueError("Invalid check message")
    if type(value.get("number")) is not int or value["number"] < 1:
        raise ValueError("Invalid check number")
    for key in ("label", "input", "operation", "expected", "nudge"):
        if not isinstance(value.get(key), str):
            raise ValueError("Invalid check text")
    if value.get("expected_output") is not None and not isinstance(value["expected_output"], str):
        raise ValueError("Invalid expected output")
    if value.get("status") not in ("running", "finished"):
        raise ValueError("Invalid check status")
    if value["status"] == "finished":
        if type(value.get("passed")) is not bool:
            raise ValueError("Invalid check outcome")
        if not all(isinstance(value.get(key), str) for key in ("actual", "output")):
            raise ValueError("Invalid check result text")
    observations = value.get("observations", [])
    if not isinstance(observations, list) or len(observations) > 16:
        raise ValueError("Invalid check observations")
    for item in observations:
        if not isinstance(item, dict) or type(item.get("passed")) is not bool:
            raise ValueError("Invalid check observation")
        if not all(
            isinstance(item.get(key), str) for key in ("label", "actual", "expected", "comparison")
        ):
            raise ValueError("Invalid check observation text")
        if any(len(item[key]) > 1000 for key in ("label", "actual", "expected")):
            raise ValueError("Oversized check observation")
        if item["comparison"] not in ("==", "!=", "<", "<=", ">", ">="):
            raise ValueError("Invalid check comparison")
    return cast(CheckEvent, value)
