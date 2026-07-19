---
type: "[[phase]]"
id: PHASE-006
aliases: ["PHASE-006"]
title: "Native cockpit UI (TypeScript rewrite)"
status: done
order: 6
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
features:
  - "[[FEAT-0008-Cockpit-API-Hardening]]"
  - "[[FEAT-0009-Native-Shell-Layout]]"
  - "[[FEAT-0010-Native-Nav-Right-Pane]]"
  - "[[FEAT-0011-Native-Center-Pane]]"
  - "[[FEAT-0012-Native-UX]]"
  - "[[FEAT-0013-Agent-State-Signal]]"
depends: ["[[PHASE-005-Desktop-Shell]]"]
---

# Phase 6: Native cockpit UI (TypeScript rewrite)

## Goal
Rewrite the 3-pane cockpit experience as a native Electron renderer.
Replace the in-iframe HTML the Python tool currently serves to mode 3
(desktop) with TypeScript panes that talk to the Python sidecar's
existing JSON API. The Python tool keeps its Markdown renderer + index
+ SSE + file watcher and continues to serve **mode 1 (browser)
unchanged** — only the desktop shell stops loading the rendered HTML
shell and starts driving the UI directly.

Outcome: the desktop app stops feeling like a wrapped website. Native
context menus, real keyboard shortcuts (Cmd+P / Cmd+F / Cmd+1..3),
drag-and-drop, multi-window, system-theme matching, OS-level
trackpad gestures, no iframe focus weirdness.

## Scope

### In scope
- **FEAT-0008** — Cockpit API hardening (Python side). Audit endpoints,
  freeze schema, add a `GET /api/render/<rel-path>` endpoint returning
  the rendered Markdown HTML fragment + the metadata the renderer needs.
  Additive; mode 1 unaffected.
- **FEAT-0009** — Native shell layout. 3-pane grid, resizers, collapse
  states, `titleBarStyle: 'hiddenInset'` chrome with breadcrumb, status
  bar, system/light/dark theme sync.
- **FEAT-0010** — Native nav surface. Activity-bar layout: narrow
  workspace rail (with per-workspace agent-state dots fed by
  FEAT-0013) **plus** the in-workspace primary nav (Features /
  Tasks / Issues / Library / Recent) fed by `/api/cockpit/nav`, plus
  the right pane (linked + backlinks) fed by
  `/api/cockpit/context`. SSE soft-reload + tab heartbeat. Replaces
  the temporary Browse panel that ships with FEAT-0011.
- **FEAT-0011** — Native center pane + routing. Fetches rendered HTML
  fragments, mounts them, intercepts internal `<a>` clicks, owns
  back/forward history, per-note scroll preservation, hash anchors,
  interactive checkboxes.
- **FEAT-0012** — Native-only UX wins. Cmd+P quick-switch (fuzzy note
  search), Cmd+F find-in-doc, native context menus on tree items,
  drag-and-drop file → note, window state per workspace, multi-window.
  OS notifications when a workspace's agent-state flips to `waiting`
  (consumes FEAT-0013).
- **FEAT-0013** — Agent state signal. New `cockpit signal <state>`
  CLI + `POST /api/cockpit/agent-state` endpoint + per-workspace
  state tracking + `cockpit:agent-state` SSE fan-out. The data pipe
  the workspace rail dots (FEAT-0010) and notifications (FEAT-0012)
  consume. Schema bump.

### Out of scope
- Replacing `renderer.py` (Python's Markdown→HTML pipeline). The
  rewrite keeps Python rendering the Markdown body; only the wrapping
  shell + panes move to TypeScript.
- Rewriting the index / link graph / file watcher / SSE channel.
- Editing notes from inside the cockpit. The cockpit stays a viewer;
  editing happens in the user's editor.
- Mode 1 (browser) UI changes. The Python-rendered HTML pages stay
  alive and unchanged for browser users.
- Mode 2 (Obsidian Bases). Untouched.
- Plugin / extension system, i18n, accessibility audit. Future work.

## Exit criteria
- All current mode-3 functionality reproduced as native renderer panes
  with no iframe — including every left-mode, the right pane's three
  sections, the embedded terminal, and live reload.
- Mode 1 regression-test clean: every Python endpoint + every
  Python-rendered HTML page that exists today still works for browser
  users (TST-* notes per endpoint before deprecating any).
- At minimum three native-only features shipped: **Cmd+P quick-switch**,
  **Cmd+F find-in-doc**, **native context menus**.
- Visual parity with current cockpit (no obvious style regressions in
  the rendered Markdown view or in the panes).

## Dependencies
- **Hard:** PHASE-005 (desktop shell exists; iframe currently mounts
  the cockpit).
- **Hard:** Mode 1 regression coverage before deprecating any
  Python-rendered HTML for desktop. Some endpoint tests exist
  (`tests/test_cockpit.py`, `test_cockpit_state.py`); gaps need
  filling in FEAT-0008.

## Notes

### Sequencing
1. **FEAT-0008 first.** API contract has to be solid before the
   renderer is built against it. ✓ *done*
2. **FEAT-0011 (center pane) before FEAT-0010 (nav)** — gets something
   visible quickly. Backfill the nav once the center pane proves the
   approach. ✓ *done*
3. **FEAT-0013 before FEAT-0010.** The agent-state signal is the data
   pipe the workspace rail consumes; ship the pipe first, then the UI
   that reads it.
4. **FEAT-0010 (nav surface).** Workspace rail with status dots + the
   full in-workspace nav. Replaces the temporary Browse panel.
5. **FEAT-0009 (shell layout)** can happen in parallel with 10 — it
   only touches the outer chrome.
6. **FEAT-0012 (UX wins) last.** Easiest to scope-trim if energy runs
   out; everything in it is pure addition.

### Risks
- **Polish drift.** `cockpit.js` (~1500 lines) and `cockpit.css`
  (~1000 lines) carry a lot of small refinements (Obsidian-style
  tree, hybrid Changes buckets, type-aware group icons, status
  palettes, …). Plan a dedicated polish sweep before closing the
  phase. Inventory all CSS classes and JS behaviours used by the
  Python templates before starting FEAT-0009.
- **API stability promises.** Once FEAT-0008 freezes the schema, any
  change ripples to both modes. Bump `X-Cockpit-Schema` on every
  break.
- **Mode 1 styling.** The Python templates emit class names + inline
  CSS that mode 1 users see directly. Moving CSS into the renderer
  means mode 1 stops getting that CSS. Either keep dual copies (with
  a sync rule) or accept that mode 1 styling diverges. **Open
  question** — FEAT-0009 decides.

### Why now
PHASE-005 shipped the wrapped-cockpit shell, which works but feels
foreign — keyboard shortcuts stop at the iframe boundary, right-click
gives a browser context menu, no Cmd+P, no real find. The user
explicitly raised the question "is the wrap-the-cockpit-in-an-iframe
choice correct?" and chose to scope the rewrite (over the lighter
"bridge" alternative).
