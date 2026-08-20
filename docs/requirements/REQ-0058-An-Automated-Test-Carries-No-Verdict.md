---
type: "[[requirement]]"
id: REQ-0058
aliases: ["REQ-0058"]
title: "An automated test carries no verdict"
status: implemented
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: ["[[ADR-0038-The-Suite-Is-The-Verdict]]"]
priority: high
scope: "Every TST-* note whose `command:` is non-empty — 139 fleet-wide on 2026-08-19."
acceptance: ["A note with a non-empty `command:` holding `ready`, `passing` or `failing` is a validator error", "A note with a non-empty `command:` holding `last_run:` or `exit_code:` is a validator error", "`run-tests.py --write` mutates no note frontmatter", "Manual tests keep their verdict, asserted by count before and after"]
implements: "[[FEAT-0139-The-Suite-Is-The-Verdict]]"
verifies: []
related: ["[[ADR-0038-The-Suite-Is-The-Verdict]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]"]
tests: []
---

# An automated test carries no verdict

## Statement

A test note that declares a `command:` **must not** hold `ready`, `passing` or `failing`, and **must not** carry `last_run:` or `exit_code:`. Its status vocabulary is lifecycle only — `draft`, `active`, `retired`.

## Acceptance Criteria

- [x] The forbidden-status check ranges over `command:` non-empty, not over `level: acceptance` — `ACCEPTANCE-STATUS`'s domain went 89 → 139 notes; `tests/test_automated_test_holds_no_verdict.py`
- [x] `last_run:` and `exit_code:` are refused on the same population — `TEST-AUTOMATED-EVIDENCE`
- [x] `run-tests.py --write` leaves every note byte-identical — `tests/test_runner_writes_nothing.py`, asserted on bytes rather than on `status`, and the mutant fails 4 of 6
- [x] Manual tests are untouched — `test_a_manual_test_may_still_record_its_verdict` and `test_a_manual_note_can_still_be_stamped`. **Measured correction**: the population is 65 fleet-wide but 5 in this repo, and the migration changed 38 notes here, 0 of them manual

## Notes

This is not a new constraint. `ACCEPTANCE-STATUS` enforces it today as an error over the 89 automated notes at `level: acceptance` — 64% of the domain — and cannot say why it stops there.
