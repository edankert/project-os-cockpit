---
type: "[[task]]"
id: TASK-0334
aliases: ["TASK-0334"]
title: "Delegated acceptance — the runner with agent:principal as witness, charter in context, worker kept at arm's length"
status: backlog
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0077-The-Intent-Charter]]"]
parent: "[[FEAT-0077-The-Intent-Charter]]"
effort: L
depends: ["[[TASK-0333-The-Charter-Note]]"]
blocks: []
related: ["[[REQ-0029-A-Delegate-Is-Always-Distinguishable]]"]
tests: []
---

# Delegated acceptance

## Definition of Done

- A delegated run is FEAT-0063's runner driven by a principal-agent session: clean context (never the worker's session or its reasoning trace — ADR-0013's standard), the approved charter in context, judging against criteria by using the product where the criteria demand it.
- Every tick's witness is `agent:principal` with charter and delegation shas; `accepted_by` distinguishes delegate from human at a glance (REQ-0029).
- Fails file issues exactly as human runs do; the digest lifts delegate-accepted features for the human's spot-check — supervision is reading.
