---
type: "[[task]]"
id: TASK-0223
aliases: ["TASK-0223"]
title: "Brief payload and the identity band"
status: backlog
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["[[FEAT-0043-Design-Top-Level-Surface]]"]
parent: "[[FEAT-0043-Design-Top-Level-Surface]]"
effort: "M"
depends: ["[[TASK-0222]]"]
blocks: ["[[TASK-0224]]"]
related: []
tests: []
---

# Brief payload and identity band

## Definition of Done

- [ ] A sidecar payload reads `LLM_BRIEF.md` — identity (name, purpose), high-value paths, invariants
- [ ] The payload flags a brief that is **absent**, **unfilled**, or **filled**, as three distinct states
- [ ] The surface renders the identity band first: what this is, who for, its shape
- [ ] An unfilled brief renders a prompt to fill it, **never the placeholder text**
- [ ] An absent brief degrades to the design system alone rather than an error
- [ ] The band links to the file so editing is one click, and the file remains the source

## Steps

- [ ] Parse the brief's known sections tolerantly — a hand-edited brief must not break the surface
- [ ] Three-state detection with tests for each
- [ ] Build the band
- [ ] Verify against this repo's real brief

## Notes

Parsing must be **tolerant**. The brief is prose a human edits, not a data file: a missing section, a reordered one, or an added heading are all normal and none may break the surface. Read what is recognised, ignore the rest, and never fail closed on a file whose whole purpose is being hand-written.

Three states, not two, because "no brief" and "brief that says REPLACE ME" call for different things — one is a project that has not adopted the convention, the other is a project that adopted it and stopped.
