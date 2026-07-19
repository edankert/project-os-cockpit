---
type: "[[task]]"
id: TASK-0033
aliases: ["TASK-0033"]
title: "Cockpit: right-pane toggle uses Obsidian-style panel-right SVG, moved to far right"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-09
updated: 2026-05-23
source: []
parent: "[[FEAT-0006]]"
fixes: []
effort: XS
due: ""
depends: ["[[TASK-0032]]"]
blocks: ["[[TASK-0034]]"]
related: []
tests: []
---

# TASK-0033 — Panel-right SVG icon at far right

## Definition of Done
- [x] Right-pane toggle button uses inline SVGs matching Lucide's `panel-right-close` (open state) and `panel-right-open` (collapsed state) — same shape Obsidian uses for its sidebar toggle.
- [x] The button slot moves to after the theme-toggle button so it's the rightmost control on row 1 of the page header.
- [x] Existing toggle behaviour and persistence stay the same.

## Steps
- [x] Templates (`templates.py`): swapped the slot order — `theme-toggle` now precedes `cockpit-right-toggle-slot`.
- [x] JS (`cockpit.js`): added `PANEL_RIGHT_CLOSE_PATHS` / `PANEL_RIGHT_OPEN_PATHS` constants + `panelRightIconSvg(collapsed)` helper. `mountRightPaneToggle` appends the SVG element instead of setting `textContent`. The click handler swaps the SVG via `replaceChildren`.
- [x] CSS (`cockpit.css`): updated `.right-pane-toggle` to a flex centre with no border (icon button look), `padding: 4px`, hover background. Slot's `margin-right: 8px` switched to `margin-left: 8px` to space it from the theme button.

## Notes
Chevron direction follows Obsidian convention: pane open → arrow points inward (click → close); pane closed → arrow points outward (click → open).
