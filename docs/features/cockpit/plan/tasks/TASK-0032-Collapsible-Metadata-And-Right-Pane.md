---
type: "[[task]]"
id: TASK-0032
aliases: ["TASK-0032"]
title: "Cockpit: collapsible frontmatter card + collapsible right pane (persisted)"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-09
updated: 2026-05-23
source: []
parent: "[[FEAT-0006]]"
fixes: []
effort: S
due: ""
depends: []
blocks: ["[[TASK-0033]]"]
related: []
tests: ["[[TST-0002]]"]
---

# TASK-0032 — Collapsible frontmatter + right pane

## Definition of Done
- [x] Frontmatter card renders as a `<details open>` with a small `Frontmatter` summary row carrying a chevron — collapses on click.
- [x] Collapsed state persists in `localStorage` and reapplies on page load and after client-side navigation (centre-pane swap).
- [x] Right pane has a header toggle (`⇥` to hide, `⇤` to show). Toggling sets `.cockpit.right-collapsed`, which drops the third column and gives the centre the freed width.
- [x] Right-pane state persists in `localStorage`.
- [x] Tests pass.

## Steps
- [x] Server (`templates.py`): `_metadata_strip_html` now emits `<details class="metadata-strip" open>` with a `<summary class="metadata-strip-summary">` (chevron + "Frontmatter" label).
- [x] Server (`templates.py`): added `<div id="cockpit-right-toggle-slot">` next to the existing controls in the page header row 1.
- [x] Client (`cockpit.js`): new `META_STRIP_KEY` and `RIGHT_PANE_KEY` localStorage keys; `applyMetaStripState`, `applyRightPaneState`, `mountRightPaneToggle` helpers.
- [x] Client (`cockpit.js`): `applyMetaStripState` re-runs after every centre-pane swap in `navigateTo` so navigating across notes preserves the collapsed state.
- [x] Client (`cockpit.js`): per-element `_metaWired` flag on the `<details>` so `<toggle>` listeners aren't bound twice when the same element is reused.
- [x] CSS (`base.css`): `details.metadata-strip > summary` styling + chevron rotate; `details[open]` adds a divider under the summary.
- [x] CSS (`cockpit.css`): `.cockpit.right-collapsed` grid override (drops 3rd column) and hides `.cockpit-right`. New `.right-pane-toggle` + `.cockpit-right-toggle-slot` styles.

## Notes
- The `theme-toggle` button stays at the far right of row 1; the right-pane toggle sits to its left, after the filter pill.
- The home/landing page's "Current focus" block still uses `<aside class="metadata-strip">` (kept non-collapsible — it's already a section header on the synthetic landing).
