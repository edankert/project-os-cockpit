---
type: "[[task]]"
id: TASK-0539
aliases: ["TASK-0539"]
title: "Settle the outcome vocabulary in `TAXONOMY.md` upstream — one table, matching the data, legacy readable but not current"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0137-One-Outcome-Vocabulary-Written-Down-Once]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# One table

## Definition of Done

- [ ] `TAXONOMY.md`'s `mark` section is rewritten as the ledger's outcome vocabulary: `pass`, `fail`, `partial`, `blocked`, `question`, `na`.
- [ ] Absence is documented as a state — *"no entry"* is what "nobody has run it" looks like, and it is not a value.
- [ ] Minimal's characters and [[ADR-0034]]'s words are listed as **read-only legacy**, in a section that says so.
- [ ] Landed in `~/Dev/repos/project-os` first, then synced to all four repos — the drift is currently in every one of them, upstream included.

## Notes

Two judgements are already made in [[ADR-0037]] decision 6 and should not be re-opened here: `question` is kept (the source proposal drops it by omission, and it is the only signal that a *check* rather than a behaviour is wrong), and `rerun` is retired three weeks after being minted.

Measured 2026-08-19: `canceled`, `important`, `question` and `rerun` are each written **0 times** fleet-wide. The live vocabulary is `done` 546, `todo` 124, `incomplete` 1.
