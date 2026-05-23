---
type: "[[task]]"
id: TASK-0013
aliases: ["TASK-0013"]
title: "Cockpit shell + JS pane renderer (code-driven layout)"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-08
updated: 2026-05-23
source: []
implements: ["[[FEAT-0006]]", "[[REQ-0013]]"]
fixes: []
effort: M
due: ""
depends: ["[[TASK-0012]]"]
blocks: ["[[TASK-0014]]", "[[TASK-0015]]", "[[TASK-0018]]"]
related: ["[[REQ-0012]]", "[[ADR-0004]]"]
tests: []
---

# Cockpit shell + JS pane renderer

## Definition of Done
- [x] Centre route (`/<note-path>`) returns the cockpit HTML shell: header, three pane divs (left / centre / right), embedded `<script type="application/json" id="cockpit-config">{ "active": "<note-id-or-path>" }</script>`, and `<script src="/_static/cockpit.js" defer>`.
- [x] `src/docs_server/static/cockpit.js` (vanilla JS, no build, no framework):
  - Reads `#cockpit-config` on load.
  - On boot: fetches `/api/cockpit/nav` (left pane, cached for the session) and `/api/cockpit/context?this=<active>` (right pane).
  - Renders the left pane: phase-grouped feature cards with `status` chip + `id` + `title` link + `goal` underneath. Whole-card click area. "Hide completed" filter pill (persisted in localStorage).
  - Renders the right pane: two sections (`Linked from this note`, `Links back to this note`), each grouped by type. Items show `id` / `title` (link) / `status` (chip) / `priority`. Backlink-only section uses muted styling + "(inbound only)" subtitle so the visual distinction is immediate.
  - Intercepts row-link clicks within the panes: pushes history state, re-renders the centre pane via `fetch` + `DOMParser`, re-fetches only the right pane with the new `this`, no full-page reload.
  - URL state contract: active note in the URL path; refreshing preserves the cockpit state.
- [x] CSS in `src/docs_server/static/cockpit.css`: 3-column grid layout (left ~280 px / centre fluid / right ~320 px), phase group headers, type group headers + per-type chip color tokens (≤60% saturation per [[REQ-0012]]) in the right pane, backlink-only section visually distinguished. All token-driven (no hard-coded colors). Mobile-narrow gracefully collapses to centre-only with the side panes hidden.
- [x] Browser smoke test (manual, documented):
  - Open this repo's docs/ in the cockpit. Left pane shows features under PHASE-001/002/003/004 headers.
  - Click a feature → centre pane updates, URL changes, right pane re-fetches.
  - Pick a feature with both outbound links and unique inbound (e.g. FEAT-0001) and visually verify the two sections, with backlink-only items distinguished.

## Steps
- [x] Wrap every note page with the cockpit shell (chose option A in `templates.py::page()`); no separate `/cockpit/<note-path>` route.
- [x] Static-file route already serves `cockpit.js` + `cockpit.css` via `/_static/<file>`.
- [x] Cockpit HTML shell built into `templates.py::page()` with `cockpit_active` parameter; embeds `#cockpit-config`.
- [x] `cockpit.js` written: `loadConfig()`, `fetchNav()` (cached), `fetchContext(active)`, `renderLeftPane()`, `renderRightPane()`, `onRowClick()`, `onPopState()`, `applyHideCompletedFilter()`.
- [x] `cockpit.css` written using base.css tokens; per-type chip color tokens added to base.css (`--type-feature`, `--type-task`, ..., 13 hues at ≤60% saturation).
- [x] Manual browser test against this repo's `docs/`.

## Notes
**Vanilla JS only.** No npm, no bundler, no framework. ~one file, alongside `sse-reload.js`.

**Centre pane rendering**: the existing renderer already returns full HTML. The cockpit shell can either embed that HTML on first paint and use `fetch` + `DOMParser` to swap `.content` on nav, or use an `<iframe>`. Recommend the fetch+swap path so theme/state stays consistent.

**Why JS over server-rendered**: the right pane re-fetches whenever the active note changes; doing that as a full page reload means the left pane re-renders too (loses scroll position, flickers). With JSON API + JS, only the right pane re-fetches. Per [[ADR-0004]], the JSON contract also unblocks future interactive controls (column-sort, filter, graph pane) as JS-only changes.

**Backlink-only distinction** — small visual cues:
- Section heading: "Links back to this note" with a subtitle "(inbound only)".
- Maybe an arrow glyph (← vs →) prefix on items.
- Slightly muted text color.
- Final styling decided in CSS pass during implementation.
