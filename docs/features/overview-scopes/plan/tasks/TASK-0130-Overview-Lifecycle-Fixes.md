---
type: "[[task]]"
id: TASK-0130
aliases: ["TASK-0130"]
title: "Overview lifecycle fixes — history, refresh churn, fetch fan-out, live ticks"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
parent: "[[FEAT-0023-Overview-Scopes]]"
effort: "M"
depends: ["[[TASK-0129]]"]
blocks: []
related: ["[[TASK-0127]]"]
tests: []
---

# Overview lifecycle fixes

## Definition of Done
- [x] Overview is reachable via history: entering the mode navigates to the `~overview` virtual rel (scoped: `~overview/PHASE-####`); back/forward restore the exact scope.
- [x] File-change soft reloads refresh the mounted dashboard's data without losing scroll position (no full-churn rebuild).
- [x] One hook event → at most one `/api/cockpit/state` fetch shared by strip, Now card, and sessions surfaces (was three).
- [x] Live session durations/costs tick every 30s while a session is live.

## Steps
- [x] `~overview` branch in `navigateTo`; `setNavMode('overview')` routes through it.
- [x] Scroll-preserving `refreshOverviewInPlace()` on `file-changed`.
- [x] `refreshAgentSnapshot()` single-fetch fan-in; consumers subscribe.
- [x] 30s live tick timer.

## Notes
Fixes 1–5 from the 2026-07-06 Overview review (fix 6 lands with TASK-0128's cache).
