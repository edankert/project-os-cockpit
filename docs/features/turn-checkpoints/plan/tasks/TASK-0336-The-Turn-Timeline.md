---
type: "[[task]]"
id: TASK-0336
aliases: ["TASK-0336"]
title: "The turn timeline — each turn with the shape of what it changed, so the wrong turn is findable"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-11
source: ["[[FEAT-0078-Turn-Checkpoints]]"]
parent: "[[FEAT-0078-Turn-Checkpoints]]"
effort: M
depends: ["[[TASK-0335-Capture-Per-Turn]]"]
blocks: ["[[TASK-0337-Restore-As-A-Recorded-Action]]"]
related: ["[[ISS-0096-No-Surface-Says-What-Changed]]"]
tests: []
---

# The turn timeline

## Definition of Done

- A session's turns list with, per turn, the files touched grouped by kind and the counts — the same shape [[ISS-0096]] defines, computed between adjacent checkpoints, and sharing its implementation rather than growing a second one.
- The row says what the turn was *for* where the ledger knows it (the dispatched item), so a timeline reads as work rather than as diffs.
- Absent checkpoints, the surface says so plainly instead of rendering an empty list.

## Done — 2026-08-11

`checkpoints.turns()` — each checkpoint with the files changed since the one before it, grouped by kind.

**It shares [[ISS-0096]]'s `_shape_kind` rather than growing a second one**, as the DoD requires. *"Which files, grouped by kind"* is one question and it now has one answer; computing it a second way here is how the two would come to disagree about what counts as a test — [[ISS-0023]]'s failure in a new place. A test asserts the import and asserts the buckets are **not** restated locally.

Newest first, each row describing the step *into* it: reading down the list is reading the work backwards, which is how somebody looks for where a thing went wrong.

### The bug this found, kept as its guard

The first rendering came out **reversed**. Git's `creatordate` has *second* granularity, so two checkpoints taken in the same second tie and the sort is arbitrary — every turn's changes were attributed to its neighbour. For a "where did it go wrong" slider, out-of-order turns are worse than no turns: they point confidently at the wrong place.

Fixed by putting the order in the **ref name** — a microsecond stamp — where it cannot tie, and sorting by `-refname`. `test_turns_are_newest_first_even_within_one_second` writes four checkpoints as fast as the loop runs and asserts the order.

The earliest checkpoint reports `from_start` rather than `0 files`, because "this turn did nothing" and "we started measuring here" are different facts.
