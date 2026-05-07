#!/usr/bin/env bash
# Release the canonical project-os-cockpit source into project-os/tools/cockpit/.
#
# Direction: project-os-cockpit (canonical) → project-os (delivery copy). One-way.
# The sync overwrites; nothing flows back. Run after closing any CHG that
# touches src/project_os_cockpit/ or pyproject.toml — the LIFECYCLE.md rule
# obligates the agent to do so.
#
# Guards:
# - canonical repo must be clean (no staged or unstaged changes)
# - project-os destination must be clean (no uncommitted local edits)
# - rsync uses --delete so removed files in the canonical source disappear
#   from project-os — but only inside tools/cockpit/, scoped tightly.
#
# Outputs in the project-os copy:
#   src/project_os_cockpit/  — the package source tree (the only thing run at runtime)
#   pyproject.toml
#   README.md
#   CANONICAL_SHA     — canonical commit hash at sync time
#   CANONICAL_DATE    — ISO date of the sync
#
# tests/ is intentionally NOT synced — the project-os copy is a delivery
# artefact, not a dev environment. Tests live in the canonical repo where
# development happens.
#
# Spec: REQ-0017. Implemented by TASK-0020.

set -euo pipefail

# -------- locate the two repos -----------------------------------------

CANONICAL_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PROJECT_OS_ROOT="${PROJECT_OS_ROOT:-$HOME/Dev/repos/project-os}"
DEST="$PROJECT_OS_ROOT/tools/cockpit"

if [[ ! -d "$PROJECT_OS_ROOT" ]]; then
  echo "error: project-os not found at $PROJECT_OS_ROOT" >&2
  echo "       set PROJECT_OS_ROOT to override the location." >&2
  exit 2
fi

# -------- guard: canonical repo must be clean --------------------------

# Use `git status --porcelain` rather than `git diff --quiet` so untracked
# files (work-in-progress not yet `git add`-ed) also block. The project-os
# copy stamps CANONICAL_SHA=HEAD; if HEAD doesn't represent the working
# tree, the stamp lies.
cd "$CANONICAL_ROOT"
if [[ -n "$(git status --porcelain)" ]]; then
  echo "error: canonical repo ($CANONICAL_ROOT) is not clean." >&2
  echo "       commit (or .gitignore) before releasing — the project-os" >&2
  echo "       copy must trace to a real canonical commit." >&2
  git status --short >&2
  exit 3
fi

# -------- guard: project-os destination must be clean ------------------

if [[ -d "$DEST" ]]; then
  cd "$PROJECT_OS_ROOT"
  if [[ -n "$(git status --porcelain -- tools/cockpit)" ]]; then
    echo "error: project-os destination has uncommitted edits at" >&2
    echo "       $DEST" >&2
    echo "       review and commit / discard them before re-syncing." >&2
    git status --short -- "tools/cockpit" >&2
    exit 4
  fi
  cd "$CANONICAL_ROOT"
fi

# -------- ensure destination exists ------------------------------------

mkdir -p "$DEST"

# -------- run the sync (rsync with explicit include set) ---------------

# Each rsync handles one top-level path so we don't accidentally clobber
# project-os/tools/cockpit/run.sh (which is project-os-owned, not
# canonical-owned).
RSYNC_OPTS=(
  -a --delete
  --exclude '__pycache__'
  --exclude '.pytest_cache'
  --exclude '*.egg-info'
  --exclude '.DS_Store'
)

rsync "${RSYNC_OPTS[@]}" "$CANONICAL_ROOT/src/"        "$DEST/src/"
cp "$CANONICAL_ROOT/pyproject.toml"                    "$DEST/pyproject.toml"
cp "$CANONICAL_ROOT/README.md"                         "$DEST/README.md"

# Remove any previously-synced tests/ directory from older runs.
rm -rf "$DEST/tests"

# -------- write provenance stamps --------------------------------------

CANONICAL_SHA="$(git -C "$CANONICAL_ROOT" rev-parse HEAD)"
CANONICAL_DATE="$(date -u +%Y-%m-%d)"
printf '%s\n' "$CANONICAL_SHA"  > "$DEST/CANONICAL_SHA"
printf '%s\n' "$CANONICAL_DATE" > "$DEST/CANONICAL_DATE"

echo "synced project-os-cockpit $CANONICAL_SHA → $DEST"
echo "remember to commit the result in project-os."
