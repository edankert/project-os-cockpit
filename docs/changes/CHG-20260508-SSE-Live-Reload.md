---
type: "[[change]]"
id: CHG-20260508-SSE-Live-Reload
aliases: ["CHG-20260508-SSE-Live-Reload"]
title: "SSE channel + client soft-reload — FEAT-0002 done"
status: merged
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
source: ["[[TASK-0006]]"]
commit: ""
pr: ""
impacts:
  - "src/docs_server/server.py"
  - "src/docs_server/templates.py"
  - "src/docs_server/renderer.py"
  - "src/docs_server/static/sse-reload.js"
issues: []
features: ["[[FEAT-0002]]"]
related: ["[[REQ-0004]]", "[[CHG-20260507-File-Watcher]]", "[[TASK-0011]]"]
---

# SSE live reload online

## Summary
Adds a long-lived `/_events` endpoint that streams `text/event-stream` to every connected browser. Each connection subscribes to the shared `EventBus` from TASK-0005; file changes fan out as `event: file-changed\ndata: <rel-path>\n\n`. A small vanilla-JS script (`sse-reload.js`) subscribes from every rendered page and reloads when the changed path matches.

This is the final FEAT-0002 task — live reload is now observable end-to-end. Save a `.md` in your editor; the corresponding browser tab refreshes within ~100 ms.

## Impact

### New URL
- `GET /_events` — SSE channel. Per-connection queue subscribed to the bus; heartbeats every 15 s. HTTP/1.1 keep-alive.

### Templates
- `templates.page()` now takes a `reload_source` parameter. When set, the rendered HTML carries:
  - `<meta name="docs-server:source" content="<value>">` in `<head>`
  - `<script src="/_static/sse-reload.js" defer>` after the theme bootstrap
- Three reload modes:
  - **Note pages** (rendered `.md`): `reload_source` = the docs-root-relative path. Reload only when *that* file changes.
  - **Landing / index / directory pages**: `reload_source = "*"`. Reload on any file event.
  - **Notice pages** (403 / 404): no reload (omit the meta tag).

### Client script
- `src/docs_server/static/sse-reload.js` — ~25 lines, vanilla JS, no build, no framework. Reads the meta tag, opens an `EventSource` to `/_events`, calls `location.reload()` (after 80 ms) when a `file-changed` event matches.
- Browser auto-reconnect on disconnect is built into `EventSource` — no work on our side. So `docs-server` can restart and connected tabs reattach automatically.

### HTTP version bump
- Handler now uses `protocol_version = "HTTP/1.1"`. Existing endpoints continue to send `Content-Length`, so keep-alive across non-SSE requests is fine. No behaviour change for clients beyond longer-lived TCP connections.

### Multi-client correctness
- Verified two concurrent SSE subscribers each receive every file-change event independently — no head-of-line blocking. Bus snapshots subscribers under a lock and dispatches outside, so a slow client can't stall the others.

### Clean disconnect
- `BrokenPipeError` / `ConnectionResetError` / `OSError` caught in the SSE handler. `unsubscribe()` called from `finally`, so subscriber list never leaks.

## Follow-ups
- [ ] [[TASK-0011]] — cockpit JS-side re-fetch will extend the SSE payload with a typed `kind` (`frontmatter` / `body` / `base`) so panes can target what to re-fetch instead of always reloading the page. The current event shape is intentionally coarse so the SSE channel could land first.
- [ ] FEAT-0002 done — retro-fitting `TST-*` acceptance tests across FEAT-0001 + FEAT-0002 is increasingly worth doing before either FEAT-0003 (terminal) or FEAT-0006 (cockpit) start.
- [ ] FEAT-0003 (embedded terminal) is the only remaining PHASE-001 work and has no task breakdown yet — needs `feature-scaffold`-style decomposition before implementation.
