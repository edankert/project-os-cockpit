---
type: "[[feature]]"
id: FEAT-0006
aliases: ["FEAT-0006"]
title: "Bases-driven 3-pane cockpit layout"
status: backlog
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
goal: "Mirror the Obsidian cockpit in the browser: a 3-pane layout where any `.base` file can be mounted as left or right pane, the centre is the rendered note, and right-pane bases that reference `this.file` re-evaluate when the active note changes."
release: ""
related: [FEAT-0001, FEAT-0002, FEAT-0004]
---

# Bases-driven 3-pane cockpit layout

## Goal
Reproduce the Obsidian cockpit (NAV left / editor centre / CONTEXT right — see `tools/instructions/OBSIDIAN.md`) as the default browser experience, but driven *generically* by any `.base` file. The user can mount `NAV.base`, `Tasks.base`, `Issues.base`, or any future base file in either side pane via configuration. No `.base` filename is hardcoded inside the server.

A small, focused interpreter for the Obsidian Bases query DSL evaluates each base against an in-memory note index. Right-pane bases that filter on `this.file` (the central pattern in `CONTEXT.base`) re-evaluate every time the centre note changes, so the right pane always reflects the active note's relationships.

## Scope

### In scope
- An in-memory note index keyed by path, plus a backlink graph keyed by both file path and ID-alias. Shared with FEAT-0004's backlinks panel; built once at startup, invalidated by FEAT-0002's watcher.
- A YAML parser for `.base` files (trivial — they're already valid YAML).
- A small evaluator covering the Bases DSL primitives the existing 12 `.base` files actually use:
  - Boolean composition: `and`, `or`, `not`.
  - Comparisons: `==`, `!=`.
  - Type-link literal: `link("X")` (treated identically to `"[[X]]"`).
  - File predicates: `file.ext`, `file.inFolder(...)`, `file.hasLink(this.file)`.
  - Frontmatter predicates: `<field>.containsAny(...)`, `<field>.isEmpty()`.
  - Active-note context: `this.file`.
  - Formulas: `if(...)`, `file.asLink(...)`.
  - View shape: `type: table`, `name`, `groupBy`, `order` (columns), `sort`, `columnSize`, `rowHeight`.
- A JSON API for pane data: `GET /api/base?path=<path-to-.base>&this=<active-note-id-or-empty>` returns `{ views: [...], rows: [...] }` — view metadata (tabs, group/sort/columns) plus the evaluated row set. Cacheable when `this` is absent; per-active-note when present.
- A small vanilla-JS client (no build step, no framework) that consumes the JSON API and renders tabbed tables with grouping, sort, and column-size honoured. Lives in `src/docs_server/static/cockpit.js`. Sits alongside the existing FEAT-0002 SSE-reload script.
- A 3-pane layout shell: header strip, left pane, centre pane, right pane. The centre pane is FEAT-0001's existing rendered-note HTML; the side panes are JS-mounted from the JSON API.
- CLI flags `--cockpit-left=<path-to-.base>` and `--cockpit-right=<path-to-.base>` with defaults pointing at `docs/__bases__/NAV.base` and `docs/__bases__/CONTEXT.base`. Either flag can be set to `none` to hide that pane. Multiple bases per pane (e.g. `--cockpit-left=NAV.base,Tasks.base`) become tabs in that pane — supported at the API level even if the v1 UI only renders one base per pane.
- URL state: the active note is part of the URL path; mounted bases are query params (`?left=...&right=...`) so a refresh restores the cockpit exactly as it was.
- SSE wiring (depends on FEAT-0002): the watcher emits `{kind, path}` events; the JS client receives them and re-fetches only the pane(s) whose evaluator could be affected. A change to the active note's frontmatter triggers a right-pane re-fetch; a change to a `.base` file triggers a re-fetch of any pane mounting that base; bulk frontmatter edits coalesce into a single re-fetch per pane.

### Out of scope
- Generalising the evaluator beyond the primitives currently used. New primitives can be added as new `.base` files start using them; not speculatively.
- Editing notes from the cockpit (read-only viewer).
- Reproducing every Obsidian Bases pixel detail — column widths and group headers approximate the Obsidian look but don't have to match exactly.

### Deferred to follow-on iterations (intentionally enabled by the JSON API choice)
- Click-to-sort column headers, type-to-filter row inputs, draggable pane resizers — all are pure client-side additions on top of the JSON contract.
- A graph-view pane reusing the same backlink graph.
- Saved cockpit layouts (named workspaces).

## Acceptance
- Running `python -m docs_server $(pwd)/docs` opens a page with three panes: NAV.base on the left, the rendered note in the middle, CONTEXT.base on the right. Both side panes hydrate from the JSON API on first load.
- `GET /api/base?path=docs/__bases__/NAV.base` returns valid JSON with the expected `views[]` and `rows[]` for this repo.
- `GET /api/base?path=docs/__bases__/CONTEXT.base&this=FEAT-0001` returns rows that include only notes which link to FEAT-0001.
- Clicking a row in NAV navigates the centre pane (URL changes, browser history works); the right pane re-fetches with the new active note and updates with no full-page reload.
- `python -m docs_server $(pwd)/docs --cockpit-left=docs/__bases__/Tasks.base` swaps the left pane to the Tasks dashboard with no server code changes.
- `--cockpit-right=none` removes the right pane and gives the centre pane the freed width.
- Editing a note in your editor causes the centre pane (existing FEAT-0002 reload) *and* any side pane that depends on it to soft-refresh within a fraction of a second — no full-page reload.
- Editing `NAV.base` itself causes the left pane to re-render with the new view definition via SSE.
- Refreshing the browser preserves the cockpit state (active note + mounted bases) from the URL.

## Links
- Conceptual reference: `tools/instructions/OBSIDIAN.md` (Cockpit Layout section).
- Source bases: `docs/__bases__/*.base` (12 files; only NAV and CONTEXT are mounted by default but any can be).
- Shared infrastructure: FEAT-0004 backlinks panel — uses the same note index + backlink graph this feature builds.
