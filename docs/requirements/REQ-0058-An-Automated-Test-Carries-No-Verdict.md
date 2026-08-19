---
type: "[[requirement]]"
id: REQ-0058
aliases: ["REQ-0058"]
title: "An automated test carries no verdict"
status: draft
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
source: ["[[ADR-0038-The-Suite-Is-The-Verdict]]"]
priority: high
scope: "Every TST-* note whose `command:` is non-empty — 139 fleet-wide on 2026-08-19."
acceptance: ["A note with a non-empty `command:` holding `ready`, `passing` or `failing` is a validator error", "A note with a non-empty `command:` holding `last_run:` or `exit_code:` is a validator error", "`run-tests.py --write` mutates no note frontmatter"]
implements: "[[FEAT-0139-The-Suite-Is-The-Verdict]]"
verifies: []
related: ["[[ADR-0038-The-Suite-Is-The-Verdict]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]"]
tests: []
---

# An automated test carries no verdict

## Statement

A test note that declares a `command:` **must not** hold `ready`, `passing` or `failing`, and **must not** carry `last_run:` or `exit_code:`. Its status vocabulary is lifecycle only — `draft`, `active`, `retired`.

## Acceptance Criteria

- [ ] The forbidden-status check ranges over `command:` non-empty, not over `level: acceptance`
- [ ] `last_run:` and `exit_code:` are refused on the same population
- [ ] `run-tests.py --write` leaves every note byte-identical
- [ ] The 65 manual tests that record a human verdict are untouched, asserted by count before and after

## Notes

This is not a new constraint. `ACCEPTANCE-STATUS` enforces it today as an error over the 89 automated notes at `level: acceptance` — 64% of the domain — and cannot say why it stops there.
