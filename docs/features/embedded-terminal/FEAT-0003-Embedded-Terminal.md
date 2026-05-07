---
type: "[[feature]]"
id: FEAT-0003
aliases: ["FEAT-0003"]
title: "Embedded local-only terminal (Claude Code / Codex)"
status: backlog
phase: "[[PHASE-001-MVP]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
goal: "Run an AI coding assistant alongside the docs in a single browser window — terminal panel embedded next to the rendered note, locked to the local machine."
release: ""
related: [FEAT-0001, FEAT-0002, RISK-0001]
---

# Embedded local-only terminal

## Goal
A terminal panel sits alongside the rendered docs in the same browser window so you can run `claude` (Claude Code) or `codex` while reading or editing notes — and watch the page live-reload (FEAT-0002) as the assistant edits files. The terminal endpoint is bound to `127.0.0.1` only; tablet sessions over the LAN see only the docs content, not the terminal.

## Scope
- **In scope (v1):**
  - Off by default. Opt in with a CLI flag (`--terminal`) or config field.
  - Drives [`ttyd`](https://github.com/tsl0922/ttyd) externally (the server documents how to start it; the renderer template embeds an `<iframe src="http://127.0.0.1:7681/">` when terminal is enabled).
  - Loopback-only bind enforced via `ttyd --interface lo`.
  - Renderer detects whether the docs request came from a loopback connection (request remote address); if so, includes the iframe; otherwise omits it. Tablet over LAN never sees the iframe.
  - Documented start command + sample shell wrapper that launches `ttyd claude` (or `ttyd codex`).
- **Out of scope (v1):**
  - xterm.js + WebSocket+PTY bridge — kept as v2 path. See ADR-0002.
  - Multi-session / split / tabbed terminals.
  - Authentication on the terminal endpoint (loopback bind is the security boundary).

## Acceptance
- `ttyd` running on `127.0.0.1:7681` is reachable from `curl http://127.0.0.1:7681/` on the host.
- The same URL is NOT reachable from another device on the LAN — `curl` from the tablet times out or refuses.
- A page served by the render server on `0.0.0.0:8765` displays the iframe when opened on the host browser, and does not display it when opened on the tablet.
- `claude` / `codex` runs inside the iframe and can edit `.md` files in the docs/ directory; FEAT-0002 then reloads the open page within a fraction of a second.

## Notes
Pairing this with FEAT-0002 is the killer feature: the assistant edits a note, the renderer's file watcher fires, and the page (visible right next to the terminal) updates in place — a tight authoring loop without ever leaving the browser.

The security model is set by [REQ-0005](../../requirements/REQ-0005-Terminal-Local-Only.md) and [RISK-0001](../../risks/RISK-0001-Terminal-Exposure.md). The default-off + loopback-bind combination makes accidental exposure hard.
