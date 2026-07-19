---
type: "[[task]]"
id: TASK-0152
aliases: ["TASK-0152"]
title: "Hook ingestion dedup — one event, one record, whichever capture paths fire"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
parent: "FEAT-0033"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[FEAT-0019-Agent-Hook-Ingestion]]", "[[FEAT-0027-External-Session-Signal]]"]
tests: []
---

# TASK-0152 — ingestion dedup

A cockpit-terminal session with the external hook enabled fires both capture paths into the same sidecar; there is no dedup key, so prompts append twice (live evidence: your-sudoku's session index, every prompt duplicated ~60–130ms apart) and activity SSE doubles. Fix in `AgentSessionTracker.ingest()`: drop an event whose `(session_id, hook_event_name, payload-hash)` was seen within a short window (~2s); alternatively investigate marking instrumented sessions so the external hook stands down. Regression test seeded with the observed double-capture pattern; retro-clean is not needed (indexes roll over at 50 sessions).
