---
type: "[[adr]]"
id: ADR-0002
aliases: ["ADR-0002"]
title: "Embedded terminal: ttyd via iframe vs xterm.js+pty bridge"
status: accepted
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
deciders: ["user:edwin"]
related: ["[[FEAT-0003]]"]
---

# ADR-0002 — Terminal embedding approach

## Context
The embedded-terminal feature ([[FEAT-0003]]) needs a way to run an interactive shell (or a command like `claude` / `codex`) inside the docs-server browser window. Two well-trodden paths:

1. **`ttyd` via iframe** — a separate `ttyd` process wraps any command as a web terminal, listens on a port, served via a small `<iframe>` in the docs page.
2. **`xterm.js` + Python WebSocket-to-PTY bridge** — embed the same terminal engine VS Code uses, run a PTY in the docs-server process, bridge stdin/stdout over a WebSocket.

## Decision
v1: ship `ttyd` via iframe. Document `xterm.js + WebSocket+PTY` as the v2 path; revisit if v1's UX limitations bite.

## Consequences

### Positive (v1 ttyd-iframe)
- **Trivial integration.** ~15 minutes from "install ttyd" to "iframe in the page". A single binary handles all the hard parts (PTY, ANSI, resize, clipboard).
- **Reliable.** Mature project; many users.
- **Isolation.** The `ttyd` process is independent of the render server; if it crashes, the docs server is unaffected.
- **Loopback bind built in.** `ttyd --interface lo` does exactly what [[REQ-0005]] requires.

### Negative (v1 ttyd-iframe)
- **Two processes to manage.** Need to start `ttyd` separately. Docs-server can document or wrap the launch, but it's not "one process does everything".
- **No tight UI integration.** The iframe is an opaque rectangle; we can't easily integrate keyboard shortcuts, sync the terminal CWD with the currently-viewed note, or split into multiple panes.
- **Authentication is `ttyd`'s problem.** We rely on the loopback bind for security; `ttyd` can also do basic auth, but adding that is out of scope.

### Migrating to v2 (xterm.js + bridge)
If v1's UX limits start to matter, we'd:
- Add `xterm.js` as a frontend dep (single ~600KB JS file).
- Spawn a PTY in the docs-server using `pty.openpty()` + a subprocess running the configured command.
- Bridge over a WebSocket endpoint on `127.0.0.1` only.
- Get tight UI control: split panes, multiple sessions, sync CWD with the viewed note's parent directory.

The migration is well-scoped (~300 lines) and doesn't break the v1 user experience because the iframe URL would just become a relative path served by docs-server itself.

## Status
Accepted. Revisit when v1 ships and UX feedback tells us whether the iframe limits matter in practice.
