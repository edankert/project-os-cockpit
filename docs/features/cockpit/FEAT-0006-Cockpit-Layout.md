---
type: "[[feature]]"
id: FEAT-0006
aliases: ["FEAT-0006"]
title: "3-pane cockpit layout (code-driven)"
status: in-progress
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-08
source: []
goal: "Render every note as a 3-pane cockpit page: features-by-phase navigator on the left, the rendered note in the centre, and the note's outbound + inbound-only relationships on the right."
release: ""
related: ["[[FEAT-0001]]", "[[FEAT-0002]]", "[[FEAT-0004]]", "[[REQ-0012]]", "[[REQ-0013]]", "[[ADR-0004]]"]
---

# 3-pane cockpit layout

## Goal
Every note rendered by docs-server is wrapped in a 3-pane cockpit:

- **Left pane** — project navigator: every feature in the docs tree, grouped by phase, with `id` / `title` (link) / `status` chip / `goal` columns.
- **Centre pane** — the note rendered by FEAT-0001's existing pipeline.
- **Right pane** — relationships of the active note: outbound links + inbound-only backlinks (visually distinguished), each section grouped by note `type` with `id` / `title` (link) / `status` / `priority` columns.

Layout and column choices come from [[REQ-0013]]. The data layer is the `Index` from [[TASK-0007]] (in-memory notes + outbound/inbound graph). The transport between server and client is JSON; the pane renderers are vanilla JS in the browser. No `.base` evaluator is involved — see [[ADR-0004]] for the design pivot from the original `.base`-driven plan.

## Scope

### In scope
- New JSON endpoints under `/api/cockpit/`:
  - `GET /api/cockpit/nav` — the left-pane payload (features grouped by phase, with the four columns spelled out in REQ-0013).
  - `GET /api/cockpit/context?this=<note>` — the right-pane payload for an active note: `linked` (outbound) + `backlinks` (inbound minus outbound), each grouped by `type`.
- A vanilla-JS pane renderer at `src/docs_server/static/cockpit.js` that:
  - Hydrates each pane from the JSON API on load.
  - Intercepts in-pane row clicks for client-side navigation (push history, fetch new centre HTML, refetch the right pane).
  - Subscribes to `/_events` (FEAT-0002's existing SSE channel) and refetches affected panes on relevant file changes — per-pane 100 ms debounce.
- A 3-pane HTML shell embedded in every rendered note page (centre pane = the renderer's existing HTML).
- CSS in `src/docs_server/static/cockpit.css`, all token-driven per [[REQ-0012]].
- URL state: the active note is the URL path. Refreshing preserves cockpit state.
- Visual differentiation between "outbound" and "inbound-only" right-pane sections so the reader sees at a glance that "this links here even though the active note doesn't link back."

### Out of scope
- `.base` files. They remain Obsidian dashboards. The deferred TASK-0008 / 0009 / 0010 / 0011 are kept in-tree for any future "render any `.base` as a standalone page" feature.
- Multi-pane configuration / per-deployment layout overrides.
- Editing notes via the cockpit.
- Generic / reusable cockpit framework — this is a project-os-tuned layout.

### Deferred to follow-on iterations (intentionally enabled by the JSON API choice)
- Column-sort toggles, filter-as-you-type inputs, draggable pane resizers — pure JS additions on top of the JSON contract.
- A graph-view pane reusing the same backlink graph.
- Adding more left-pane "tabs" (e.g. a Tasks dashboard alongside Features) — additive, no architectural change.

## Acceptance
- Running `python -m docs_server $(pwd)/docs` and opening any note shows a 3-pane layout: features-by-phase navigator on the left, the rendered note centre, the note's relationships on the right.
- `GET /api/cockpit/nav` returns valid JSON; every non-template feature in the repo appears under its phase header.
- `GET /api/cockpit/context?this=FEAT-0001` returns the active note's outbound and inbound-only sets, both grouped by type, with the four columns (id / title / status / priority).
- Clicking a feature in the left pane navigates to that feature in the centre (URL changes, browser history works); the right pane re-fetches.
- For an active note with both outbound and inbound-only links, both right-pane sections render and the inbound-only section is visually distinguished.
- Editing a feature note's `status`, `phase`, or `goal` in your editor causes the left pane to update within ~200 ms (no full reload). Editing the active note refreshes the centre + the right pane similarly.
- Refreshing the browser on any URL restores the same cockpit state (active note + scroll position best-effort).

## Links
- Architectural decision: [[ADR-0004]] (code-driven over `.base`-driven).
- Layout contract: [[REQ-0013]].
- Visual contract: [[REQ-0012]].
- Data layer: [[TASK-0007]] (Index + link graph).
- Build sequence: [[TASK-0012]] (JSON API) → [[TASK-0013]] (shell + JS) → [[TASK-0014]] (SSE re-fetch).
- Deferred `.base`-driven work: [[TASK-0008]] / [[TASK-0009]] / [[TASK-0010]] / [[TASK-0011]] / [[REQ-0009]] / [[REQ-0010]] / [[REQ-0011]].
