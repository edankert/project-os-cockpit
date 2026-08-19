---
type: "[[task]]"
id: TASK-0539
aliases: ["TASK-0539"]
title: "Settle the outcome vocabulary in `TAXONOMY.md` upstream — one table, matching the data, legacy readable but not current"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0137-One-Outcome-Vocabulary-Written-Down-Once]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# One table

## Definition of Done

- [ ] `TAXONOMY.md`'s `mark` section is rewritten as the ledger's outcome vocabulary: `pass`, `partial`, `na`, `excused`, `blocked`, `fail`, `question` — with the gate column **and** the persists-past-the-seal column, because the second is what separates `na` from `excused`.
- [ ] Absence is documented as a state — *"no entry"* is what "nobody has run it" looks like, and it is not a value.
- [ ] Minimal's characters and [[ADR-0034]]'s words are listed as **read-only legacy**, in a section that says so.
- [ ] Landed in `~/Dev/repos/project-os` first, then synced to all four repos — the drift is currently in every one of them, upstream included.

## Done here 2026-08-19, and NOT yet upstream

`TAXONOMY.md`'s `mark` section is now **Acceptance outcomes** — seven values with a gate column *and* a survives-the-seal column, because the second is what separates `na` from `excused`. Absence is documented as a state rather than a value. Both legacy vocabularies are listed under a heading that says they are read and never written, with the mapping into the ledger and the written rule that **`canceled` → `na`, never `excused`**.

**The upstream copy is not done and this task stays open until it is.** `tools/instructions/` is template-owned; landing it here first is the wrong order ([[ADR-0030]] decision 6) and it is recorded rather than quietly accepted. It is one file copy plus a sync, and it must not go into `your-trainer` or `your-sudoku` blind — both are a schema generation behind ([[ISS-0217]]).

## Notes

Three judgements are already made in [[ADR-0037]] decision 6 and should not be re-opened here: `question` is kept (the source proposal drops it by omission, and it is the only signal that a *check* rather than a behaviour is wrong); `rerun` is retired three weeks after being minted; and *not run* splits into three — `na` (cannot apply here, persists), `excused` (not done this cycle, expires at the seal) and `blocked` (could not run it right now, **blocks**).

Measured 2026-08-19: `canceled`, `important`, `question` and `rerun` are each written **0 times** fleet-wide. The live vocabulary is `done` 546, `todo` 124, `incomplete` 1.
