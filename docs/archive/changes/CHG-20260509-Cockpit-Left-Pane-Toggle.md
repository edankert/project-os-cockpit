---
type: "[[change]]"
id: CHG-20260509-Cockpit-Left-Pane-Toggle
aliases: ["CHG-20260509-Cockpit-Left-Pane-Toggle"]
title: "Cockpit: left-pane toggle (panel-left SVG) + bigger pane-toggle icons"
status: merged
owner: user:edwin
created: 2026-05-09
updated: 2026-05-09
source: ["[[TASK-0034]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/templates.py"
  - "src/project_os_cockpit/static/cockpit.js"
  - "src/project_os_cockpit/static/cockpit.css"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[CHG-20260509-Cockpit-Panel-Right-Icon]]", "[[CHG-20260509-Cockpit-Collapsible-Metadata-And-Right-Pane]]"]
---

# Cockpit: left-pane toggle + bigger pane-toggle icons

## Summary
Mirrors the right-pane toggle for the left navigator pane: a Lucide `panel-left-close` / `panel-left-open` SVG button at the far-left of page-header row 1, persisted state via localStorage, `.cockpit.left-collapsed` grid override that drops the first column. Both pane-toggle icons grow from 16px to 20px. With both panes collapsed the centre fills the entire cockpit (single-column layout).

## Impact

### `templates.py`
- Page-header row 1 order: `left-toggle-slot → home-link → mode-slot → platform-slot → filter-slot → theme-toggle → right-toggle-slot`.

### `cockpit.js`
- New `LEFT_PANE_KEY` (`project-os-cockpit.cockpit.left-pane-collapsed`).
- New `loadLeftPaneCollapsed` / `saveLeftPaneCollapsed` helpers + `leftPaneCollapsed` module state.
- Lucide path constants added: `PANEL_LEFT_CLOSE_PATHS`, `PANEL_LEFT_OPEN_PATHS`.
- Refactored SVG construction into `panelIconSvg(klass, paths)`; existing `panelRightIconSvg` and new `panelLeftIconSvg` are thin wrappers. SVG `width`/`height` bumped 16 → 20.
- New `applyLeftPaneState` and `mountLeftPaneToggle` (mirrors of the right-pane equivalents).
- Boot order updated to mount + apply the left toggle before the right.

### `cockpit.css`
- New rules: `.cockpit.left-collapsed { grid-template-columns: minmax(0, 1fr) 340px; }` and `.cockpit.left-collapsed .cockpit-left { display: none; }`.
- New combo rule: `.cockpit.left-collapsed.right-collapsed { grid-template-columns: minmax(0, 1fr); }` — both panes hidden gives a single-column centre.
- `.cockpit-left-toggle-slot` mirrors the right slot, with `margin-right: 8px`.
- `.left-pane-toggle` and `.left-pane-icon` folded into the existing `.right-pane-toggle` / `.panel-right-icon` rules via comma-separated selectors.

### Tests
- 50 cases passing / 1 skipped — no test asserted slot count or icon size.

### Verified
- `curl /docs/.../FEAT-0001-...md` confirms the new `<div id="cockpit-left-toggle-slot">` is present at the start of header row 1.
- Toggling left + right independently leaves the centre pane reflowing through 3-col / 2-col / 1-col layouts.

## Documentation Coverage (All Types Considered)
- features: not-applicable
- requirements: not-applicable
- tasks: new ([[TASK-0034]])
- issues: not-applicable
- tests: not-applicable
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 33→34, focus.task → TASK-0034, metrics tasks_total 33→34 / tasks_done 27→28, items.changes addition)
