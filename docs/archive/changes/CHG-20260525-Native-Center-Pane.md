---
type: "[[change]]"
id: CHG-20260525-Native-Center-Pane
aliases: ["CHG-20260525-Native-Center-Pane"]
title: "Native centre pane: /api/render mount, link interception, history, scroll/anchors, interactive checkboxes"
status: merged
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0070]]", "[[TASK-0071]]", "[[TASK-0072]]", "[[TASK-0073]]", "[[TASK-0074]]"]
commit: ""
pr: ""
impacts:
  - "desktop/src/renderer/index.html (iframe → article#doc-view; cockpit.css link)"
  - "desktop/src/renderer/renderer.css (.doc-view styles)"
  - "desktop/src/renderer/renderer.ts (+navigateTo, link interception, history, scroll, checkbox handler)"
  - "desktop/src/main.ts (app:openExternal IPC, View → Back/Forward menu items)"
  - "desktop/src/preload.ts (app.openExternal, menu.onBack/onForward exposed)"
  - "desktop/scripts/copy-assets.mjs (copies src/project_os_cockpit/static/cockpit.css)"
  - "src/project_os_cockpit/server.py (+/api/notes/check-toggle route, _toggle_task_at helper, per-file lock)"
  - "tests/test_check_toggle.py (new — 10 tests)"
  - "docs/references/COCKPIT-API.md (+ POST /api/notes/check-toggle section)"
  - "docs/features/native-center-pane/plan/tests/TST-0008-Check-Toggle.md (new)"
issues: []
features: ["[[FEAT-0011-Native-Center-Pane]]"]
related: ["[[FEAT-0008-Cockpit-API-Hardening]]", "[[PHASE-006-Native-Cockpit-UI]]"]
---

# Native centre pane

## Summary

FEAT-0011 done (in-review). The iframe is gone — the centre column
is now a native `<article id="doc-view">` filled by `fetch()`ing
`GET /api/render?path=<rel>` and mounting the HTML. The renderer
owns navigation, history, scroll, hash anchors, link routing, and
interactive task-list checkboxes.

Test count: **120 → 130** (+10 from the new check-toggle endpoint).
8 TST notes total.

Mode 1 (browser) unaffected: the iframe-less renderer is a
mode-3-only swap; no Python templates or static assets change
behaviour for browser users. The new `POST /api/notes/check-toggle`
endpoint is purely additive.

## What landed

### TASK-0070 — `/api/render`-driven mount
- HTML: `<iframe id="sidecar-view">` removed, replaced with
  `<article id="doc-view">`.
- `copy-assets.mjs` now copies `src/project_os_cockpit/static/cockpit.css`
  → `dist/renderer/cockpit.css` at build time so the mounted HTML
  inherits mode-1 styling. Single source of truth in Python.
- Renderer: on `sidecar:event` 'ready', stashes the workspace's
  sidecar URL, then `navigateTo('README.md')`. 404 mounts a "no
  README" placeholder.

### TASK-0071 — Link interception
- New IPC `app:openExternal` (main → `shell.openExternal` after
  validating `https?://`).
- Renderer: delegated `click` listener on `#doc-view` classifies
  every `<a>`: docs-internal → `navigateTo(rel)`; external →
  `openExternal(url)`; fragment-only → in-page scroll.
- Cmd/Ctrl-click on a docs link forces system-browser open (escape
  hatch).

### TASK-0072 — History stack
- In-memory `historyStack` + `historyCursor`; bounded at 100.
- `navigateTo(rel, {replace?, fromHistory?})` pushes by default,
  replaces on history nav.
- Mouse buttons 3 / 4 → back / forward.
- View menu items **Back** (Cmd+[) and **Forward** (Cmd+]).

### TASK-0073 — Scroll preservation + hash anchors
- `scrollPositions: Map<relPath, number>` updated at every nav-away.
- History nav restores from the map; fresh nav resets to top.
- `#heading` fragment → `requestAnimationFrame` →
  `element.scrollIntoView()` after the new HTML lays out.
- SSE `agent:focus` events route through `navigateTo`, so an
  external `cockpit focus <id>` actually moves the centre pane (it
  used to just brighten the iframe via SSE — now the renderer owns
  the swap).

### TASK-0074 — Interactive checkboxes
- New endpoint `POST /api/notes/check-toggle` with
  `{path, index, checked}`. Walks the source `.md` to find the
  zero-based Nth task-list line; rewrites the `- [ ]` / `- [x]`
  token; per-file `threading.Lock` serialises concurrent toggles.
- Renderer: strips `disabled` from checkboxes on mount; delegated
  `change` listener on `#doc-view` posts the toggle and reverts
  optimistic UI on error.
- 10 pytest cases (TST-0008): happy on/off, `docs/` prefix, 400 on
  missing fields, 403 traversal, 404 missing-file / out-of-range
  index, nested-list index counting.

## Smoke-test status
- `npm run build` clean.
- Electron launches; 9 workspaces discovered.
- Renderer-side behaviour (click a link, back/forward, scroll
  restore, hash anchor, checkbox toggle) needs visual confirmation
  by the user — that's what flips TASK-0070..0074 from `doing` →
  `done`.

## Documentation Coverage
- features: covered (FEAT-0011 status → `in-review`)
- requirements: not-applicable
- tasks: TASK-0070..0074 status → `doing` (pending user smoke)
- issues: not-applicable
- tests: TST-0008 added (status `passing`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (counters, focus → TASK-0074, FEAT-0011 →
  in-review, tests 7→8, test_cases 119→131/130 passing, tasks_done
  unchanged at 65 until user verifies)
