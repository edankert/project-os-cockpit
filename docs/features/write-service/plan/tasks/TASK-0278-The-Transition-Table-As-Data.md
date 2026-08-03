---
type: "[[task]]"
id: TASK-0278
aliases: ["TASK-0278"]
title: "The human-owned transition table as one data structure, and the endpoint that consults it"
status: backlog
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0059-The-Write-Service-Widens]]"]
parent: "[[FEAT-0059-The-Write-Service-Widens]]"
effort: M
depends: []
blocks: ["[[TASK-0279-The-Tick-Path]]"]
related: ["[[DES-0005-The-Actuator-Grammar]]"]
tests: []
---

# The transition table as data

## Definition of Done

- One dict in `note_writes.py`, beside `DECIDE_TRANSITIONS`, mapping (type, from-status) → the actions a human may take, exactly [[DES-0005]]'s matrix.
- `POST /api/notes/transition` performs one; `GET /api/notes/actions` reports what is legal (with `disabled`+`reason` where a gate blocks) so the renderer never restates vocabulary.
- Every status named in the table exists in `statuses.py`; guarded by a vocabulary test in the ISS-0023 style.
- An agent-owned transition in the request is a 4xx naming the ownership rule.
