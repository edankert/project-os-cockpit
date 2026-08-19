---
type: "[[task]]"
id: TASK-0534
aliases: ["TASK-0534"]
title: "The release gate reads the shipping platform's ledger, and the delta is stated per repo before it lands"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0135-Everything-Downstream-Is-A-Query]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The gate

## Definition of Done

- [ ] `Suite.blocking_for(subjects)` takes its settled-ness from the ledger for the release's platform.
- [ ] No entry, `fail`, `blocked` or `question` blocks. `pass`, `partial` and `na` clear, and so does an `excused` belonging to **this** release.
- [ ] `blocked` blocking is deliberate and tested: `na`/`excused` are decisions about this release, `blocked` is an accident that will be gone next week ([[ADR-0037]] decision 6).
- [ ] A release with no platform reads every platform's ledger and is blocked by any of them — the same opt-in rule [[DES-0012]] D4 gives release contents.
- [ ] The delta against today's gate is computed per repo and recorded before that repo migrates.

## Notes

**This does not touch `tier:`.** [[ISS-0208]] owns the tier filter and the fail-closed clause, and both are orthogonal to where the verdict is stored. Folding them together would make one open issue impossible to reason about — the same reason [[PHASE-037]] refused the gate question.

The delta is the whole risk of this phase. `your-trainer`'s iOS position gets much worse on paper, because it was always that bad and the schema could not say so.
