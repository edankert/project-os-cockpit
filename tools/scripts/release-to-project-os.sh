#!/usr/bin/env bash
# Release the canonical docs-server source into project-os/tools/docs-server/.
#
# Direction: docs-server (canonical) → project-os (delivery copy). One-way.
# The sync overwrites; nothing flows back. Run after closing any CHG that
# touches src/docs_server/ or pyproject.toml — the LIFECYCLE.md rule
# obligates the agent to do so.
#
# Guards:
# - canonical repo must be clean (no staged or unstaged changes)
# - project-os destination must be clean (no uncommitted local edits)
# - rsync uses --delete so removed files in the canonical source disappear
#   from project-os — but only inside tools/docs-server/, scoped tightly.
#
# Outputs in the project-os copy:
#   src/docs_server/  — the package source tree (the only thing run at runtime)
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
DEST="$PROJECT_OS_ROOT/tools/docs-server"

if [[ ! -d "$PROJECT_OS_ROOT" ]]; then
  echo "error: project-os not found at $PROJECT_OS_ROOT" >&2
  echo "       set PROJECT_OS_ROOT to override the location." >&2
  exit 2
fi

# -------- guard: canonical repo must be clean --------------------------

cd "$CANONICAL_ROOT"
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "error: canonical repo ($CANONICAL_ROOT) has uncommitted changes." >&2
  echo "       commit or stash before releasing — the project-os copy" >&2
  echo "       must trace to a real canonical commit." >&2
  git status --short >&2
  exit 3
fi

# -------- guard: project-os destination must be clean ------------------

if [[ -d "$DEST" ]]; then
  cd "$PROJECT_OS_ROOT"
  if ! git diff --quiet -- "tools/docs-server" \
      || ! git diff --cached --quiet -- "tools/docs-server"; then
    echo "error: project-os destination has uncommitted edits at" >&2
    echo "       $DEST" >&2
    echo "       review and commit / discard them before re-syncing." >&2
    git status --short -- "tools/docs-server" >&2
    exit 4
  fi
  cd "$CANONICAL_ROOT"
fi

# -------- ensure destination exists ------------------------------------

mkdir -p "$DEST"

# -------- run the sync (rsync with explicit include set) ---------------

# Each rsync handles one top-level path so we don't accidentally clobber
# project-os/tools/docs-server/run.sh (which is project-os-owned, not
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

echo "synced docs-server $CANONICAL_SHA → $DEST"
echo "remember to commit the result in project-os."
