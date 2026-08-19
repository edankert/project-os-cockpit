---
type: "[[task]]"
id: TASK-0528
aliases: ["TASK-0528"]
title: "The validator reads a ledger — required fields, reason-bearing marks, and a sealed ledger that cannot change"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0133-The-Ledger-Is-The-Only-Place-A-Verdict-Lives]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The gate on the ledger

## Definition of Done

- [ ] An entry missing `check`, `mark`, `date`, `by` or `method` is an error naming the file and the index.
- [ ] `fail`, `partial`, `blocked`, `question`, `na` refused without `reason`. `pass` is not.
- [ ] `check` must resolve to an existing acceptance test.
- [ ] An entry may not carry a `platform` that contradicts its file.
- [ ] A sealed ledger differing from its committed content is an error — **proved by a test that edits one and expects the failure**.
- [ ] Errors land upstream in `~/Dev/repos/project-os/tools/scripts/validate-docs.py` first ([[ADR-0030]] decision 6), then sync down.

## Notes

The reason rule is [[ADR-0029]]'s, finally enforceable. Measured 2026-08-19: `verdict_reason:` is non-empty on **0 of 671** notes — the rule has never been tested against anything, because nobody has written one of the four marks that demand it.

Immutability is what makes *"was release R walked?"* answerable. Without it the ledger is a mutable log, which is a scalar with more steps.
