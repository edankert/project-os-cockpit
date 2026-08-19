---
type: "[[task]]"
id: TASK-0529
aliases: ["TASK-0529"]
title: "Backfill one ledger per repo from the scalar marks, and measure the gate delta before it lands"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0133-The-Ledger-Is-The-Only-Place-A-Verdict-Lives]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The backfill, and the number that must precede it

## Definition of Done

- [ ] `project-os-cockpit` (34 notes), `your-sudoku` (56), `your-trainer` (581) each get one backfilled ledger.
- [ ] `done` → one `pass` entry. `todo` → **no entry**. `incomplete` → `partial` with a reason.
- [ ] **`canceled` → `na`, never `excused`.** Measured 0 occurrences fleet-wide, so the rule costs nothing — but it must be written down, because decision 6 gave the old single value two successors and a migration that guesses would silently make a permanent exception expire, or a per-release one permanent. `na` is right for a backfill: nothing in the old field said which release it belonged to, and `excused` is the value that claims one.
- [ ] `important`, `question` and `rerun` → refuse and list. 0 occurrences, so a repo that has one is a repo this script has not been read against.
- [ ] Platform: `your-trainer`'s is **android** — every one of its 513 passes was earned there. The other two repos are single-platform.
- [ ] Each backfilled entry carries `by: migration`, the migration date, and a `note:` naming the pre-migration address from `migrated_from:`.
- [ ] **The gate delta is measured per repo and written into this note before any repo migrates.**

## Notes

**There is no date to recover.** `verdict_date:` is empty on 671 of 671 notes fleet-wide. Reconstructing from `git log -L` over the pre-migration document is possible, partial, and would produce precision indistinguishable from precision anybody could trust. The honest stamp is the migration date plus a `note:` saying so.

**The delta is not symmetric.** 124 `todo` → no entry is the same blocking state. 513 Android passes becoming platform-specific is a sharp tightening of `your-trainer`'s iOS position — which is the deliverable, and is exactly the kind of movement [[ISS-0208]] says nobody may make without seeing the number first.
