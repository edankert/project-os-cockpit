---
type: "[[task]]"
id: TASK-0136
aliases: ["TASK-0136"]
title: "cockpit dispatch CLI — queue work from any terminal"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
parent: "[[FEAT-0025-Dispatch-Runtime]]"
effort: "S"
depends: []
blocks: []
related: []
tests: ["[[TST-0014]]"]
---

# cockpit dispatch CLI

## Definition of Done
- [x] `cockpit dispatch <ID> [--verb v] [--agent a]` posts a queue-request; requests persist sidecar-side.
- [x] Desktop picks requests up via SSE (open workspace) and fetch-on-attach (others), resolves the verb template, and runs the normal execute path.
