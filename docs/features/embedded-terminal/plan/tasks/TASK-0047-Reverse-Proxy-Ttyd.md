---
type: "[[task]]"
id: TASK-0047
aliases: ["TASK-0047"]
title: "Cockpit: reverse-proxy ttyd through the cockpit (same-origin iframe + scrollbar CSS injection)"
status: done
phase: "[[PHASE-004-Embedded-Terminal]]"
owner: user:edwin
created: 2026-05-22
updated: 2026-05-22
source: []
parent: "[[FEAT-0003]]"
fixes: []
effort: M
due: ""
depends: ["[[TASK-0044]]"]
blocks: []
related: ["[[TASK-0046]]"]
tests: ["[[TST-0002]]"]
---

# TASK-0047 — Reverse-proxy ttyd through the cockpit

## Definition of Done
- [x] ttyd runs with `-b /_terminal/` so its bundled JS constructs URLs (including WebSocket) relative to that base path. All client requests come back to the cockpit at `/_terminal/*`.
- [x] Cockpit serves `/_terminal/*` by forwarding to `127.0.0.1:<ttyd-port>/_terminal/*`. Same-origin for the iframe.
- [x] HTTP proxy: `terminal_proxy.proxy_http()` uses `http.client` to forward GETs verbatim; intercepts the index HTML to inject muted scrollbar CSS before `</head>`.
- [x] WebSocket proxy: `terminal_proxy.proxy_websocket()` handles the upgrade — opens a raw socket to ttyd, performs its own upgrade, computes the browser-facing Sec-WebSocket-Accept, then runs bidirectional byte forwarding with two daemon threads (`_bidirectional_forward`). No new pip deps.
- [x] `/api/terminal` returns `{"url": "/_terminal/"}` (same-origin relative path) instead of the direct ttyd port.
- [x] Tests cover: ws_accept against the RFC 6455 example; HTML injection before `</head>`; pass-through for non-HTML; case-insensitive matching; double-injection safety.

## Steps
- [x] terminal.py: added `TERMINAL_BASE_PATH = "/_terminal/"`; ttyd argv gains `-b /_terminal`; `info()` returns the relative URL.
- [x] terminal_proxy.py: new module with `ws_accept`, `inject_html_extras`, `proxy_http`, `proxy_websocket`, `_bidirectional_forward`.
- [x] server.py: imports `terminal_proxy` + `TERMINAL_BASE_PATH`; new route handler `_proxy_terminal()` dispatches on `Upgrade: websocket`.
- [x] tests/test_terminal_proxy.py — five focused cases on the pure pieces.

## Notes
- The proxy adds ~150 LOC of stdlib-only code. Two daemon threads per active terminal session (one per direction).
- Browser ↔ cockpit and cockpit ↔ ttyd both run on `127.0.0.1`; REQ-0005 (terminal on loopback only) is unchanged.
- Same-origin unlocks future work:
  - Injecting a small JS bridge so xterm.js events (`onData`, `onTitleChange`, …) postMessage the parent cockpit page. Direct improvement over the file-watcher proxy in TASK-0046.
  - Custom keyboard shortcuts that take precedence over the terminal (Cmd+B left-pane, Cmd+J terminal-toggle, …).
  - Theme follow-along when the cockpit's light/dark switch fires (postMessage → xterm.js theme update, no ttyd restart needed).
  - Send-to-terminal from cockpit chrome (right-click a file → "Send path to terminal").
- The HTML injection helper is generic enough to layer additional `<style>` / `<script>` blocks later.
