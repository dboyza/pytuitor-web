#!/bin/bash
# Run every local check: Python lint and tests, then frontend lint, types, tests, and build.
set -euo pipefail
cd "$(dirname "$0")/.."
step() { printf '\n== %s\n' "$1"; }

step "Python lint and format"
uv run --locked ruff check .
uv run --locked ruff format --check .

step "Python tests"
uv run --locked pytest -q

step "Frontend lint, format, types, and tests"
npm --prefix frontend run -s lint
npm --prefix frontend run -s format:check
npm --prefix frontend run -s check
npm --prefix frontend run -s test

step "Frontend build"
npm --prefix frontend run -s build > /dev/null

printf '\nAll checks passed.\n'
