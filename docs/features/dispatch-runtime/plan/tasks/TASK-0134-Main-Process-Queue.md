---
type: "[[task]]"
id: TASK-0134
aliases: ["TASK-0134"]
title: "Main-process dispatch queue — persisted, workspace-independent delivery"
status: doing
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
parent: "[[FEAT-0025-Dispatch-Runtime]]"
effort: "M"
depends: []
blocks: []
related: []
tests: ["[[TST-0011]]"]
---

# Main-process dispatch queue

## Definition of Done
- [x] `dispatch:execute` IPC in main decides enqueue-vs-deliver from the workspace's last known agent state; queues persisted under userData and restored on launch.
- [x] Delivery fires on agent-state transitions for ANY workspace (poller hook + SSE-fed fast path for the active one), typing into that workspace's own PTY (REPL mode after Stop with a live session, shell command otherwise, single-quote escaped).
- [x] `dispatch:queue-changed` fans to all windows; renderer popover lists items with per-item remove + clear.
