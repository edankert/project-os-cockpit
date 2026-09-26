---
type: "[[task]]"
id: TASK-0006
aliases: ["TASK-0006"]
title: "SSE channel + client-side soft reload script"
status: done
phase: "[[PHASE-001-MVP]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
parent: "[[FEAT-0002]]"
fixes: []
effort: S
due: ""
depends: ["[[TASK-0005]]"]
blocks: []
related: []
tests: []
---

# SSE channel + soft reload

## Definition of Done
- [x] `GET /_events` returns `text/event-stream` and stays open. Per-connection `queue.Queue` subscribes to the shared bus; each connection gets an independent stream. Heartbeats every 15 s (`: heartbeat\n\n`) keep idle connections alive through proxies.
- [x] On every file event from the bus, all connected clients receive `event: file-changed\ndata: <rel-path>\n\n`.
- [x] Multi-client independence verified: two concurrent subscribers both received two events from two different file changes; no head-of-line blocking.
- [x] Client closes handled cleanly — `BrokenPipeError` / `ConnectionResetError` / `OSError` caught, `unsubscribe()` called in `finally`, no zombie subscribers, no errors in the server log.
- [x] Templates emit `<meta name="docs-server:source" content="<rel-path-or-*>">` plus `<script src="/_static/sse-reload.js" defer>` on every rendered page. The static script reads the meta and reloads with an 80 ms delay (so a save-burst settles) when the changed path matches.

## Steps
- [x] SSE handler in `server.py`: HTTP/1.1 + `text/event-stream` + `Cache-Control: no-cache, no-transform` + `X-Accel-Buffering: no`. Per-connection queue, 15 s `queue.get` timeout for heartbeats.
- [x] `Handler.protocol_version = "HTTP/1.1"` so connections can persist; existing endpoints already send Content-Length so they're keep-alive-safe.
- [x] Templates: added `reload_source` parameter to `templates.page()`. Note pages get the rel-path; landing/index/directory pages get `"*"` (reload on any event); 403/404 notice pages get nothing.
- [x] `src/docs_server/static/sse-reload.js` — vanilla JS, ~25 lines, no build step. Listens for `file-changed` events, matches via `source === "*" || source === ev.data`, reloads with `setTimeout(reload, 80)`.
- [x] Browser-equivalent test via `curl -N`: subscribed to `/_events`, touched `docs/PHASES.md`, received `: connected\n\nevent: file-changed\ndata: PHASES.md\n\n` immediately. Multi-client run: both subscribers received both events.

## Notes
SSE is one-way (server → client). That's enough here — the file watcher pushes; the browser listens. WebSocket would let the browser send too, but we don't need that until / unless we add interactivity beyond reads.

The endpoint name is `/_events` (with the underscore prefix) to align with `/_static/`. Reserved namespace; user content under `/docs/` can never collide.

The `reload_source = "*"` convention is a pragmatic over-reload: any change anywhere refreshes index/landing/dir-listing pages. They could be narrowed (e.g., index pages only reload on `.md` changes that affect the indexed type) but `*` is correct, simple, and cheap given typical project-os repo sizes.

**Verification gap (recurring):** still no formal `TST-*` notes for FEAT-0002 — verified by `curl -N` probes + the multi-client smoke test. Same flag as the FEAT-0001 close-out.
