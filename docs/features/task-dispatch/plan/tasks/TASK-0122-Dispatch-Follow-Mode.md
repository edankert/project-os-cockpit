---
type: "[[task]]"
id: TASK-0122
aliases: ["TASK-0122"]
title: "Dispatch round-trip — focus hint + follow-mode integration"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
parent: "[[FEAT-0021-Task-Dispatch]]"
effort: "XS"
depends: ["[[TASK-0121]]"]
blocks: []
related: []
tests: []
---

# Dispatch round-trip

## Definition of Done
- [ ] Dispatch records the dispatched item as the workspace's agent-focus hint so follow mode and the activity strip surface the work immediately, before the agent's own focus/hook events arrive.

## Steps
- [ ] POST the dispatched target to `/api/cockpit/focus` (agent="dispatch") at dispatch time.
- [ ] Confirm the strip shows the item while the session spins up.

## Notes
Uses the existing focus channel — no new plumbing.
