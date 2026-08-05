---
type: "[[task]]"
id: TASK-0337
aliases: ["TASK-0337"]
title: "Restore to a turn — a principal-owned action, recorded, with the conversation caveat stated where it is offered"
status: backlog
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-05
source: ["[[FEAT-0078-Turn-Checkpoints]]"]
parent: "[[FEAT-0078-Turn-Checkpoints]]"
effort: M
depends: ["[[TASK-0336-The-Turn-Timeline]]"]
blocks: []
related: ["[[REQ-0026-Only-Human-Owned-Transitions]]", "[[ADR-0009-The-Principal-Is-A-Role]]"]
tests: []
---

# Restore as a recorded action

## Definition of Done

- Restore is offered through the actuator row's grammar and is **principal-owned** — a worker can never rewind itself ([[ADR-0009]]); the endpoint refuses a worker identity as firmly as it refuses an agent-owned transition.
- Before restoring, the current state is itself captured, so a restore is never the end of a road.
- The action records what was restored and why, and the affected item gains an issue when the restore implies work was undone — a rewind that leaves no trace is indistinguishable from work that never happened.
- The offer states plainly that files move and conversation does not.
