"""Authored curriculum, independent of the terminal interface."""

from dataclasses import dataclass
from importlib.resources import files
from textwrap import dedent
from typing import Literal


@dataclass(frozen=True)
class Check:
    label: str
    expression: str
    expected: object
    nudge: str
    stdin: str | None = None
    expected_output: str | None = None
    description: str = ""


@dataclass(frozen=True)
class StageContract:
    """The learner-facing and executable contract for one exercise stage."""

    instructions: str = ""
    checks: tuple[Check, ...] = ()
    hints: tuple[str, ...] = ()
    stdin: str = ""
    files: tuple[str, ...] = ("lesson.py",)
    starter_files: dict[str, str] | None = None
    reference_files: dict[str, str] | None = None


@dataclass(frozen=True)
class Lesson:
    id: str
    track: str
    title: str
    subtitle: str
    minutes: int
    concepts: tuple[str, ...]
    body: str
    repair: str
    checks: tuple[Check, ...]
    hints: tuple[str, ...]
    prediction: str
    choices: tuple[str, ...]
    answer: int
    explanation: str
    solution: str
    project: bool = False
    revision: int = 3

    chapter_id: str = ""
    prerequisites: tuple[str, ...] = ()
    entrypoint: str = "lesson.py"
    files: tuple[str, ...] = ("lesson.py",)
    solution_files: dict[str, str] | None = None
    repair_files: dict[str, str] | None = None
    stdin: str = ""
    build_stage: StageContract | None = None
    repair_stage: StageContract | None = None
    project_id: str = ""

    @property
    def build_label(self) -> str:
        return "Extend" if self.project_id else "Build"

    @property
    def starter(self) -> str:
        return ""

    def stage_contract(self, stage: Literal["build", "repair"]) -> StageContract:
        """Return a stage contract, preserving the original fields by default."""
        if stage == "build" and self.build_stage is not None:
            return self.build_stage
        if stage == "repair" and self.repair_stage is not None:
            return self.repair_stage
        if stage not in ("build", "repair"):
            raise ValueError(f"Unknown exercise stage: {stage}")
        if stage == "build":
            return StageContract(
                checks=self.checks,
                hints=self.hints,
                stdin=self.stdin,
                files=self.files,
                starter_files={name: "" for name in self.files},
                reference_files=self.solution_files or {self.entrypoint: self.solution},
            )
        return StageContract(
            checks=self.checks,
            hints=self.hints,
            stdin=self.stdin,
            files=self.files,
            starter_files=self.repair_files or {self.entrypoint: self.repair},
            reference_files=self.solution_files or {self.entrypoint: self.solution},
        )


def lesson_text(lesson_id: str) -> str:
    return files("pytuitor_web").joinpath("lessons", f"{lesson_id}.md").read_text(encoding="utf-8")


def code(source: str) -> str:
    return dedent(source).strip() + "\n"


@dataclass(frozen=True)
class Section:
    id: str
    title: str
    description: str
    optional: bool = False


@dataclass(frozen=True)
class Chapter:
    id: str
    track: str
    title: str
    outcome: str
    section_id: str = ""
    prerequisites: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProjectMilestone:
    """A versioned extension with an independently authored repair contract."""

    lesson: Lesson
    requires: tuple[str, ...]
    provides: tuple[str, ...]
    base_files: dict[str, str]


@dataclass(frozen=True)
class ProjectDefinition:
    id: str
    title: str
    description: str
    milestones: tuple[ProjectMilestone, ...]
