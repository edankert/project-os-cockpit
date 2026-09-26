---
type: "[[change]]"
id: CHG-20260509-Cockpit-Collapsible-Metadata-And-Right-Pane
aliases: ["CHG-20260509-Cockpit-Collapsible-Metadata-And-Right-Pane"]
title: "Cockpit: collapsible frontmatter card + collapsible right pane"
status: merged
owner: user:edwin
created: 2026-05-09
updated: 2026-05-09
source: ["[[TASK-0032]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/templates.py"
  - "src/project_os_cockpit/static/cockpit.js"
  - "src/project_os_cockpit/static/cockpit.css"
  - "src/project_os_cockpit/static/base.css"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[REQ-0013]]"]
---

# Cockpit: collapsible frontmatter + right pane

## Summary
Two persisted UI affordances:

1. **Frontmatter card** rendered on each note now collapses on click. Server emits `<details open>` with a small "Frontmatter" summary row + chevron. Client-side JS strips the `open` attribute when the user previously collapsed it; toggling persists. State carries over across client-side navigation (centre-pane swap), not just page reloads.

2. **Right (relationships) pane** has a header toggle (`⇥` to hide, `⇤` to show). Clicking sets `.cockpit.right-collapsed`, which drops the 3rd column and lets the centre pane reflow. Persisted across reloads.

## Impact

### Server (`templates.py`)
- `_metadata_strip_html` switched from `<aside class="metadata-strip"><dl>...</dl></aside>` to `<details class="metadata-strip" open><summary class="metadata-strip-summary">…</summary><dl>...</dl></details>`. Existing CSS hooks on `.metadata-strip` continue to apply.
- Added `<div id="cockpit-right-toggle-slot">` to row 1 of the page header (after the filter slot, before the theme toggle).
- Home-page focus block (`<aside class="metadata-strip">` for synthetic landing) intentionally not converted — different context, already wrapped under an `<h2>`.

### Client (`cockpit.js`)
- New `META_STRIP_KEY` and `RIGHT_PANE_KEY` localStorage keys.
- New helpers: `loadMetaStripCollapsed` / `saveMetaStripCollapsed`, `loadRightPaneCollapsed` / `saveRightPaneCollapsed`.
- `applyMetaStripState()` strips `open` when collapsed; wires a `toggle` listener once per element (`_metaWired` flag) so re-applying after navigation doesn't accumulate handlers.
- `applyRightPaneState()` toggles `right-collapsed` on `.cockpit`.
- `mountRightPaneToggle()` builds the header button with `⇤/⇥` glyph swap + aria.
- `applyMetaStripState()` is called from boot AND from `navigateTo` (after centre swap), since the centre HTML is replaced on in-pane nav.

### CSS
- `base.css`: `details.metadata-strip > summary` (mono header, chevron), `details.metadata-strip[open] > summary` (divider under summary). Chevron rotates on open/close.
- `cockpit.css`: `.cockpit.right-collapsed { grid-template-columns: 320px minmax(0, 1fr); }` and `.cockpit.right-collapsed .cockpit-right { display: none; }`. New `.cockpit-right-toggle-slot` + `.right-pane-toggle` styles in the same family as the platform / filter pills.

### Tests
- 50 cases passing / 1 skipped — no behaviour regression detected by the existing JSON contract tests. No new assertions added (the change is a presentation toggle with no API surface).

### Verified live (your-trainer/docs)
- `curl /docs/features/FEAT-0001-BluetoothIntegration.md` returns the new `<details class="metadata-strip" open>` markup with `<summary class="metadata-strip-summary">` carrying the chevron + "Frontmatter" label.
- The right-toggle slot appears in row 1 of every rendered page header.

## Follow-ups
- [ ] When the right pane is collapsed there's no on-pane way to bring it back from inside the centre — only the header button works. If that's awkward in practice, a thin always-visible re-open strip on the right edge would help.
- [ ] The metadata strip is collapsible globally (one toggle covers every note). A per-note recall could be added by keying on the note id, but the global toggle is simpler and matches the user's stated "once collapsed stays collapsed" expectation.

## Documentation Coverage (All Types Considered)
- features: not-applicable
- requirements: not-applicable (refinement under existing REQ-0013 layout scope)
- tasks: new ([[TASK-0032]])
- issues: not-applicable
- tests: not-applicable
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 31→32, focus.task → TASK-0032, metrics tasks_total 31→32 / tasks_done 25→26, items.changes addition)
