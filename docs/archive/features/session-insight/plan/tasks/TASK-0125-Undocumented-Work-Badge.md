---
type: "[[task]]"
id: TASK-0125
aliases: ["TASK-0125"]
title: "Undocumented-work badge — live doc-traceability guardrail"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
parent: "[[FEAT-0022-Session-Insight-And-Traceability]]"
effort: "S"
depends: ["[[TASK-0123]]"]
blocks: []
related: []
tests: []
---

# Undocumented-work badge

## Definition of Done
- [ ] A live per-session rule flags sessions that edit source files (outside `docs/`) without touching any TASK/ISS/CHG note: amber badge on the workspace rail square and in the activity strip.
- [ ] Badge clears when a docs note is touched or the session ends with docs updates; informational only, never blocking.

## Steps
- [ ] Rule evaluation in the session accumulator (sidecar) → flag in state payload + SSE.
- [ ] Rail + strip badge rendering; clear conditions.
- [ ] Tests for the rule (docs-only session, mixed session, code-only session).

## Notes
Only possible because the cockpit knows the project-os contract — the differentiator feature of the phase.
