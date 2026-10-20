"""Attach explicit experienced stages while preserving legacy fields."""

from dataclasses import replace

from pytuitor_web.content import (
    experienced_composition,
    experienced_concurrency,
    experienced_delivery,
    experienced_design,
    experienced_internals,
    experienced_online,
    experienced_semantics,
)
from pytuitor_web.models import Lesson, StageContract

CHAPTER_CONTENT = (
    experienced_semantics,
    experienced_composition,
    experienced_design,
    experienced_concurrency,
    experienced_delivery,
    experienced_internals,
    experienced_online,
)
BUILD_INSTRUCTIONS = {
    key: value for chapter in CHAPTER_CONTENT for key, value in chapter.BUILD_INSTRUCTIONS.items()
}
REPAIR_STAGES = {
    key: value for chapter in CHAPTER_CONTENT for key, value in chapter.REPAIR_STAGES.items()
}


FEEDBACK = {
    "python-expressions": (
        "A missing value, blank text, and the string 0 are different inputs; choose the "
        "fallback after trimming only text."
    ),
    "pattern-matching": (
        "The first matching case wins. Put specific shapes before general ones, and use a "
        "guard when the shape alone cannot decide."
    ),
    "objects-not-boxes": (
        "A new outer dictionary still shares nested containers. Check which object "
        "changes after a nested edit."
    ),
    "call-contracts": (
        "Defaults, keyword-only arguments, and inclusive numeric boundaries are separate "
        "parts of the call contract."
    ),
    "collection-idioms": (
        "Replacing a group loses previous names; appending every occurrence loses "
        "uniqueness. Preserve first-seen order for both."
    ),
    "callable-tools": (
        "Sorting should use the supplied key and remain stable; closures must remember "
        "their own factor."
    ),
    "functional-pipelines": (
        "Filter before transforming; a left fold calls combine with the accumulator first"
        " and preserves the empty initial value."
    ),
    "functions-with-memory": (
        "An omitted bucket needs a new list, but an explicitly supplied empty bucket must"
        " be reused. Forward all wrapped arguments."
    ),
    "decorator-factories": (
        "The factory receives configuration, the decorator receives a function, and the "
        "wrapper receives each call."
    ),
    "lazy-by-design": (
        "Creating an iterator must not exhaust its source. Read only enough input to "
        "supply the next requested value."
    ),
    "logging-basics": (
        "Use the named logger with arguments rather than an f-string, keep exact messages, "
        "and leave logging configuration to the application."
    ),
    "exception-boundaries": (
        "Translate only the intended conversion error, chain its cause, and close the "
        "stream on every exit."
    ),
    "context-practice": (
        "An absent key differs from a key holding None. Restore state in finally without "
        "suppressing the body error."
    ),
    "managed-contexts": (
        "Returning a resource from enter and returning a suppression decision from exit "
        "have different meanings."
    ),
    "iterator-tools": (
        "A yielded list remains visible to the caller. Create a fresh batch instead of "
        "clearing and reusing the previous list."
    ),
    "iterator-recipes": (
        "Preview is bounded, alignment pads rather than truncates, and a product contains"
        " every pair."
    ),
    "adjacent-groups": (
        "Adjacent runs are not global groups. Consume each run before advancing and allow"
        " equal unhashable labels."
    ),
    "ready-to-ship": (
        "A test that passes on your implementation may still be ineffective. Check zero, "
        "invalid input, and a deliberately incorrect implementation."
    ),
    "sqlite-records": (
        "Pass every value through ? placeholders and commit each change; a closed connection "
        "loses anything left uncommitted."
    ),
    "data-models": (
        "A frozen value is replaced by a new instance; restocking must not mutate the original."
    ),
    "dataclass-lifecycle": (
        "Default factories separate instance lists; replacing a dataclass does not "
        "automatically copy nested mutable fields."
    ),
    "typed-contracts": (
        "Annotations describe relationships without converting values. Keep falsy items "
        "and consume only the requested amount."
    ),
    "practical-object-protocols": (
        "Validate before storing a property, preserve operands during addition, and "
        "return NotImplemented for unsupported operand types."
    ),
    "class-construction": (
        "An inherited class factory should construct cls, not a fixed concrete class. "
        "Abstract methods enforce the required interface."
    ),
    "structural-typing": (
        "Use the required operation on the supplied object; do not require inheritance or"
        " depend on a write return value."
    ),
    "test-doubles": (
        "Retry only the documented error, pause between attempts rather than after the "
        "last one, and preserve the final failure."
    ),
    "coroutine-basics": (
        "Calling a coroutine does not run it. Await cooperative work for each value, "
        "including zero."
    ),
    "clean-exits": (
        "Cleanup belongs in finally; gather preserves input order while overlapping "
        "coroutine progress."
    ),
    "task-groups": (
        "Create every task before awaiting group completion, then read results in input "
        "order after all children have finished."
    ),
    "async-streams": (
        "Use async iteration, strip before deciding whether to keep text, and propagate "
        "source errors."
    ),
    "module-boundaries": (
        "A reusable module must import quietly and define the actual reusable behavior in"
        " its own file."
    ),
    "package-metadata": (
        "Read the project table rather than root-level keys; an optional dependency list "
        "can be absent without hiding malformed TOML."
    ),
    "cli-contracts": (
        "Let argparse handle ordering and integer conversion, then return the documented "
        "plain dictionary."
    ),
    "resource-paths": (
        "Only a missing file gets defaults. A malformed document or a non-object JSON "
        "value is a different failure."
    ),
    "descriptors": (
        "A descriptor is shared by a class, but stored values belong to individual "
        "instances. Class access has no instance."
    ),
    "metaclasses": (
        "Read directly declared attributes and reject collisions before replacing an "
        "existing registration."
    ),
    "method-resolution": (
        "super follows the actual instance MRO, not a fixed parent. Each cooperating "
        "method contributes once."
    ),
    "installing-packages": (
        "Ask importlib.metadata about the distribution name; importing can fail for an "
        "installed package whose import name differs."
    ),
    "pytest-basics": (
        "Tests are useful only when they fail for broken code. Cover the rounding case, both "
        "percent boundaries, and the promised ValueError."
    ),
    "web-requests": (
        "A 404 or 500 reply is still a response. Handle 404 first, raise for other errors, "
        "send values through params or json=, and always set a timeout."
    ),
    "runtime-inspection": (
        "Read signature parameters, not local variable names; inspection must never "
        "execute the function."
    ),
}


def build_stage(lesson: Lesson) -> StageContract:
    """Project an established Build authoring record into an explicit contract."""
    references = lesson.solution_files or {lesson.entrypoint: lesson.solution}
    return StageContract(
        instructions=BUILD_INSTRUCTIONS[lesson.id],
        checks=tuple(
            replace(check, nudge=FEEDBACK[lesson.id])
            if check.nudge == "Compare the actual and expected results for this input."
            else check
            for check in lesson.checks
        ),
        hints=lesson.hints,
        stdin=lesson.stdin,
        files=lesson.files,
        starter_files={name: "" for name in lesson.files},
        reference_files=references,
    )


def apply(lessons):
    """Attach explicit stage contracts and derive compatibility fields."""
    refreshed = []
    for lesson in lessons:
        build = build_stage(lesson)
        repair = REPAIR_STAGES[lesson.id]
        entrypoint = lesson.entrypoint
        refreshed.append(
            replace(
                lesson,
                revision=7 if lesson.id == "class-construction" else 6,
                solution=build.reference_files[entrypoint],
                repair=repair.starter_files[entrypoint],
                checks=build.checks,
                hints=build.hints,
                stdin=build.stdin,
                files=build.files,
                solution_files=build.reference_files,
                repair_files=repair.starter_files,
                build_stage=build,
                repair_stage=repair,
            )
        )
    return tuple(refreshed)
