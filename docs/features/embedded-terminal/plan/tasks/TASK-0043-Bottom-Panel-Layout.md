---
type: "[[task]]"
id: TASK-0043
aliases: ["TASK-0043"]
title: "Cockpit: bottom-panel layout in centre column (resizer + collapse + persisted height)"
status: backlog
phase: "[[PHASE-004-Embedded-Terminal]]"
owner: user:edwin
created: 2026-05-22
updated: 2026-05-22
source: []
implements: ["[[FEAT-0003]]"]
fixes: []
effort: S
due: ""
depends: []
blocks: ["[[TASK-0044]]", "[[TASK-0045]]"]
related: []
tests: []
---

# TASK-0043 — Bottom-panel layout

## Goal
Carve out a bottom sub-pane inside the centre column (between left + right panes) that will host the embedded terminal (TASK-0044) and the preview tab (TASK-0045). Left + right panes stay full-height; only the centre column splits vertically.

## Definition of Done
- [ ] New `.cockpit-centre-column` wrapper around `.cockpit-centre` + the new `.cockpit-bottom-panel`. Centre column is a vertical flex container.
- [ ] Bottom panel has a small header strip (~24px) with: panel-title tab(s), collapse toggle. Stays visible even when content is collapsed.
- [ ] Default height: 280px. Default state: collapsed.
- [ ] Resizer: 4px-high draggable splitter between centre and bottom panel; drag to resize; persist height in localStorage.
- [ ] Collapse: clicking the header toggle hides the body, leaves the strip visible. Persisted.
- [ ] Centre pane keeps its `overflow-y: auto`; its scroll position survives toggle / resize.
- [ ] No regressions on the existing 3-pane layout: left/right pane behaviour unchanged.
- [ ] Works correctly with the existing left/right pane toggles (TASK-0032..0034) — bottom panel doesn't reflow when side panes collapse, but bottom panel itself stretches across the freed centre-column width.

## Steps
- [ ] Templates: wrap `.cockpit-centre` in `.cockpit-centre-column` with the new `.cockpit-bottom-panel` as a sibling.
- [ ] CSS: vertical flex on `.cockpit-centre-column`; centre = `flex: 1 1 auto`; bottom panel = `flex: 0 0 auto`; resizer styling.
- [ ] JS: `mountBottomPanelResizer()` + `mountBottomPanelToggle()`. Persist `BOTTOM_PANEL_HEIGHT_KEY` and `BOTTOM_PANEL_COLLAPSED_KEY`.
- [ ] JS: shell-only tabs (placeholders) for "Terminal" and "Preview" — actual content populated in TASK-0044 and TASK-0045.

## Notes
- Requirement amendment: REQ-0013 today specifies a 3-pane layout. This task introduces a 4th surface (bottom panel inside centre column). Either amend REQ-0013 or add a sibling REQ.
- The bottom-panel header strip remains visible even when content is collapsed so the user can reopen it without remembering where it lives. Same UX as VS Code's terminal.
- Pre-condition for TASK-0044 (ttyd) and TASK-0045 (preview), which both render into this panel.
