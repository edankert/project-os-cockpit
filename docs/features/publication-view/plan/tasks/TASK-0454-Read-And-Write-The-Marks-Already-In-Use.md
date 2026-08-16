---
type: "[[task]]"
id: TASK-0454
aliases: ["TASK-0454"]
title: "Read and write the marks already in use — [~] and [F], not the [!] this repo invented"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0111-The-Marks-The-Record-Already-Uses]]", "[[ISS-0181-Four-Things-The-Release-Surface-Cannot-Do]] item 1"]
parent: "[[FEAT-0111-The-Marks-The-Record-Already-Uses]]"
effort: S
depends: []
blocks: ["[[TASK-0455-A-Check-Carries-Its-Verdict-And-Its-Witness]]"]
related: ["[[ISS-0177-An-Exception-Mark-Drops-A-Check-With-No-Justification]]", "[[ISS-0141]]"]
tests: []
---

# Read and write the marks already in use

## Why

`ACCEPTANCE_TESTS_v2.1.0.md` carries **6 `[~]` and 1 `[F]`**, used consistently. This repo introduced `[!]` for the same purpose, in a form no suite in the fleet writes, and left it parse-only — [[ISS-0177]] records that a hand-written `[!]` drops a check today with no justification and nothing owed.

The permissive half shipped without the half that asks for a reason. Adopting the existing vocabulary closes that without inventing anything.

## What

| mark | meaning | gate |
|---|---|---|
| `[x]` | passed | satisfied |
| `[~]` | partial, with a reason | reconciled, not blocking ([[ISS-0141]]) |
| `[F]` | failed and tracked | **blocking** |
| `[!]` | still readable, never offered | as today |
| `[ ]` | not walked | blocking |

`[F]` blocks because the parser reads an unrecognised mark as blocking, and for a failed-and-tracked check that is exactly right. **Recorded so nobody later reads it as a parser gap and "fixes" it into a pass.**

## Constraints

- No existing row changes meaning. `../your-trainer`'s seven marked rows parse to the same verdicts after this as before — asserted, not assumed.
- `[!]` is not removed and not promoted. Removing it would break a suite that already uses it; offering it would re-open [[ISS-0177]].
- The `mtime` guard and name comparison from [[FEAT-0103]] still refuse a write to a suite that moved underneath the edit.

## Done when

- [x] `[~]` and `[F]` read and written, each with its own gate treatment
- [x] `[!]` reads as today and appears in no control
- [x] round-trip: parse → write → parse yields the same mark, for every mark in the table
- [x] a row written **by hand** in the existing grammar parses identically to one written by the tool
- [x] `../your-trainer`'s 6 `[~]` and 1 `[F]` unchanged — the corpus assertion
- [x] a write against a moved suite is still refused
