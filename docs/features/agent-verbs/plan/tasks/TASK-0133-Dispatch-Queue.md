---
type: "[[task]]"
id: TASK-0133
aliases: ["TASK-0133"]
title: "Dispatch queue — enqueue when busy, auto-type on Stop/SessionEnd"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
parent: "[[FEAT-0024-Agent-Verbs]]"
effort: "M"
depends: ["[[TASK-0132]]"]
blocks: []
related: ["[[TASK-0114]]"]
tests: []
---

# Dispatch queue

## Definition of Done
- [x] Dispatching while the workspace agent is busy/needs-input enqueues (per-workspace, in-memory) with a toast; direct dispatch otherwise.
- [x] Delivery state machine driven by the hook feed: live session at `Stop` (waiting) → queued prompt typed into the REPL; `SessionEnd`/idle → fresh `claude`/`codex` shell command.
- [x] Activity strip shows a queue chip with count; clicking it clears the queue (toast confirms).

## Steps
- [x] Queue map + enqueue path in `dispatchToAgent`.
- [x] Deliver-on-transition via the `cockpit:agent-state` SSE listener.
- [x] Strip chip + clear affordance.

## Notes
The REPL-vs-shell distinction matters: after `Stop` the interactive CLI is still open, so a shell command would be swallowed as conversation text — the queue types the raw prompt there instead.
