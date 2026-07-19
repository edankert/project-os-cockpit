---
type: "[[plan]]"
id: PLAN-FEAT-0011
aliases: ["PLAN-FEAT-0011"]
title: "Plan: Native centre pane + routing"
status: active
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
implements: ["[[FEAT-0011-Native-Center-Pane]]"]
related: ["[[FEAT-0008-Cockpit-API-Hardening]]", "[[FEAT-0009-Native-Shell-Layout]]", "[[FEAT-0010-Native-Nav-Right-Pane]]", "[[PHASE-006-Native-Cockpit-UI]]"]
---

# Plan — FEAT-0011 Native centre pane

## Delivery sequence

1. **[[TASK-0070]] — Replace iframe with `/api/render`-driven mount.**
   The centre pane stops being an `<iframe>` and becomes a `<div>`
   that fetches `GET /api/render?path=<rel>` from the active sidecar
   on first ready + on every navigation request. Renderer copies
   `cockpit.css` into `dist/renderer/` at build time so the mounted
   HTML inherits the same styles mode-1 uses. Default landing: the
   workspace's `docs/README.md` when present, else a "pick a note"
   placeholder.

2. **[[TASK-0071]] — Internal link interception + soft nav.**
   Intercept `<a>` clicks within the mounted HTML. Three buckets:
   docs-internal (`/docs/...` or wikilinks resolving to a docs
   path) → soft-nav through the same fetch path; external
   (`http(s)://...`) → `shell.openExternal` via IPC; fragment-only
   (`#heading`) → scroll within mounted HTML.

3. **[[TASK-0072]] — History stack (back / forward).**
   In-memory `historyStack: string[]` keyed by docs-rel paths, plus
   a cursor for the current position. Wire to: mouse buttons
   4 / 5, View menu Back/Forward (accelerator `Cmd+[` / `Cmd+]`),
   and ignore-on-replace flag for the soft-nav helper.

4. **[[TASK-0073]] — Per-note scroll preservation + hash anchors.**
   Save scroll offset on every nav-away, restore on history back.
   `#heading` anchors scroll to the matching element after mount
   (small `requestAnimationFrame` deferral so the DOM is laid out).
   Cockpit-focus events from the SSE bridge land on this code path.

5. **[[TASK-0074]] — Interactive checkboxes.**
   Click a `<input type="checkbox">` inside the mounted HTML → POST
   to a new `/api/notes/check-toggle` endpoint that locates the
   checkbox line in the source `.md` and rewrites the `- [ ]` /
   `- [x]` token. Optimistic UI update; SSE `file-changed` confirms.
   Updates the contract doc + adds a pytest.

## Dependencies
- **Hard:** FEAT-0008 (the `/api/render` endpoint this consumes).
- **Soft:** FEAT-0009 (shell layout, theming) — independent;
  centre pane works without polished chrome.
- **Soft:** FEAT-0010 (left nav) — FEAT-0011 ships before; the user
  navigates via links inside the mounted doc until 0010 lands.

## Open questions to pin during implementation
- **Landing target.** First-load defaults to `README.md`. If
  absent, render a "pick a note" placeholder. Consider snapshot
  focus when FEAT-0010 lands. Decided in TASK-0070.
- **Click target for soft-nav.** Match `<a href="/docs/...">` or
  any `<a>` whose resolved href starts with the sidecar origin
  + `/docs/`? Probably both; the rendered HTML uses both forms
  depending on context. Decided in TASK-0071.
- **History limit.** Bound the stack at 100 entries to prevent
  unbounded memory in heavy sessions. Decided in TASK-0072.
- **Hash anchor target.** Markdown rendering emits `<h2 id="...">`
  via the slugger. Document the expected id-shape in
  COCKPIT-API.md when TASK-0073 lands.
- **Checkbox write-back race.** Two checkboxes clicked in rapid
  succession from the same render — the second write needs to
  read the file after the first write committed. Use a per-file
  lock in the Python endpoint. Decided in TASK-0074.

## Out of plan
- Native nav left-pane (FEAT-0010).
- Native shell chrome / title bar (FEAT-0009).
- Cmd+P quick-switch / Cmd+F find-in-doc (FEAT-0012).
- Search / replace in the rendered doc.
- Side-by-side compare view.
- A bundler / TS test framework — renderer changes verified
  manually for now.
