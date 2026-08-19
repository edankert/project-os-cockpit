---
type: "[[task]]"
id: TASK-0529
aliases: ["TASK-0529"]
title: "Backfill one ledger per repo from the scalar marks, and measure the gate delta before it lands"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0133-The-Ledger-Is-The-Only-Place-A-Verdict-Lives]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The backfill, and the number that must precede it

## Definition of Done

- [x] `project-os-cockpit` (34 notes), `your-sudoku` (56), `your-trainer` (581) each get one backfilled ledger.
- [x] `done` → one `pass` entry. `todo` → **no entry**. `incomplete` → `partial` with a reason.
- [x] **`canceled` → `na`, never `excused`.** Measured 0 occurrences fleet-wide, so the rule costs nothing — but it must be written down, because decision 6 gave the old single value two successors and a migration that guesses would silently make a permanent exception expire, or a per-release one permanent. `na` is right for a backfill: nothing in the old field said which release it belonged to, and `excused` is the value that claims one.
- [x] `important`, `question` and `rerun` → refuse and list. 0 occurrences, so a repo that has one is a repo this script has not been read against.
- [x] Platform: `your-trainer`'s is **android** — every one of its 513 passes was earned there. The other two repos are single-platform.
- [x] Each backfilled entry carries `by: migration`, the migration date, and a `note:` naming the pre-migration address from `migrated_from:`.
- [x] **The gate delta is measured per repo and written into this note before any repo migrates.**

## Done 2026-08-19 — `tools/scripts/backfill-ledger.py`, dry-run by default

**The delta is ZERO in all three repos, on the platform the verdicts were earned on.** Measured before writing anything, which is what this task refused to run without:

| repo | checks | entries | `todo` -> no entry | gate on the earning platform | **gate on any other** |
| --- | --- | --- | --- | --- | --- |
| `project-os-cockpit` | 34 | 34 | 0 | 0 -> 0 **(+0)** | **34** |
| `your-trainer` | **581** | 513 | **68** | **62 -> 62 (+0)** | **507** |
| `your-sudoku` | 56 | 0 | 56 | 56 -> 56 **(+0)** | **56** |

*(Corrected 2026-08-19 by independent review, finding 1.* **The script measured a smaller corpus than the gate it protects.** *`acceptance.load(docs)` with no index walks `docs/tests/acceptance/` only; every production gate passes an index, and the indexed branch collects every `[[test]]` at `level: acceptance` anywhere under `docs/` — 581/62 in `your-trainer`, not 579/60. A migration measuring the wrong corpus prints `+0` while destroying a recorded pass: a `mark: done` note outside that directory gets no entry, `apply_ledger` reads it as `todo`, and the gate moves by a number nobody saw. The two notes it would have hit today — `TST-0015`, `TST-0018` — are both `todo`, so the corpus was saved by luck rather than by the check. The script now builds an index; the delta is still 0 everywhere, measured against the corpus the gate actually reads.)*

**Zero is the boring half and it is the half that had to be proved: the backfill is lossless.** Every check that cleared the gate before clears it after, and the 66/56 `todo` rows that became *no entry* keep blocking — the same state by a different mechanism.

**The number that matters is the last column, and it is not a gate that moved.** `your-trainer`'s iOS release is held by **507** checks against Android's 62. Those 505 were always unverified on iOS; the schema had one scalar per check and no way to say so, so they read as verified for both. This is a question the corpus could not previously be asked, answered for the first time — which is why it is reported separately from the delta rather than added to it.

`project-os-cockpit` is backfilled and applied (`docs/releases/ledgers/WORKING-macos.json`, 34 entries). `your-trainer` and `your-sudoku` are **measured and not applied**: both are other repos, `your-trainer` carries 58 files of work in flight, and neither can be committed from here.

## Notes

**There is no date to recover.** `verdict_date:` is empty on 671 of 671 notes fleet-wide. Reconstructing from `git log -L` over the pre-migration document is possible, partial, and would produce precision indistinguishable from precision anybody could trust. The honest stamp is the migration date plus a `note:` saying so.

**The delta is not symmetric.** 124 `todo` → no entry is the same blocking state. 513 Android passes becoming platform-specific is a sharp tightening of `your-trainer`'s iOS position — which is the deliverable, and is exactly the kind of movement [[ISS-0208]] says nobody may make without seeing the number first.
