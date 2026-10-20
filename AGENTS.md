# Pytuitor Web agent guide

## Keep this document useful

This is a living document: keep verified, durable decisions here and update existing guidance instead of appending a work log.
Stay near 100 lines; put details in `docs/`, never secrets or temporary artifacts.

## Product direction

- A local web edition of Pytuitor: browser lessons beside a real terminal on this computer, like the user's Dockyard project.
- The user chose (2026-10-19) a local FastAPI server rather than a hosted site, a fork of Pytuitor's curriculum rather than a shared dependency, and a real shell plus a Run button rather than a program-only console.
- Keep a modern, polished interface with Python blue and yellow accents on neutral grays, in dark and light themes.
- The terminal and editor use the bundled JetBrains Mono Nerd Font; code never renders ligatures, so learners see what they type.
- The course has 84 lessons and 22 Lantern Reach milestones in 22 chapters and six sections; see [the curriculum map](docs/curriculum.md).
- Keep learning, checks, and progress offline and local; no accounts, telemetry, or AI services.
- Lessons use blank Build then Repair; milestones use cumulative Extend then independent Repair; both stages are required.
- Prerequisites advise without blocking; references require explicit reveal and never replace drafts.
- Known topics are skipped by Continue but remain open; optional reviews never block Continue.

## Teaching standards

- Explain new terms and syntax before requiring them; use plain English and standard programming names.
- Lesson prose uses one sentence per line, bolds a term only where it is defined, and never bolds UI labels; tests enforce bold-term order.
- Refer to the web interface in prose: the terminal, the Build tab, Run, Check, Other files; never TUI keys or panes.
- Make blank-editor exercises solvable: specify names, signatures, input handling, output, and edge cases.
- Verify references pass and Repair programs fail meaningfully; accept valid alternatives and test observable behavior.
- Keep prose, hints, checks, repair code, and references synchronized; bump revisions when stage behavior changes.
- See [the authoring guide](docs/authoring.md) and [challenge criteria](docs/teaching-criteria.md).

## Interaction contracts

- The workbench is lesson (Learn, stage, and Checks tabs) beside an editor above a terminal; panes resize and remember their sizes.
- Below 980 pixels wide, Lesson, Code, and Terminal become tabs; every pane stays mounted so shells keep running.
- Each stage has its own on-disk workspace and shell; switching stages switches terminals without closing them.
- Run flushes saves and types `python <entry>` into the stage shell; Check flushes saves and tests a clean copy, never the shell folder.
- Shortcuts: Mod+Enter runs, Mod+Shift+Enter checks, Mod+S saves, Mod+K searches, Ctrl+backtick focuses the terminal, and ? lists shortcuts.
- Editor changes autosave; terminal edits to tracked files appear in the editor; unsaved editor edits win.
- Untracked files are previewed read-only and join the draft only when the learner adds them.
- Checks open the first failing case with expected, actual, input, and output evidence.
- Opening a lesson is the only action that changes the resume anchor.
- Reset and file removal back up the stage to the profile's `exports/` folder first; Start over moves workspaces there and closes every shell.
- Downloads are zip files; game checkpoint exports also keep a copy in `exports/`.
- Show focus on panes and controls; dialogs trap focus and start on their main action, never the close button.

## Code map and pitfalls

- Forked core, kept close to Pytuitor: `models.py`, `curriculum.py`, `course_map.py`, `content/`, `lessons/`, `project_*`, `state.py`, `runner.py`, `_worker.py`, `execution_policy.py`, `workspace.py`.
- `service.py` owns learning operations and disk workspaces behind one lock; `web.py` is the authenticated API; `cli.py` launches.
- `consoles.py` owns PTYs (POSIX directly, Windows through pywinpty); `shell.py` and `shells/` build private rc files and environments.
- `frontend/src/workbench/` owns the lesson page; `terminal/` the xterm dock; `pages/` the other screens; `styles/` tokens and layout.
- Pass each new stage payload to `useWorkspace().load`; never reload files from an effect, or local state like revealed hints would discard edits.
- The `react-hooks` lint rules forbid synchronous setState in effects and impure render; remount with `key` instead of resetting state.
- Console WebSockets bypass HTTP middleware, so they verify origin and cookie themselves.
- Process limits are not an OS sandbox, and the embedded shell has the user's permissions; say so plainly.
- See [the architecture guide](docs/architecture.md) for sign-in, sync, and execution details.

## Working and verification

- Run `scripts/check.sh` before committing; it covers ruff, pytest, eslint, prettier, TypeScript, vitest, and the build.
- Build the browser assets with `npm --prefix frontend run build`; they land in the ignored `src/pytuitor_web/static/`.
- Use scratch `--data-dir` profiles under `.artifacts/`; never test against the user's progress.
- Reproduce bugs through the browser UI first and keep meaningful regressions in `tests/test_web.py`.
- Inspect real-browser screenshots at desktop and narrow widths in both themes; keep artifacts in `.artifacts/`.
- Windows support is implemented but unverified; report it that way until it is tested on Windows.
- Report only validation actually performed.
- Never use em dashes, agent co-authors, or manual changelog or generated-file edits.
- Make local commits; push or publish only when instructed; add no hosted CI.
- Suggest a concrete next step after major work.
