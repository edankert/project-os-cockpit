---
type: "[[task]]"
id: TASK-0010
aliases: ["TASK-0010"]
title: "Cockpit shell + JS pane renderer"
status: backlog
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
implements: ["[[FEAT-0006]]"]
fixes: []
related: ["[[REQ-0012]]"]
effort: M
due: ""
depends: [TASK-0009]
blocks: [TASK-0011]
related: []
tests: []
---

# Cockpit shell + JS pane renderer

## Definition of Done
- [ ] CLI flags wired:
  - `--cockpit-left=<path-or-list-or-none>` (default `docs/__bases__/NAV.base`)
  - `--cockpit-right=<path-or-list-or-none>` (default `docs/__bases__/CONTEXT.base`)
  - Comma-separated list mounts multiple bases as tabs in that pane.
  - `none` hides the pane.
- [ ] The centre route (`/<note-path>`) returns the cockpit HTML shell: header, left/centre/right pane divs, embedded `<script type="application/json" id="cockpit-config">` with `{left: [...], right: [...], active: "<note-id>"}`, and `<script src="/_static/cockpit.js" defer>`.
- [ ] `src/docs_server/static/cockpit.js` (vanilla JS, no build, no framework):
  - Reads `#cockpit-config` on load.
  - For each mounted pane: fetches `/api/base?path=<each-base>&this=<active>` and renders a tabbed view set (one tab per `views[]` entry). Multi-base panes get a tab strip per base, then per view within the active base.
  - Renders tables honouring `order` (column projection), `groupBy` (group headers + collapsible groups), `sort` (row order within groups), `columnSize` (CSS pixel widths), `rowHeight` (CSS class).
  - Resolves `formula.display_title` link cells to anchors that navigate the centre pane.
  - Intercepts row-link clicks: pushes history state, re-renders the centre pane via `fetch`, re-fetches *only* the right pane with the new `this`, no full-page reload.
- [ ] URL state contract:
  - Active note in the URL path (`/FEAT-0001`).
  - Mounted bases as query params (`?left=docs/__bases__/NAV.base&right=docs/__bases__/CONTEXT.base`).
  - Refresh restores cockpit exactly.
- [ ] Static file route: `/_static/<file>` serves out of `src/docs_server/static/` with a path-traversal guard.
- [ ] CSS in `src/docs_server/static/cockpit.css`: 3-column flex layout (left 280px / centre fluid / right 280px), header strip, table styles, group headers. Mobile-narrow gracefully collapses to centre-only. The stylesheet follows [[REQ-0012]]:
  - All colors are CSS custom properties defined on `:root` (light) and `[data-theme="dark"]` (dark). No hard-coded hex/rgb in component rules.
  - Greyscale ramp tokens (`--bg`, `--surface`, `--border`, `--text`, `--text-muted`) plus a small set of semantic accent tokens (`--accent-link`, `--accent-focus`, `--status-active`, `--status-done`, `--status-blocked`, etc.). All accents desaturated (≤60% HSL S).
  - Theme resolution: an inline `<head>` script reads `localStorage.theme || matchMedia('prefers-color-scheme: dark')` and sets `data-theme` on `<html>` *before* stylesheet apply, to avoid the wrong-theme flash on first paint.
  - A theme-toggle control in the cockpit header writes to localStorage and flips `data-theme`.
- [ ] Browser smoke test (manual, documented in the task's test-plan section): open this repo's docs/, see all three panes, click a NAV row, see centre + right update without reload, hit refresh, see same state.

## Steps
- [ ] Add the static-file route (small, with the same `..` guard as the renderer).
- [ ] Build the cockpit HTML shell template (in `docs_server.server` or a new `templates/cockpit.html` — single file is fine).
- [ ] Write `cockpit.js`:
  - `loadConfig()` → reads `#cockpit-config`.
  - `fetchPane(bases, this_)` → returns a list of `EvaluatedBase` payloads.
  - `renderPane(target, payloads)` → tab strip + per-view table.
  - `renderTable(view)` → group/sort/column logic.
  - `onRowClick(href)` → `history.pushState`, re-fetch centre, re-fetch right.
  - `onPopState` → reverse the above.
- [ ] Write `cockpit.css`.
- [ ] Wire the CLI flags through to the cockpit-config payload.
- [ ] Manual browser test against this repo's `docs/`.

## Notes
**Vanilla JS only.** No npm, no bundler, no framework. The README's "no Node.js, no build step" promise stays intact — the JS is a single file under `src/docs_server/static/`.

Multi-base-per-pane support is in the contract (`--cockpit-left=NAV.base,Tasks.base`) even if the v1 UI only renders a single base nicely. Validates that the JSON API design generalises before TASK-0011 starts coalescing SSE events.

When the active note is on the boundary of the docs root or doesn't exist, the centre pane shows a "not found" placeholder and `this` in the right-pane fetch is null (so CONTEXT.base evaluates to empty).
