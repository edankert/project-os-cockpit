---
type: "[[task]]"
id: TASK-0182
aliases: ["TASK-0182"]
title: "Nest drill-down children by shared phase, so a task parked in another phase appears once under its own phase instead of duplicating or vanishing"
status: done
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-07-21
updated: 2026-09-07
source: ["[[ISS-0287]]"]
parent: "FEAT-0023"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[TASK-0181]]", "[[TASK-0177]]"]
tests: []
---

# Nest children by shared phase

*Reconstructed 2026-09-07 ([[ISS-0287]]). This note was committed as a **zero-byte file** on 2026-07-21 and stayed empty, so every citation of it resolved to nothing and it was absent from the snapshot and every count. What follows is taken from the delivering commit `15d732c` and from the issue it closed — nothing here is inferred beyond what those record.*

## What it did

The overview drills down from a phase to the items it carries. A task whose own `phase:` differs from its parent feature's had no single home in that tree: it could be rendered under both, or under neither, depending on which side of the join was walked. Children are grouped by the phase they *themselves* name, so each one appears exactly once — under its own phase — in both the project view and the per-phase view.

Landed in the same batch as [[TASK-0181]] (one shared `done` set behind the phase boxes and the hero counts) and [[TASK-0177]] (a clean fallback for phase-less projects), which is why the commit describes them together: all three are the overview disagreeing with itself about what belongs where.

## Verification

Carried by the batch's own review; no test note is claimed, because none was written at the time and inventing one now would be a false record.
