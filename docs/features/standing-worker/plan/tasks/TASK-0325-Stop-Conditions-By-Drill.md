---
type: "[[task]]"
id: TASK-0325
aliases: ["TASK-0325"]
title: "Stop conditions proven by drill — budget, backoff, validator red, and the human's stop switch"
status: backlog
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0074-The-Standing-Worker]]"]
parent: "[[FEAT-0074-The-Standing-Worker]]"
effort: M
depends: ["[[TASK-0323-The-Session-Loop]]"]
blocks: []
related: ["[[REQ-0031-The-Loop-Always-Halts]]"]
tests: []
---

# Stop conditions, by drill

## Definition of Done

- Implemented: daily session and wall-clock budgets; two failed close-outs park an item with an issue; three parked items halt; validator red beyond the session halts; the landing card's stop switch halts now.
- Halting files what-and-why into the queue — a halted worker is an obligation on the desk, not an absence.
- **Each condition exercised in a drill**, the drill logged in the feature note — the PHASE-022 rule that a guard unbroken is a guard unbelieved, applied to autonomy's brakes before they are needed in anger.
