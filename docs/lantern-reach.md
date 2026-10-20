# Your growing game: Lantern Reach

Lantern Reach is an offline text adventure about exploring a valley, helping its residents, and restoring an outpost.
You write the Python yourself, starting with a few questions and growing it into a persistent, tested game.
The first three course sections finish a playable core adventure.
Optional depth adds capabilities such as cave traversal, streaming chronicles, concurrent scouts, packaging, journal formatters, and a ranger station report.

## Find your game

Choose **Your game** in the sidebar, or search for any milestone with Ctrl+K (⌘K on a Mac).
The page lists all 22 milestones, their progress, and the working versions of each one.
Choose a milestone to see its story and starting-code origin, then select **Open milestone**.
The syllabus also lists each milestone at the end of its chapter.
Continue follows the recommended lessons and milestones; optional sections still require an explicit choice.

## Extend, check, and repair

Ordinary lessons begin with blank Build exercises.
Game milestones use **Extend**: the first starts blank, and later ones continue a compatible working checkpoint from your own code.
Required new files start blank unless they contain supplied earlier code.
Your extra files and creative changes are retained.
Refactors such as splitting modules or creating a package are explicit learner tasks; Pytuitor does not rewrite your Python.

Use Run to play and Check to exercise the stated behavior and retained capabilities.
A successful Extend saves an immutable working checkpoint only for the exact checked file snapshot.
Editing the current draft requires checking again, while its earlier working version remains in history.
Repair opens a separate authored incident, preserving your Extend draft and checkpoint.
Complete both stages, then choose Next to continue.

Every focused lesson includes a concrete connection to the game feature its chapter prepares.
Hints and references remain explicit.
Revealing a reference records that support; it does not replace your draft.
When continuing extra optional features, keep those features while adapting the canonical reference's approach.

## Skip ahead without losing your work

If no compatible earlier checkpoint exists, the milestone starts from clearly labeled supplied earlier code.
This is the previous working game, not the current milestone's completed solution.
Skipped milestones remain incomplete, and the source provenance stays visible in future checkpoints.

**Start from supplied code** on the game page starts a fresh supported attempt after confirmation.
If a draft already exists, both Extend and Repair source files are exported before the attempt is replaced.
Historical checkpoints remain intact.
For manual adaptation, continue your existing source and use the new requirements and explicit reference comparison.

Optional capabilities follow their real preparation rather than a single compulsory chain.
Packaging can be entered from the core game without completing async.
Compatible earlier extra capabilities are carried forward and included in later checks; silently dropping them cannot earn a new working checkpoint.
Independent histories are not automatically merged.

## Revisit, play, restore, and export

The game page lists each milestone's immutable working versions with their support provenance.
**Play** runs a temporary copy of the selected version in a terminal; its source and your active drafts remain unchanged.
Close the dialog to end it, or end an input stream with Ctrl+D.
Temporary play does not retain generated saves.

**Restore** requires confirmation, backs up both current stage drafts, and copies the selected compatible source into a new attempt.
The restored draft must be checked against the current milestone contract.
A damaged or missing checkpoint produces an error; use another version or a supplied base without discarding your draft.
History shows its source-storage size and is retained until you explicitly start over; there is no automatic pruning.

**Download** saves that version as a zip file; **Download latest game** saves the latest working version.
Each download is also kept in a new folder under the profile's `exports/` folder, which never overwrites an existing destination.
The archive includes Python source, instructions, and a provenance manifest.
Use Python 3.11 or newer to run `python game.py` from the unzipped folder.
The packaging milestone also supports `python -m lantern_reach` and authors installable package metadata.
Build tooling may require an explicitly requested download; normal source play is offline and requires no third-party runtime packages.
The optional ranger milestone imports requests only inside its report functions, so the rest of the game still runs without it; its `requirements.txt` lists what `report URL` and the pytest tests need, and installing them needs internet.

A core expedition starts at the outpost.
Visit the forest and gather wood, return to deliver two pieces to Mira, then restore the beacon.
Help Oren with rope and Tess with wood to improve the settlement.
Use help to discover the current version's commands and keep exploring after the ending.
Earlier checkpoints intentionally have fewer commands and may start with an arrival questionnaire.

## Keep player saves

Your program's save files are separate from your Python source and from tutor checkpoints.
In an editable milestone, Run happens in the stage's workspace folder, so a save written there is available to the next run.
New files appear under **Other files** in the file list; they are not part of your draft or its checks.
Add a file to the workspace only when the exercise should include it, because Check copies workspace files into a fresh folder.
A downloaded game writes its saves normally in the folder where you run it.

## Existing profiles and recovery

Existing supported profiles migrate to version 4 with the original JSON retained as `profile-before-v4.json`.
Lesson IDs, both old stage drafts, known topics, and historical completion remain intact.
Game records are separate and do not fabricate achievements from old project completion.
Older Pytuitor versions cannot read the new schema; close the tutor and copy the preserved original backup into a separate profile if you need to return to that older version.
Keep the current profile and project checkpoint directory intact when doing so.

Resetting a stage backs up its source and restores its chosen Extend base or the authored broken Repair.
Starting over clears profile progress and references to history after confirmation; files already exported remain separate.
Do not use your personal profile for experiments or automated validation; use `--data-dir` with a scratch directory.
