---
type: "[[task]]"
id: TASK-0034
aliases: ["TASK-0034"]
title: "Cockpit: left-pane toggle (panel-left SVG) at far left, bigger icons (16→20px)"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-09
updated: 2026-05-09
source: []
implements: ["[[FEAT-0006]]", "[[REQ-0012]]"]
fixes: []
effort: XS
due: ""
depends: ["[[TASK-0033]]"]
blocks: []
related: []
tests: []
---

# TASK-0034 — Left-pane toggle + bigger icons

## Definition of Done
- [x] Left navigator pane has a header toggle on the **far left** of row 1, mirroring the right-pane toggle on the far right.
- [x] Uses Lucide's `panel-left-close` (open state) / `panel-left-open` (collapsed state) SVGs.
- [x] Toggling sets `.cockpit.left-collapsed` which drops the first grid column and lets the centre/right reflow. Both panes can be collapsed simultaneously — `.cockpit.left-collapsed.right-collapsed` gives a single-column layout.
- [x] State persists in localStorage under `project-os-cockpit.cockpit.left-pane-collapsed`.
- [x] Both pane-toggle icons bumped from 16px to 20px.

## Steps
- [x] Templates (`templates.py`): added `<div id="cockpit-left-toggle-slot">` as the first child of page-header row 1 (before the home-link).
- [x] JS (`cockpit.js`):
  - New `LEFT_PANE_KEY` localStorage key.
  - `loadLeftPaneCollapsed` / `saveLeftPaneCollapsed` helpers.
  - Refactored the SVG builder to a shared `panelIconSvg(klass, paths)` factory; new `panelLeftIconSvg(collapsed)` and `panelRightIconSvg(collapsed)` wrappers.
  - SVG width/height bumped 16 → 20.
  - `applyLeftPaneState()` toggles `.cockpit.left-collapsed`; `mountLeftPaneToggle()` builds the button. Both wired into boot.
- [x] CSS (`cockpit.css`):
  - `.cockpit.left-collapsed` grid override (drops 1st column) + hide `.cockpit-left`.
  - `.cockpit.left-collapsed.right-collapsed` → single-column layout.
  - `.cockpit-left-toggle-slot` `margin-right: 8px`.
  - `.left-pane-toggle` rules folded into the existing `.right-pane-toggle` block via comma-separated selectors.

## Notes
The left-toggle sits before the home-link visually, so the row order is now:
`left-toggle → home-link → mode-tabs → platform → filter → theme-toggle → right-toggle`. Symmetric.
