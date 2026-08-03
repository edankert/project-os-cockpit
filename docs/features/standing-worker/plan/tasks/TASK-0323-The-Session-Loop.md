---
type: "[[task]]"
id: TASK-0323
aliases: ["TASK-0323"]
title: "The session loop — dispatch through the instrumented terminal, watch to close-out or failure, record, next"
status: backlog
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0074-The-Standing-Worker]]"]
parent: "[[FEAT-0074-The-Standing-Worker]]"
effort: L
depends: ["[[TASK-0322-Selection-With-Reasons]]"]
blocks: []
related: []
tests: []
---

# The session loop

## Definition of Done

- The driver dispatches the selected item into a shell-instrumented session (the existing spawn + hooks path) and watches the same lifecycle events the agents strip reads.
- Outcomes recorded per session: closed-out clean / failed / stalled; a stalled session past its budget is ended and recorded as such, never abandoned running.
- The loop continues to the next selection only after the outcome is recorded and the lease heartbeat is current.
