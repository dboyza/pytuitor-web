# Architecture

Pytuitor Web is a local application: a Python server on the loopback interface and a React workbench in the browser.
Nothing leaves the computer; lessons, checks, progress, and terminals all run locally.

## Launch and sign-in

`pytuitor-web` opens a profile, starts Uvicorn on `127.0.0.1`, and opens a one-time sign-in link.
The link's token is exchanged once for an HTTP-only, same-site session cookie and expires after ten minutes.
Every API request needs that cookie; writes also need the exact origin and an `x-pytuitor` header.
WebSocket handshakes check the origin and cookie themselves, because HTTP middleware does not run for them.
Only one server can open a profile at a time, enforced by the profile lock in `state.py`.

## Progress and drafts

`state.py` stores the version 4 profile forked from Pytuitor, so its drafts, checks, game history, and reviews use the same format.
Profiles live in the platform data directory under `pytuitor-web`, or in `--data-dir`.
Browser-only preferences, such as pane sizes and terminal text size, stay in local storage.

## Workspaces on disk

Each stage has a real folder: `workspaces/<lesson>/<build|repair>/` inside the profile.
The draft's files, called tracked files, are mirrored there, and the stage's terminal opens in that folder.
The editor saves each file after a short pause, writing the draft and the disk together.
While a lesson is open, the browser polls the stage every 1.5 seconds:

- A tracked file changed on disk, such as by the terminal, is adopted into the draft and shown in the editor.
- A tracked file saved by another tab is fetched by comparing server fingerprints.
- A missing required file is restored from the draft; a missing extra file is removed from the draft.
- Other files, such as program output, are listed as untracked until the learner adds them.

Unsaved editor changes always win over a poll; the pending save then overwrites the disk.
`.venv`, `__pycache__`, `.git`, and other tool folders are never listed or tracked.

## Run, Check, and the terminal

The terminal is a real shell on a pseudo-terminal, streamed over a WebSocket and rendered by xterm.js with the bundled JetBrains Mono Nerd Font.
Shells use private rc files, so the learner's own dotfiles are neither read nor modified; the tutor's Python comes first on `PATH`.
Run types `python <entry file>` into the stage's shell, interrupting a running program first.
Check never uses the shell: `runner.py` copies the tracked files into a temporary folder and runs each authored check in `_worker.py`.
Check results stream to the browser as newline-delimited JSON, and closing the request stops the check's process tree.
Passing a game milestone's Extend stage saves an immutable checkpoint, exactly as in the terminal edition.
Playing a checkpoint opens a temporary folder and runs the game directly on a pseudo-terminal, removing the folder when it ends.

Process limits and isolation are not an operating-system sandbox, and the embedded shell has the user's own permissions.
On Windows the shell runs PowerShell through ConPTY via pywinpty; this path has not been verified on Windows yet.

## Frontend

`frontend/` is a Vite and React application built into `src/pytuitor_web/static/`, which the server serves with a single-page fallback.
CodeMirror 6 provides the editor, and one Lezer highlighter colors the editor, lesson examples, and references through `--tk-*` tokens.
`workbench/useWorkspace.ts` owns autosave, flushing before Run and Check, and polling.
`terminal/TerminalDock.tsx` keeps one shell per stage alive while the server runs, so leaving and returning to a lesson reattaches with its scrollback.
