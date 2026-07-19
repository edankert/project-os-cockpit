---
type: "[[task]]"
id: TASK-0026
aliases: ["TASK-0026"]
title: "Cockpit: default nav items use stacked layout (id+status row 1, title row 2, subtitle row 3)"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-09
updated: 2026-05-09
source: []
parent: "[[FEAT-0006]]"
fixes: []
effort: S
due: ""
depends: ["[[TASK-0025]]"]
blocks: []
related: []
tests: ["[[TST-0002]]"]
---

# TASK-0026 — Default nav items use stacked layout

## Definition of Done
- [x] `navItem` (Features / Tasks / Issues / Recent) renders three rows: row 1 `[icon] [id (mono, ellipsis when long)] [spacer] [status]`; row 2 `[title]`; row 3 `[subtitle]` when present.
- [x] `.nav-id` ellipsises gracefully when an id like `CHG-20260509-Cockpit-Stacked-Items-Right-Pane-Order-And-Group-Icons` would otherwise overflow.
- [x] Subtitle still renders (Features `goal`, Tasks `parent · effort`, Issues `affects · component`, Recent `type · date`).
- [x] Active and hover states still color the title — the duplicated `.nav-item.is-active .nav-title` rule was consolidated.

## Steps
- [x] Restructured `navItem` in `cockpit.js`.
- [x] Updated `.nav-id` and `.nav-title` rules in `cockpit.css` (id ellipsis, title now a row-2 paragraph with 2-line clamp).
- [x] Removed the duplicate `.nav-item.is-active .nav-title` rule from line ~307.
- [x] Tests pass — no test asserted the single-line layout, so no rewrite needed.

## Notes
This converges `navItem` and `navItemStacked` visually except that `navItem` may carry a row-3 subtitle. Pinned + rare-types (stacked) don't.
