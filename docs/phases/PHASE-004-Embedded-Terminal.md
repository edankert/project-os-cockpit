---
type: "[[phase]]"
id: PHASE-004
aliases: ["PHASE-004"]
title: "Embedded terminal"
status: done
order: 4
owner: user:edwin
created: 2026-05-08
updated: 2026-09-16
features:
  - "[[FEAT-0003-Embedded-Terminal]]"
issues:
  - "[[ISS-0255]]"
  - "[[ISS-0310]]"
  - "[[ISS-0311]]"
depends: ["[[PHASE-001-MVP]]"]
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

## Original exit criteria (2026-05)
- `python -m project_os_cockpit <docs> --terminal --terminal-bind 127.0.0.1 --terminal-port 7681` starts the docs server and can be paired with `ttyd --interface lo --port 7681 claude`.
- Host browser sees the docs + iframe; LAN tablet sees the docs only.
- Editing a `.md` from inside `claude`/`codex` triggers FEAT-0002's soft-reload of the corresponding open page.

## Exit Criteria

- [x] The console keeps earlier Codex and plain-shell output reachable through its History action and wheel input. The isolated Electron walk moved through 120 numbered shell lines in tmux history ([[TASK-0627]], [[ISS-0310]]).
- [x] History remains reachable after switching to another workspace and back. A DevTools wheel gesture moved the displayed tmux history after reattachment ([[TASK-0627]], [[ISS-0310]]).
- [x] Claude keeps its alternate screen and mouse input after reattachment. The real Claude CLI remained in tmux's alternate screen with mouse tracking enabled after a workspace switch ([[TASK-0627]]).
- [x] Ending Codex returns to a working shell prompt while the Electron window stays open. The real Codex CLI exited with `/exit`, and a later shell command ran in the same console ([[TASK-0627]], [[ISS-0311]]).

## Dependencies
PHASE-001 (renderer + live reload). Independent of PHASE-002 (cockpit) and PHASE-003 (downstream pilot) — can land in any order alongside them.

## Notes
Originally scoped under PHASE-001 (MVP). Pulled out to a dedicated phase so PHASE-001 could close cleanly on the renderer + live-reload combination, which is the genuinely-MVP useful tool. The terminal is high-value but optional sugar.

## Close-out (2026-07-20)

The embedded local-only terminal is complete and closed (FEAT-0003): xterm + per-workspace local PTY (loopback-only by construction), tmux survivability, and the ttyd reverse-proxy path. The preview-tab nice-to-have (TASK-0045) is deferred to PHASE-999. The terminal scrollback and Codex-exit repair is temporarily reopening this standing home through [[TASK-0627]].

## Reopened and re-closed (2026-08-25) — [[ISS-0255]]

This is the terminal's **standing home** (`CLAUDE.md`, "When to open a phase — and when not to"): a single reported defect gets an `ISS-*` and a task here, not a phase of its own. Reopened to `active` for the day and closed again the same session, which is what the rule asks for — a phase left permanently `active` because its home must be "known" reads as one somebody forgot.

The defect: the console clipped its last line and its last two columns, because `@xterm/addon-fit` measures the fit parent's *border* box under this renderer's global `box-sizing: border-box` and `.terminal-mount` carried padding the terminal could not use. Fixed in [[TASK-0577]] by moving the inset to `.terminal-pane`; pinned by [[TST-0078]]; recorded in [[CHG-20260825-The-Console-Stops-Clipping-Its-Last-Line]].

## Re-closed 2026-09-16

[[TASK-0627]] completed the terminal scrollback and Codex exit walk in an isolated rebuilt Electron copy. [[ISS-0310]] and [[ISS-0311]] are fixed. The test copy used its own user data and tmux socket; both temporary tmux sessions were disposed after the walk.

Distinct from [[ISS-0016]], which was a *stale* fit and whose `ResizeObserver` remedy still holds. Two defects, one symptom — which is why the second one took a measurement rather than a memory to find.
