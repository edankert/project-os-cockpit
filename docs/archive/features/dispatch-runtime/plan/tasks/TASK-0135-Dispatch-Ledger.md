---
type: "[[task]]"
id: TASK-0135
aliases: ["TASK-0135"]
title: "Dispatch ledger — record, session stamping, provenance UI"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
parent: "[[FEAT-0025-Dispatch-Runtime]]"
effort: "M"
depends: []
blocks: []
related: []
tests: ["[[TST-0014]]"]
---

# Dispatch ledger

## Definition of Done
- [x] `POST /api/cockpit/dispatch` records `{id, verb, agent}`; pending dispatches stamp the next session that starts; sessions expose `dispatches`.
- [x] `/api/render` gains `dispatch_history` for dispatchable notes (verb, agent, ts, session id, live flag).
- [x] Renderer: provenance line on dispatched notes, "← verb ID" on session rows, warning when re-dispatching a note whose dispatch is live.
