---
type: "[[task]]"
id: TASK-0149
aliases: ["TASK-0149"]
title: "Rate-limit pip in the agent strip — surface the 5h budget already collected"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
parent: "FEAT-0031"
effort: ""
due: ""
depends: []
blocks: []
related: []
tests: []
---

# TASK-0149 — rate-limit pip

The tracker already stores `cost.rate_limits.five_hour/seven_day` (used %, resets_at) from the statusline; nothing renders it. Add a strip pip `5h N%` (tooltip: reset time + 7d figure), `.meter-hot` ≥ 80% — the number to check before dispatching more work. Verification: statusline fixture with rate_limits → pip renders, hot threshold styles, absent data → pip hidden.
