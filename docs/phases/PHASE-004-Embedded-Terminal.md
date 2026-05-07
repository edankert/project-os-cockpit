---
type: "[[phase]]"
id: PHASE-004
aliases: ["PHASE-004"]
title: "Embedded terminal"
status: backlog
order: 4
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
features:
  - "[[FEAT-0003-Embedded-Terminal]]"
depends_on: ["[[PHASE-001-MVP]]"]
---

# Phase 4: Embedded terminal

## Goal
Add the optional embedded local-only terminal panel — `ttyd`-driven by default, loopback-bound, off by default — so the docs viewer can run `claude` / `codex` next to the rendered notes in the same browser window. Pairs with FEAT-0002's live reload so the assistant's edits are visible as soon as it saves.

## Scope

### In scope
- FEAT-0003 — opt-in iframe over `ttyd` bound to `127.0.0.1` only.
- Renderer's request-origin detection so the iframe is included only on loopback connections (tablet over LAN sees the docs without the terminal).

### Out of scope
- xterm.js + WebSocket+PTY bridge (kept as a v2 path; see ADR-0002).
- Multi-session / split / tabbed terminals.
- Authentication on the terminal endpoint (loopback bind is the security boundary).

## Exit criteria
- `python -m project_os_cockpit <docs> --terminal --terminal-bind 127.0.0.1 --terminal-port 7681` starts the docs server and can be paired with `ttyd --interface lo --port 7681 claude`.
- Host browser sees the docs + iframe; LAN tablet sees the docs only.
- Editing a `.md` from inside `claude`/`codex` triggers FEAT-0002's soft-reload of the corresponding open page.

## Dependencies
PHASE-001 (renderer + live reload). Independent of PHASE-002 (cockpit) and PHASE-003 (downstream pilot) — can land in any order alongside them.

## Notes
Originally scoped under PHASE-001 (MVP). Pulled out to a dedicated phase so PHASE-001 could close cleanly on the renderer + live-reload combination, which is the genuinely-MVP useful tool. The terminal is high-value but optional sugar.
