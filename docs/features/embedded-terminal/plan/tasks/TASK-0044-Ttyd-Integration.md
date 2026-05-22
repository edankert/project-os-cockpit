---
type: "[[task]]"
id: TASK-0044
aliases: ["TASK-0044"]
title: "Cockpit: ttyd integration — embedded LLM CLI terminal in the bottom panel"
status: backlog
phase: "[[PHASE-004-Embedded-Terminal]]"
owner: user:edwin
created: 2026-05-22
updated: 2026-05-22
source: []
implements: ["[[FEAT-0003]]", "[[REQ-0005]]"]
fixes: []
effort: M
due: ""
depends: ["[[TASK-0043]]"]
blocks: []
related: ["[[ADR-0002]]"]
tests: []
---

# TASK-0044 — ttyd integration

## Goal
Spawn `ttyd` as a child process bound to `127.0.0.1`, embed its UI in an iframe inside the cockpit's bottom-panel "Terminal" tab. The user types in any LLM CLI (claude-code, codex, gemini-cli, or just `bash`) and the existing watcher → SSE pipeline propagates the LLM's file edits to the cockpit's side panes in real time.

## Definition of Done
- [ ] `ttyd` is an optional install extra: `pip install project-os-cockpit[terminal]`. Base install stays light.
- [ ] Cockpit server checks for `ttyd` on disk at startup; if present, exposes the Terminal tab. Otherwise the tab is hidden / shows a small "install ttyd to enable" message.
- [ ] Server spawns `ttyd -i 127.0.0.1 -p <random-port> <shell-or-cli>` as a child process when the bottom-panel Terminal tab is mounted.
- [ ] The configured command defaults to the user's shell (`$SHELL`). Project-os config can override with the preferred LLM CLI (`claude-code`, `codex`, `gemini-cli`).
- [ ] iframe `src="http://127.0.0.1:<port>"` rendered in the Terminal tab body.
- [ ] Terminal binds **only** to 127.0.0.1, never 0.0.0.0 — enforces REQ-0005. Test for this in the startup logic.
- [ ] Clean shutdown: ttyd child process is killed when the cockpit server exits (signal handlers / atexit).
- [ ] Working directory of the spawned shell defaults to the project root (so the LLM CLI sees the project).
- [ ] Tests: spawn helper unit-tested (mocked subprocess), bind-address assertion, port allocation, lifecycle.

## Steps
- [ ] Add `ttyd` as an optional dependency in `pyproject.toml` (extras: `[terminal]`). Document install in README.
- [ ] New `src/project_os_cockpit/terminal.py` module: `class TerminalProcess` (spawn / health-check / shutdown). Allocate a free local port via `socket`.
- [ ] Wire into `server.py`: register signal handlers + atexit cleanup. Expose `GET /api/terminal` returning `{enabled, url, command}`.
- [ ] JS: in the Terminal tab, fetch `/api/terminal`; if enabled, render `<iframe src=…>`; else show the install hint.
- [ ] Project-os config: `cockpit.terminal.command: ["claude-code"]` (or similar). Validation: reject commands containing shell metacharacters from frontmatter to avoid surprise injection.
- [ ] Tests: `tests/test_terminal.py` — port allocation, bind-address, command-validation.

## Notes
- ADR-0002 already weighed ttyd vs xterm.js+PTY-bridge. ttyd is the lighter choice.
- This is the v1 path. v2 / desktop wrapper (Tauri) is parked — the same web cockpit code can be reused inside a Tauri shell later without rewrite.
- Spawning the LLM CLI is the user's choice; the cockpit just hosts whatever command is configured. Default to `$SHELL` so the install works without any LLM CLI present.
- Future: command palette / session multiplexing would need a PTY bridge instead of ttyd. Defer.
