---
type: "[[task]]"
id: TASK-0139
aliases: ["TASK-0139"]
title: "Type-from-data + hardening — data attrs, agent-mismatch warning, dead code"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
parent: "[[FEAT-0026-Verb-Polish]]"
effort: "S"
depends: []
blocks: []
related: []
tests: []
---

# Type-from-data + hardening

## Definition of Done
- [x] Nav rows carry `data-type`/`data-status`; verb resolution prefers row data over ID-prefix guessing so custom `actions.yaml` types surface.
- [x] REPL delivery warns when the live session's agent differs from the chosen one.
- [x] FEAT-0024 first-cut dead code removed (`agentSessionBusy`, unused branches).
