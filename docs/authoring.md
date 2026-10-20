# Exercise authoring

`StageContract` in `src/pytuitor_web/models.py` is the typed boundary for stage-specific learner instructions, starter files, reference files, checks, hints, and input.

`Lesson.stage_contract("build")` and `Lesson.stage_contract("repair")` provide compatible Build defaults for existing units.

The five First programs units use the `_FOUNDATION_STAGES` table in `src/pytuitor_web/beginner_course.py` as their canonical active stage content.

The legacy `Lesson` fields remain populated as compatibility projections for imports and saved drafts.

Author explicit contracts for both stages, with distinct scenarios or debugging decisions.
Compatibility defaults support legacy callers; they are not a reason to reuse the Build exercise as Repair.

Keep each Repair solvable with concepts already taught, behavior-based, and meaningfully different from its Build scenario.

The remaining 38 beginner units keep `BUILD_INSTRUCTIONS` and `REPAIR_STAGES` in the `src/pytuitor_web/content/beginner_*.py` chapter modules, assembled by `beginner_stage_refresh.py`.
Their Build references and checks remain in `beginner_course.py` and `beginner_extensions.py`; the course assembly projects active contracts into the compatibility fields.

The 41 experienced units keep Build records, complete instructions, independent Repairs, and boundary probes together in `src/pytuitor_web/content/experienced_*.py`.
`experienced_course.py` and `experienced_stages.py` assemble those records; `experienced_authoring.py` contains the small shared constructors.

Lesson Markdown keeps teaching and worked examples; stage requirements, starters, references, checks, and hints belong to the stage contracts.
Instructions render as Markdown: use code spans for names, explicit input/output examples, and separate paragraphs for distinct requirements.
Keep the complete contract when moving it out of lesson prose, including file names, return shapes, output, input assumptions, and edge cases.
Keep prerequisite explanations in the teaching body, especially when removing an old exercise section.

Before `small-superpowers`, Repair programs use top-level input, variables, and loops rather than function definitions or comprehensions.
Do not introduce dictionaries before `word-counts`.
Describe the desired behavior in the prompt; reserve diagnosis and fixes for progressive hints.
Check-specific nudges override the first stage hint; the first hint is the fallback when every case concerns the same defect.

For multi-step checks, `_scenario_check` keeps setup and assertions readable without adding runner APIs.
Online-chapter checks use the worker's `__practice_server__(respond)`, a JSON server on 127.0.0.1, and `__pytest_run__(path)`, which reimports learner tests so a check can swap in a broken function; never contact the internet from a check.
Its script assigns `result` in the worker's fresh namespace; give it a plain-language description of the operation and fixture.
Test observable behavior, including written files, input preservation, and conflicts, rather than source spelling.
Retain plausible incomplete repairs that must fail and valid alternative implementations that must pass.

Increase the lesson revision when changing either executable stage contract.
Old drafts and historical completion stay preserved, but an old checked revision must not unlock or pass a changed stage.
Use each stage's `reference_files` in journeys and exports; the legacy `lesson.solution` describes Build only.

Run `scripts/check.sh` after changing a stage contract.

## Teaching and visual review

Apply the [chapter-specific challenge criteria](teaching-criteria.md) to both stages.
Keep any new prerequisite explanation before the exercise needs it.
`checkpoints.py` authors optional predictions; attach these before catalog assembly so reorganization preserves authored contracts.

The stage tab shows the complete requirements beside the editor, so test short and long requirements with the editor and terminal visible.
The reference comparison is a read-only dialog with a line diff against the learner's draft.
Inspect changed pages in a real browser at desktop and narrow widths, in both themes, and keep screenshots under `.artifacts/`.

## Growing game content

`content/lantern/` authors Lantern Reach's 22 milestones, their implementation briefs in `briefs.py`, and the 84 lesson-to-game connections.
`project_catalog.py` assembles stable milestone IDs and makes each chapter's lessons the milestone's preparation.
`ProjectMilestone` defines the supplied earlier-code base and declared capabilities; `Lesson.project_id` adapts its stages into the existing workbench and runner.
The first milestone starts blank; later Extend stages start from a learner checkpoint or an explicitly labeled supplied earlier version.
Repair is authored separately and never becomes the next milestone's source.

Every feature must have a playable command or other visible outcome as well as behavioral checks.
References must stay inside the taught syntax boundary, especially before functions, comprehensions, decorators, and classes.
Declare intentional API changes at refactors and retain prior observable behavior through the current acceptance suite.
The workspace's active contract adds regression checks for extra optional capabilities inherited from the selected parent.
A canonical reference demonstrates the authored base; learners carrying extra features must retain and adapt those features too.

Keep `connections.py`, milestone requirements, hints, references, broken Repairs, and checks synchronized.
Run `tests/test_growing_project.py`, the full regressions, visual journeys, and installed smoke after contract changes.
Profiles migrate to version 4 with an original backup; do not infer game completion from old lessons or optional projects.

## Feedback observations and mixed reviews

Compound Lantern Reach scenarios use `__expect__(label, actual, expected, comparison="==")` to record concrete evidence while returning the comparison result.
Evaluate the learner operation once and pass its value to the helper; do not rerun it for diagnostics.
The worker records at most 16 observations per case, retaining an encountered failure when the observation list is full.
Keep labels plain and explain the expected behavior in the check's description and nudge.

Author optional mixed sessions in `content/reviews/`, with one prediction, one broken debugging task, and one small implementation per chapter.
Each task needs a stable ID, explicit observable requirements, a reference, and meaningful checks or an explained prediction answer.
Stay within that chapter's taught prerequisites and accept equivalent implementations.
Reviews use the existing runner and separate progress records; never register them as required course activities.
Validate all prediction outputs, all coding references, and failure of all broken starters with the real runner.
Review pacing and scheduling live in `review_progress.py`.
