---
type: "[[task]]"
id: TASK-0350
aliases: ["TASK-0350"]
title: "The bounded tail read gets a guard that fails when the bound is lost, and the surviving mutants get killed"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent"]
parent: "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"
effort: M
due: ""
depends: ["[[TASK-0348-Synthetic-Entries-Are-Not-Turns]]"]
blocks: []
related: ["[[ISS-0109-The-Bounded-Tail-Read-Has-No-Guard]]"]
tests: []
---

# Guards for the bounded read

Fixes [[ISS-0109-The-Bounded-Tail-Read-Has-No-Guard]].

## Definition of Done
- [x] A test **observes bytes read** for a fixture larger than the budget and fails when `_read_tail` stops seeking — replacing `start = max(0, size - budget)` with `start = 0` must turn the suite red.
- [x] The mutants the review found surviving are killed, each by a test that asserts the behaviour the constant controls rather than the constant's value: `TAIL_BYTES`, `WRITE_MULT_5M`, `FULL_REWRITE_MIN`, the cooling threshold, and both live model-switch preconditions (`read == 0`, `write >= MODEL_SWITCH_MIN_DISCARD`).
- [x] Each new guard is verified by re-running the mutation it exists to catch — a guard added without seeing it fail is the defect this task is fixing.
- [x] `test_live_state_does_not_read_whole_file` is renamed or rewritten so its name matches what it checks.

## Notes
The docstring said "the read is bounded" and the body asserted only that the right answer came out — which it does whether the read is 512KB or 34MB. A test that cannot fail does not guard, and this one was protecting the constraint the two-entry-point design exists for.
