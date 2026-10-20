"""Short authored review tasks, independent of required course stages."""

from dataclasses import dataclass, replace
from typing import Literal

from pytuitor_web.models import Check, Lesson, StageContract, code


@dataclass(frozen=True)
class ReviewTask:
    title: str
    kind: Literal["predict", "debug", "code"]
    prompt: str
    reference: str = ""
    starter: str = ""
    checks: tuple[Check, ...] = ()
    hint: str = ""
    choices: tuple[str, ...] = ()
    answer: int = 0
    explanation: str = ""
    id: str = ""

    def lesson(self):
        contract = StageContract(
            instructions=self.prompt,
            checks=self.checks,
            hints=(self.hint,),
            starter_files={"lesson.py": self.starter},
            reference_files={"lesson.py": self.reference},
        )
        return Lesson(
            id=self.id,
            track="review",
            title=self.title,
            subtitle="Optional review",
            minutes=3,
            concepts=(),
            body=self.prompt,
            repair="",
            checks=self.checks,
            hints=(self.hint,),
            prediction="",
            choices=(),
            answer=0,
            explanation="",
            solution=self.reference,
            revision=1,
            build_stage=contract,
        )


def prediction(title, snippet, choices, answer, explanation):
    return ReviewTask(
        title,
        "predict",
        "Predict the printed output before running this code.\n\n"
        + "```python\n"
        + code(snippet)
        + "```",
        choices=tuple(choices),
        answer=answer,
        explanation=explanation,
    )


def task(title, prompt, reference, checks, *, broken="", hint):
    return ReviewTask(
        title,
        "debug" if broken else "code",
        prompt,
        reference=code(reference),
        starter=code(broken) if broken else "",
        checks=tuple(
            Check(label, expression, expected, hint, description=label)
            for label, expression, expected in checks
        ),
        hint=hint,
    )


def chapter(identifier, *tasks):
    assert len(tasks) == 3
    return tuple(
        replace(item, id=f"review-{identifier}-{index}") for index, item in enumerate(tasks, 1)
    )
