---
type: "[[change]]"
id: CHG-20260509-Cockpit-Panel-Right-Icon
aliases: ["CHG-20260509-Cockpit-Panel-Right-Icon"]
title: "Cockpit: right-pane toggle uses Obsidian-style panel-right SVG, moved to far right"
status: merged
owner: user:edwin
created: 2026-05-09
updated: 2026-05-09
source: ["[[TASK-0033]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/templates.py"
  - "src/project_os_cockpit/static/cockpit.js"
  - "src/project_os_cockpit/static/cockpit.css"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[CHG-20260509-Cockpit-Collapsible-Metadata-And-Right-Pane]]"]
---

# Cockpit: panel-right SVG + far-right placement

## Summary
The right-pane toggle (added in TASK-0032) used `⇤/⇥` text glyphs which read inconsistently across fonts. Swapped for inline Lucide SVGs — `panel-right-close` (chevron pointing inward) when the pane is open, `panel-right-open` (chevron outward) when collapsed — same shape Obsidian uses for its sidebar toggle. The button slot also moves to after the theme toggle so it's the rightmost control on row 1.

## Impact

### `templates.py`
- Slot order on page-header row 1: `home-link → mode-slot → platform-slot → filter-slot → theme-toggle → right-toggle-slot`. (Was `… → right-toggle-slot → theme-toggle`.)

### `cockpit.js`
- New `PANEL_RIGHT_CLOSE_PATHS` / `PANEL_RIGHT_OPEN_PATHS` constants (Lucide path strings).
- New `panelRightIconSvg(collapsed)` helper builds an inline `<svg>` element with `currentColor` stroke.
- `mountRightPaneToggle` builds the button without text content and appends the SVG; click handler swaps the SVG via `replaceChildren`.

### `cockpit.css`
- `.right-pane-toggle` switched from a bordered pill to a flex icon button (no border, transparent → muted hover bg, `padding: 4px`, `line-height: 0`).
- `.cockpit-right-toggle-slot` `margin-right: 8px` → `margin-left: 8px` to space it from the theme button (it's now to its right).
- New `.panel-right-icon { display: block; }` to suppress the inline SVG baseline gap.

### Tests
- 50 cases passing / 1 skipped — no test asserted the slot order or button glyph.

### Verified
- The right-pane toggle now appears as the last control on row 1, with the rectangle-and-chevron Lucide icon. State persists from TASK-0032 unchanged.

## Documentation Coverage (All Types Considered)
- features: not-applicable
- requirements: not-applicable
- tasks: new ([[TASK-0033]])
- issues: not-applicable
- tests: not-applicable
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 32→33, focus.task → TASK-0033, metrics tasks_total 32→33 / tasks_done 26→27, items.changes addition)
