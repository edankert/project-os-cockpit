---
type: "[[change]]"
id: CHG-20260522-Cockpit-Reverse-Proxy-Ttyd
aliases: ["CHG-20260522-Cockpit-Reverse-Proxy-Ttyd"]
title: "Cockpit: reverse-proxy ttyd through the cockpit (same-origin iframe + scrollbar CSS injection)"
status: merged
owner: user:edwin
created: 2026-05-22
updated: 2026-05-22
source: ["[[TASK-0047]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/terminal.py"
  - "src/project_os_cockpit/terminal_proxy.py"
  - "src/project_os_cockpit/server.py"
  - "tests/test_terminal_proxy.py"
issues: []
features: ["[[FEAT-0003]]"]
related: ["[[REQ-0005]]", "[[ADR-0002]]"]
---

# Cockpit: reverse-proxy ttyd

## Summary
The embedded terminal is no longer reached via its own loopback port — the cockpit serves ttyd through `/_terminal/*` so the iframe is **same-origin** with the rest of the cockpit page. Immediate payoff: we inject muted scrollbar CSS into ttyd's index HTML (couldn't reach it before — different origin). Bigger payoff: a clean foundation for terminal ↔ cockpit communication via `postMessage` (keyboard shortcuts, theme sync, output-driven tab indicator, …).

## Implementation

### `terminal.py`
- ttyd spawn gains `-b /_terminal/` so its bundled JS constructs WebSocket + asset URLs relative to that base path. Every client request now comes back to the cockpit instead of bypassing it.
- `TerminalProcess.info()` returns the relative URL `/_terminal/` (was the direct `http://127.0.0.1:<ttyd-port>`). The browser still hits the cockpit's address.

### `terminal_proxy.py` (new, ~250 LOC)
- `ws_accept(key)` — RFC 6455 §1.3 SHA1 + base64 of `key + magic-GUID`.
- `inject_html_extras(body)` — finds `</head>` (case-insensitive), inserts a `<style>` block with `.xterm .xterm-viewport::-webkit-scrollbar` rules + Firefox `scrollbar-width: thin; scrollbar-color: …`. Pass-through for non-HTML responses (the JS bundle, fonts, etc.).
- `proxy_http(handler, ttyd_port, path)` — `http.client.HTTPConnection` to ttyd, copies headers (drops hop-by-hop), reads response, runs `inject_html_extras` when `Content-Type` is HTML, relays to the browser.
- `proxy_websocket(handler, ttyd_port, path)` — two-half handshake:
  1. Open raw TCP socket to ttyd, send our own `GET /_terminal/ws HTTP/1.1` upgrade with a fresh key; expect `HTTP/1.1 101`.
  2. Compute `Sec-WebSocket-Accept` from the browser's original key, write the 101 directly via `handler.wfile`.
  Then `_bidirectional_forward` shuttles bytes between `handler.rfile`/`handler.connection` and the ttyd socket with two daemon threads. No frame parsing — bytes pass through.

### `server.py`
- Imports `terminal_proxy` + `TERMINAL_BASE_PATH`.
- New route: any path under `/_terminal/` dispatches to `_proxy_terminal()`, which lazy-starts ttyd, picks `proxy_websocket` when the request carries `Upgrade: websocket`, else `proxy_http`.

### Tests
- `tests/test_terminal_proxy.py` (5 cases): RFC-example accept value, injection before `</head>`, non-HTML pass-through, case-insensitive HEAD match, idempotent safety.
- 68 passing / 1 skipped (was 63 / 1; +5).

### Security
- ttyd still binds to `127.0.0.1` only (REQ-0005 holds). The cockpit reverse-proxies from loopback to loopback — nothing reaches the LAN.
- ttyd's default origin check is off; with the proxy in front, all requests now legitimately originate from the cockpit's host.
- No new pip deps. Stdlib `http.client` + `socket` + `threading` only.

## What this unlocks (next-task seeds)

Same-origin parent + iframe means JS injected into the iframe can `postMessage` the parent. Four concrete follow-ups now cheap:

1. **Output-driven tab indicator** (improves TASK-0046): inject ~30 LOC into ttyd's HTML hooking `terminal.onData` → `parent.postMessage({type:"terminal:data"})`. Cockpit fires the title + favicon indicator on real output, not just file changes.
2. **Custom keyboard shortcuts**: intercept Cmd+B / Cmd+J / etc. in the iframe before xterm consumes them.
3. **Theme follow-along**: when the cockpit's light/dark switch fires, parent → iframe `postMessage` updates xterm.js theme on the fly (no ttyd restart needed; today the terminal is permanently dark).
4. **Send-to-terminal from chrome**: right-click a file in the nav → "Send path to terminal" via postMessage.

## Follow-ups
- [ ] Scaffold a JS-bridge task (TASK-0048) implementing items 1–4 above.
- [ ] Consider exposing ttyd's `-T` (terminal-type) and `-O` (origin-check) as project-os config knobs once the bridge is in.

## Documentation Coverage (All Types Considered)
- features: updated (FEAT-0003 already in-progress)
- requirements: REQ-0005 still satisfied (loopback-only); no change
- tasks: new ([[TASK-0047]])
- issues: not-applicable
- tests: new (`tests/test_terminal_proxy.py`)
- workflows: not-applicable
- decisions: not-applicable (ADR-0002 picked ttyd; proxy is an integration layer, not a redesign)
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 46→47, focus.task → TASK-0047, metrics tasks_total 46→47 / tasks_done 37→38, items.changes addition)
