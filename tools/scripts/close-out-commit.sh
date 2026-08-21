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

# What this commit changes in SNAPSHOT.yaml's `items:` MEMBERSHIP (ISS-0252).
#
# `sync-snapshot.py` propagates status, counters and metrics; **which items the
# snapshot carries is hand curation it deliberately leaves alone**. So an entry
# another session wrote by hand sits in the shared file until somebody commits
# it, and that somebody may not be the session holding its note.
#
# Measured 2026-08-20, three collisions in one afternoon closing out PHASE-037
# alongside a second session. The one that matters: a commit swept in another
# session's hand-written `PHASE-040:` entry while the note was still untracked,
# which turned `--as-committed` red with `ITEM-FILE` and **did not self-heal** —
# a dangling reference stays dangling. It was visible in `git diff` and nobody
# looked, which is why it is printed here rather than left available.
#
# The local validator cannot catch it: it reads the WORKING TREE, where the
# note exists. Only the committed state is missing it.
#
# Reported, never refused. A close-out that stops because a shared file moved
# under it is automation people disable — the same reason dirty files outside
# the scope are left alone rather than treated as an error.
snapshot_report=""
if grep -qxF "SNAPSHOT.yaml" <<<"$staged" && command -v python3 >/dev/null 2>&1; then
  snapshot_report="$(
    git show HEAD:SNAPSHOT.yaml 2>/dev/null > "$ROOT/.git/close-out-head-snapshot.tmp"
    git show :SNAPSHOT.yaml 2>/dev/null > "$ROOT/.git/close-out-index-snapshot.tmp"
    python3 - "$ROOT/.git/close-out-head-snapshot.tmp" "$ROOT/.git/close-out-index-snapshot.tmp" <<'PY'
import re, subprocess, sys

def members(path):
    """`items:` ids and their `file:`, read line-wise.

    Line-oriented on purpose: this runs inside a commit hook path, must not
    depend on PyYAML, and a parse failure here has to degrade to silence
    rather than block a close-out.
    """
    out, current, depth = {}, None, None
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return out
    inside = False
    for line in text.splitlines():
        if re.match(r"^items:\s*$", line):
            inside = True
            continue
        if inside and line[:1] not in (" ", "\t", "") and not line.startswith("#"):
            break
        if not inside:
            continue
        hit = re.match(r"^(\s+)([A-Z]{2,6}-[0-9A-Za-z-]+):\s*$", line)
        if hit and (depth is None or len(hit.group(1)) == depth):
            depth = len(hit.group(1))
            current = hit.group(2)
            out.setdefault(current, "")
            continue
        if current:
            f = re.match(r"^\s+(?:file|path):\s*\"?([^\"\n]+?)\"?\s*$", line)
            if f:
                out[current] = f.group(1)
    return out

head, index = members(sys.argv[1]), members(sys.argv[2])
added = sorted(set(index) - set(head))
removed = sorted(set(head) - set(index))
lines = []
if added:
    lines.append("  added:   " + ", ".join(added))
if removed:
    lines.append("  removed: " + ", ".join(removed))
#: The non-self-healing case, named separately. An entry whose note is not in
#: the index is a dangling reference the moment this commit lands, and no
#: later commit by anybody clears it.
dangling = []
for item in added:
    rel = index.get(item) or ""
    if not rel:
        continue
    hit = subprocess.run(["git", "ls-files", "--error-unmatch", "--", rel],
                         capture_output=True)
    if hit.returncode != 0:
        dangling.append("%s -> %s" % (item, rel))
if dangling:
    lines.append("  DANGLING (the note is in no commit; --as-committed will "
                 "fail ITEM-FILE and it does not self-heal):")
    for d in dangling:
        lines.append("    " + d)
print("\n".join(lines))
PY
  )"
  rm -f "$ROOT/.git/close-out-head-snapshot.tmp" "$ROOT/.git/close-out-index-snapshot.tmp"
fi

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
if [[ -n "${snapshot_report//[[:space:]]/}" ]]; then
  body+=$'\n'"SNAPSHOT.yaml items: membership changed by this commit (ISS-0252):"$'\n'"$snapshot_report"$'\n'
fi

# The pre-commit hook syncs the snapshot and runs the validator. It is
# the gate; --no-verify would defeat the point and is never used here.
if git commit -m "$subject" -m "$body"; then
  echo "close-out-commit: committed ${subject}"
  if [[ -n "${snapshot_report//[[:space:]]/}" ]]; then
    echo "close-out-commit: SNAPSHOT.yaml items: membership changed (ISS-0252):" >&2
    printf '%s\n' "$snapshot_report" >&2
  fi
  if [[ -n "$outside" ]]; then
    echo "close-out-commit: left these dirty files alone (outside scope):" >&2
    printf '%s' "$outside" >&2
  fi
  exit 0
fi
echo "close-out-commit: commit refused (see the validator output above)." >&2
exit 1
