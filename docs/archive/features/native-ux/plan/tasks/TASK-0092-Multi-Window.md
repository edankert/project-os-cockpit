---
type: "[[task]]"
id: TASK-0092
aliases: ["TASK-0092"]
title: "Multi-window + per-workspace window state"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0012"
effort: ""
due: ""
depends: ["[[TASK-0058]]"]
blocks: []
related: []
tests: []
---

# Multi-window + per-workspace window state

## Definition of Done
- [ ] ⌘N opens a new BrowserWindow showing a workspace picker.
- [ ] Each window has its own sidecar (already supported by
      FEAT-0007's per-window model — just need a second window).
- [ ] Window menu lists all open windows by workspace name; click
      brings the named window to the front.
- [ ] Window position + size persists **per workspace**; layered
      on top of the existing app-wide state from TASK-0064.
- [ ] Closing the last window quits on non-macOS / keeps app alive
      on macOS (existing behaviour, unchanged).

## Steps
- [ ] `windows/workspace-window.ts` — extract the BrowserWindow
      creation into a function that can be called more than once.
- [ ] Per-workspace state persistence — extend
      `window-state.ts` to key by workspace ID; fall back to
      app-wide default when no per-workspace record yet.
- [ ] Menu: rebuild the Window submenu dynamically as windows
      open/close.
