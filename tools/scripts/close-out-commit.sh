#!/usr/bin/env bash
# Commit the work a close-out just finished (FEAT-0055 / TASK-0264).
#
# Usage: close-out-commit.sh <path> [<path> ...] [-m "extra context"]
#
# Stages EXACTLY the paths given and commits them. Anything else that is
# dirty is reported and left alone.
#
# Why not `git add -A`: measured on 2026-07-30, `your-trainer` carried 44
# uncommitted files and `your-health` 8, none of them the work in hand
# and all deliberately untouched. Automation that adds everything makes
# somebody else's half-finished afternoon part of your commit, and that
# is worse than no automation at all.
#
# The message is derived from the project-os IDs among the staged notes,
# so the commit says which items closed without anyone retyping it.
#
# Does NOT push. A commit is local and reversible; a push is publishing.
set -uo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "close-out-commit: not a git repository" >&2; exit 2; }
cd "$ROOT" || exit 2

EXTRA=""
PATHS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -m) EXTRA="${2:-}"; shift 2 ;;
    -h|--help) sed -n '3,20p' "$0"; exit 0 ;;
    *) PATHS+=("$1"); shift ;;
  esac
done

# No paths is `git add -A` wearing a different name.
if [[ ${#PATHS[@]} -eq 0 ]]; then
  echo "close-out-commit: no paths given." >&2
  echo "  Name what this close-out touched. Committing everything is the" >&2
  echo "  one thing this script exists to prevent." >&2
  exit 2
fi

# A commit built on top of a half-finished operation is not the commit
# anyone meant to make.
if ! git symbolic-ref -q HEAD >/dev/null; then
  echo "close-out-commit: detached HEAD — refusing." >&2; exit 2
fi
if [[ -d .git/rebase-merge || -d .git/rebase-apply || -f .git/MERGE_HEAD ]]; then
  echo "close-out-commit: a rebase or merge is in progress — refusing." >&2; exit 2
fi

# What is dirty that we were NOT asked to commit? Reported, never staged.
#
# `--untracked-files=all` matters: the default collapses untracked
# content to the DIRECTORY (`src/`, not `src/unrelated.py`), so the
# scope comparison below would never match a filename and every
# untracked file would be reported as out-of-scope even when it had
# just been staged.
dirty_before="$(git status --porcelain --untracked-files=all | sed 's/^...//')"

git add -- "${PATHS[@]}" || { echo "close-out-commit: git add failed" >&2; exit 1; }

staged="$(git diff --cached --name-only)"
if [[ -z "$staged" ]]; then
  echo "close-out-commit: nothing to commit in the given paths." >&2
  exit 0
fi

outside=""
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  grep -qxF "$f" <<<"$staged" || outside+="  $f"$'\n'
done <<<"$dirty_before"

# Message: the project-os IDs among the staged notes, so the commit says
# what closed without anyone retyping it.
ids="$(printf '%s\n' "$staged" \
  | grep -oE '(FEAT|TASK|ISS|REQ|PHASE|RISK|CHG|ADR|TST|DES|REL)-[0-9]{4}[0-9]*' \
  | sort -u | paste -sd' ' -)"
subject="${ids:-close-out}"
[[ -n "$EXTRA" ]] && subject="$subject: $EXTRA"

body="Committed by close-out (FEAT-0055). Staged paths:"$'\n'
while IFS= read -r p; do [[ -n "$p" ]] && body+="  $p"$'\n'; done <<<"$staged"
if [[ -n "$outside" ]]; then
  body+=$'\n'"Left alone — dirty but outside this close-out's scope:"$'\n'"$outside"
fi

# The pre-commit hook syncs the snapshot and runs the validator. It is
# the gate; --no-verify would defeat the point and is never used here.
if git commit -m "$subject" -m "$body"; then
  echo "close-out-commit: committed ${subject}"
  if [[ -n "$outside" ]]; then
    echo "close-out-commit: left these dirty files alone (outside scope):" >&2
    printf '%s' "$outside" >&2
  fi
  exit 0
fi
echo "close-out-commit: commit refused (see the validator output above)." >&2
exit 1
