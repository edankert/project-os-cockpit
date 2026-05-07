---
type: "[[task]]"
id: TASK-0013
aliases: ["TASK-0013"]
title: "Cockpit shell + JS pane renderer (code-driven layout)"
status: backlog
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
source: []
implements: ["[[FEAT-0006]]", "[[REQ-0013]]"]
fixes: []
effort: M
due: ""
depends: [TASK-0012]
blocks: [TASK-0014]
related: ["[[REQ-0012]]", "[[ADR-0004]]"]
tests: []
---

# Cockpit shell + JS pane renderer

## Definition of Done
- [ ] Centre route (`/<note-path>`) returns the cockpit HTML shell: header, three pane divs (left / centre / right), embedded `<script type="application/json" id="cockpit-config">{ "active": "<note-id-or-path>" }</script>`, and `<script src="/_static/cockpit.js" defer>`.
- [ ] `src/docs_server/static/cockpit.js` (vanilla JS, no build, no framework):
  - Reads `#cockpit-config` on load.
  - On boot: fetches `/api/cockpit/nav` (left pane, cached for the session) and `/api/cockpit/context?this=<active>` (right pane).
  - Renders the left pane: phase-grouped table with `id` / `title` (link) / `status` (chip) / `goal` columns, group headers link to the phase note.
  - Renders the right pane: two sections (`Linked from this note`, `Links back to this note`), each grouped by type. Items show `id` / `title` (link) / `status` (chip) / `priority`. Backlink-only section uses a slightly muted styling so the visual distinction is immediate (e.g. faded background or italic title).
  - Intercepts row-link clicks within the panes: pushes history state, re-renders the centre pane via `fetch`, re-fetches only the right pane with the new `this`, no full-page reload.
  - URL state contract: active note in the URL path; refreshing preserves the cockpit state.
- [ ] CSS in `src/docs_server/static/cockpit.css`: 3-column flex layout (left ~280 px / centre fluid / right ~320 px), tables with phase group headers, type group headers in the right pane, backlink-only section visually distinguished. All token-driven per [[REQ-0012]] (no hard-coded colors). Mobile-narrow gracefully collapses to centre-only with the side panes hidden.
- [ ] Browser smoke test (manual, documented):
  - Open this repo's docs/ in the cockpit. Left pane shows features under PHASE-001/002/003/004 headers.
  - Click a feature → centre pane updates, URL changes, right pane re-fetches.
  - Pick a feature with both outbound links and unique inbound (e.g. FEAT-0001 right after this lands) and visually verify the two sections, with backlink-only items distinguished.

## Steps
- [ ] Decide centre-route shape: keep `/<note-path>` (current renderer route) and treat the cockpit shell as wrapping every note page; OR introduce a `/cockpit/<note-path>` route. Recommend wrapping — every note is already a cockpit page.
- [ ] Add a static-file route entry for `cockpit.js` + `cockpit.css` (the existing `/_static/<file>` route already handles this; just drop the files in).
- [ ] Build the cockpit HTML shell template (in `templates.py` — extend the existing `page()` or add a sibling `cockpit_page()`).
- [ ] Write `cockpit.js`:
  - `loadConfig()` — reads `#cockpit-config`.
  - `fetchNav()` / `fetchContext(active)` — JSON API consumers.
  - `renderLeftPane(payload)` — phase-grouped feature table.
  - `renderRightPane(payload)` — two sections, type-grouped, backlink-only distinguished.
  - `onRowClick(href)` — `history.pushState`, re-fetch centre, re-fetch right.
  - `onPopState` — reverse the above.
- [ ] Write `cockpit.css` — using existing tokens from `base.css`, no hard-coded values.
- [ ] Manual browser test against this repo's `docs/`.

## Notes
**Vanilla JS only.** No npm, no bundler, no framework. ~one file, alongside `sse-reload.js`.

**Centre pane rendering**: the existing renderer already returns full HTML. The cockpit shell can either embed that HTML on first paint and use `fetch` + `DOMParser` to swap `.content` on nav, or use an `<iframe>`. Recommend the fetch+swap path so theme/state stays consistent.

**Why JS over server-rendered**: the right pane re-fetches whenever the active note changes; doing that as a full page reload means the left pane re-renders too (loses scroll position, flickers). With JSON API + JS, only the right pane re-fetches. Per [[ADR-0004]], the JSON contract also unblocks future interactive controls (column-sort, filter, graph pane) as JS-only changes.

**Backlink-only distinction** — small visual cues:
- Section heading: "Links back to this note" with a subtitle "(inbound only)".
- Maybe an arrow glyph (← vs →) prefix on items.
- Slightly muted text color.
- Final styling decided in CSS pass during implementation.
