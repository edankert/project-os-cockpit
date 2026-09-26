---
type: "[[task]]"
id: TASK-0064
aliases: ["TASK-0064"]
title: "App chrome — menu, single-instance, deep links, agent-focus bridge, window memory"
status: done
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-05-24
updated: 2026-05-24
source: []
parent: "FEAT-0007"
effort: ""
due: ""
depends: ["[[TASK-0061]]"]
blocks: []
related: []
tests: []
---

# App chrome

## Definition of Done
- [ ] macOS menu bar: File (Open Workspace…, Rescan, Quit), View (Reload,
      Toggle Terminal), Window (workspace list), Help.
- [ ] `app.requestSingleInstanceLock()` — a second launch focuses an
      existing window or opens a workspace from argv.
- [ ] `cockpit://<workspace-id>/<target>` protocol registered;
      handler routes through the agent-focus channel.
- [ ] Main process subscribes to each sidecar's `/_events` SSE; forwards
      `agent_focus` events to the matching renderer via `agent.onFocus`.
      Verifies that `cockpit focus FEAT-0006` from an external terminal
      drives the desktop window.
- [ ] Window position and size persisted per workspace under userData.

## Steps
- [ ] `electron/menu/app-menu.ts` — `Menu.setApplicationMenu(...)`.
- [ ] Single-instance lock in main bootstrap; `second-instance` handler
      parses argv and focuses / opens the relevant window.
- [ ] `app.setAsDefaultProtocolClient('cockpit')`; `open-url` (macOS) +
      argv (Windows/Linux) handlers parse the URL.
- [ ] `electron/ipc/agent-focus.ts` — `EventSource` per active sidecar,
      forwards `agent_focus` events.
- [ ] Window-state persistence (use `electron-window-state` or roll a
      small util).

## Notes
This is the "make it feel like a real app" task. Each item is small but
the collection is what differentiates the desktop shell from a wrapped
website.
