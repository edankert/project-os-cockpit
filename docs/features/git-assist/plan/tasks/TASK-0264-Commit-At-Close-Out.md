---
type: "[[task]]"
id: TASK-0264
aliases: ["TASK-0264"]
title: "close-out-commit.sh — stage what the work declares, refuse what it does not"
status: done
phase: "[[PHASE-021-Git-Is-Not-The-Users-Job]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0055-Git-Assist]]"]
parent: "[[FEAT-0055-Git-Assist]]"
effort: M
depends: []
blocks: []
related: []
tests: []
---

# Commit at close-out

## Definition of Done
- [x] `tools/scripts/close-out-commit.sh <paths…>` stages exactly those paths and commits
- [x] **Never `git add -A`** — a dirty file outside the given paths is reported and left alone, and the commit still happens
- [x] The message is built from the notes: the IDs closed and their titles
- [x] Refuses to run with **no** paths — that is the `-A` failure wearing a different name
- [x] Refuses on a detached HEAD or mid-rebase
- [x] Does not push
- [x] The existing pre-commit hook still gates it — no `--no-verify`, ever

## Steps
- [x] The script, with the out-of-scope report
- [x] A close-out rule in `CLAUDE.md` pointing at it (`tools/instructions/` is template-owned)
- [x] Test: staging is scoped, an outside-scope dirty file survives, empty args refuse, `--no-verify` absent

## Notes

**`git add -A` is the whole hazard.** Measured 2026-07-30: `your-trainer` 44 dirty files and `your-health` 8, unrelated to the work in hand and deliberately untouched. Automation that adds everything makes someone else's half-finished afternoon part of your commit.

Reporting the out-of-scope files rather than failing on them is deliberate: they are usually legitimate parallel work, and a close-out that refuses to complete because an unrelated file is dirty is an automation people disable.

## Done 2026-07-30

`tools/scripts/close-out-commit.sh`. Nine tests against real throwaway repositories — the behaviour under test is git's, and a mocked git would only prove the mock.

The two that matter, both mutation-verified: **a dirty file outside the given paths is not committed and survives**, and **no paths refuses** rather than falling back to `-A`.

**A granularity trap on the way.** `git status --porcelain` collapses untracked content to the *directory* (`src/`, not `src/unrelated.py`), so the first cut compared directories against filenames and reported every untracked file as out-of-scope even when it had just been staged. `--untracked-files=all` fixes it. My test then failed for the same reason one line later.
