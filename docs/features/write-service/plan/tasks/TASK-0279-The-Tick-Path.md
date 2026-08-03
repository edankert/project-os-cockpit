---
type: "[[task]]"
id: TASK-0279
aliases: ["TASK-0279"]
title: "Ticking a criterion rewrites one line, in the validator's own shapes, with a witness"
status: backlog
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0059-The-Write-Service-Widens]]"]
parent: "[[FEAT-0059-The-Write-Service-Widens]]"
effort: M
depends: ["[[TASK-0278-The-Transition-Table-As-Data]]"]
blocks: []
related: ["[[REQ-0028-Evidence-Names-Its-Witness]]"]
tests: []
---

# The tick path

## Definition of Done

- `POST /api/notes/tick`: locates the criterion by exact text within the criteria section, rewrites that line only.
- Both forms: `- [x] … — evidence: <text> (user:…, date)` and `- [~] … — <reason>`, matching what REQ-BOXES/PHASE-BOXES parse — proven by running the real validator over a ticked fixture.
- mtime precondition: a note edited since render refuses the tick loudly.
- Ambiguous or missing criterion text is a 4xx; nothing is written.
