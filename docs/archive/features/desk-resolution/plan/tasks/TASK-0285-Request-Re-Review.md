---
type: "[[task]]"
id: TASK-0285
aliases: ["TASK-0285"]
title: "Request re-review from a changes-requested row — the reviewer dispatched with the note and its prior findings"
status: cancelled
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0062-Desk-Resolution-Flows]]"]
parent: "[[FEAT-0062-Desk-Resolution-Flows]]"
effort: M
depends: []
blocks: []
related: []
tests: []
---

# Request re-review

## Definition of Done

- Every changes-requested register row offers `Request re-review`; the dispatch names the note, the verdict being answered, and where the findings live.
- A pending re-review is visible on the row (and the action disabled with that reason) until a new verdict lands.
- A new verdict moves the row out of changes-requested through the existing register logic — no new state machine.
