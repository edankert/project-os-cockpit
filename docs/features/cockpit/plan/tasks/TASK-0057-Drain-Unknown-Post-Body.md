---
type: "[[task]]"
id: TASK-0057
aliases: ["TASK-0057"]
title: "Cockpit: drain unknown-POST body to prevent HTTP/1.1 keep-alive desync"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-23
updated: 2026-05-23
source: []
implements: ["[[FEAT-0006]]"]
fixes: []
effort: XS
due: ""
depends: ["[[TASK-0053]]"]
blocks: []
related: ["[[TASK-0055]]"]
tests: ["[[TST-0003-Unknown-Post-Drains-Body]]"]
---

# TASK-0057 — Drain unknown-POST body

## Goal
Make the cockpit server robust against `POST` requests to unknown routes so they don't poison subsequent requests on the same HTTP/1.1 keep-alive connection.

## Symptom (real-world)
After TASK-0053..0055 shipped, the cockpit JS started POSTing to `/api/cockpit/tab-state` every 15 s. Any browser tab still talking to a cockpit server that didn't yet have the new endpoint received `404` — but the server returned that 404 **without reading the request body**. The undrained body bytes sat in the socket buffer and got parsed as the start of the next request line. Innocent follow-up requests for `cockpit.css`, `cockpit.js`, `favicon.ico`, etc. on the reused TCP connection returned `501 Unsupported method ('{"tab_id":…}GET'))`. The visible effect: a completely unstyled page.

## Fix
In `server.py::_route_post`, added a `_drain_request_body()` helper that reads (and discards) `Content-Length` bytes before any early-return. Called from the unknown-route 404 path. The two real handlers (`_serve_cockpit_focus`, `_serve_cockpit_tab_state`) already read their bodies, so they're unaffected.

## Definition of Done
- [x] `_route_post` drains the body before responding 404.
- [x] Regression test pipelines a bad `POST` + a `GET /_static/cockpit.css` on a single keep-alive socket; first response is 404, second is **200 OK with the CSS** (not 501).
- [x] Full test suite green (76 / 1 skipped).

## Notes
- The fix is durable — future routes added without draining will still work, but the unknown-route fallback is now framework-safe.
- General lesson for stdlib `http.server`: any early-return path that doesn't consume `Content-Length` will desync HTTP/1.1 keep-alive. Worth remembering if a new POST handler grows an early `return` branch.
