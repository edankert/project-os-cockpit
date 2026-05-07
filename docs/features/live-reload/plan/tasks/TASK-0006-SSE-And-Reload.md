---
type: "[[task]]"
id: TASK-0006
aliases: ["TASK-0006"]
title: "SSE channel + client-side soft reload script"
status: backlog
phase: "[[PHASE-001-MVP]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
implements: ["[[FEAT-0002]]", "[[REQ-0004]]"]
fixes: []
effort: S
due: ""
depends: [TASK-0005]
blocks: []
related: []
tests: []
---

# SSE channel + soft reload

## Definition of Done
- [ ] `GET /events` returns `text/event-stream` and stays open.
- [ ] On every file-change event from the bus (TASK-0005), broadcasts `event: file-changed\ndata: <relative-path>\n\n` to all connected clients.
- [ ] Each connected client gets an independent stream (no head-of-line blocking).
- [ ] Client closes are handled cleanly — no zombie connections or leaks.
- [ ] Renderer template appends a small `<script>` that subscribes to `/events` and calls `location.reload()` if the changed path matches the current page's source (data attribute on the body or a `<meta name="docs-server:source">` tag).

## Steps
- [ ] SSE response handler in `server.py` — set headers, `text/event-stream` + `Cache-Control: no-cache`, write `: heartbeat\n\n` every ~15 s to keep the connection alive.
- [ ] Subscribe-to-bus pattern: each connection has a queue; events are pushed to all queues; handler drains its queue into the response.
- [ ] Template: add `<meta name="docs-server:source" content="<relative-path>">` and a JS snippet that does the EventSource subscription + match-and-reload.
- [ ] Test: open a page in the browser, edit the underlying `.md`, observe the page reloads.

## Notes
SSE is one-way (server → client). That's enough here — the file watcher pushes; the browser listens. WebSocket would let the browser send too, but we don't need that until / unless we add interactivity beyond reads.
