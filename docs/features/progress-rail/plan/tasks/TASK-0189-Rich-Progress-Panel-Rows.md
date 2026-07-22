---
type: "[[task]]"
id: TASK-0189
aliases: ["TASK-0189"]
title: "Progress panel — rich recency-ordered rows (block + id + title + from→to + relative time, active item pinned)"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-22
updated: 2026-07-22
source: ["[[REQ-0021]]"]
parent: "FEAT-0038"
effort: ""
due: ""
depends: ["[[TASK-0188]]"]
blocks: []
related: ["[[TASK-0163]]"]
tests: []
verification_waiver: "Renderer-only UI; no automated renderer unit-test surface. Validated live via CDP against a real agent session (render across all note types, live block fill on a driven transition, panel enrichment, chevron/rename); independent review on the code."
---

# TASK-0189 — rich progress panel rows

Replace the minimal work-tab rows (generic box + bare id + latest status word) with rich rows in the chosen design: `.ov-phase-sq` block (same type colour/fill as the rail) + id + note title + status transition (`from → to`, or just the current status when no transition happened this session) + relative time of last activity ("now", "4m", "1h"). Order rows by most recent activity, with the currently-active item pinned to the top and pulsed. Include CHG notes as they are created. Foundation: extend `workTransitions` from `id → status-string` to `id → {from, to, ts, title}` — the `cockpit:status-change` payload already carries all four fields; add a small relative-time helper. Items untouched by any transition this session fall back to bare id (or seed titles from `/api/cockpit/transitions` if cheap). Rows keep click-to-navigate.

Verification: trigger a status change while the panel is open — the row shows the from→to transition, moves to the top, and its time reads "now"; a CHG note created mid-session appears as a row; row click opens the note.

## Verification

Extended `workTransitions` to `{from,to,ts,title}` from the `cockpit:status-change` payload; the progress panel renders rich rows (block + id + title + `from → to` + relative time) ordered by recency with the active item pinned to the top. Verified live: a transitioned item showed its `from → to` text, time `now`, and rowIndex 0. tsc clean.
