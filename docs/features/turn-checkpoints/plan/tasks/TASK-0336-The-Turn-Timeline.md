---
type: "[[task]]"
id: TASK-0336
aliases: ["TASK-0336"]
title: "The turn timeline — each turn with the shape of what it changed, so the wrong turn is findable"
status: backlog
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-05
source: ["[[FEAT-0078-Turn-Checkpoints]]"]
parent: "[[FEAT-0078-Turn-Checkpoints]]"
effort: M
depends: ["[[TASK-0335-Capture-Per-Turn]]"]
blocks: ["[[TASK-0337-Restore-As-A-Recorded-Action]]"]
related: ["[[ISS-0096-No-Surface-Says-What-Changed]]"]
tests: []
---

# The turn timeline

## Definition of Done

- A session's turns list with, per turn, the files touched grouped by kind and the counts — the same shape [[ISS-0096]] defines, computed between adjacent checkpoints, and sharing its implementation rather than growing a second one.
- The row says what the turn was *for* where the ledger knows it (the dispatched item), so a timeline reads as work rather than as diffs.
- Absent checkpoints, the surface says so plainly instead of rendering an empty list.
