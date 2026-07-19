---
type: "[[task]]"
id: TASK-0104
aliases: ["TASK-0104"]
title: "Per-workspace terminal sessions"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0015"
related: ["[[TASK-0063]]"]
tests: []
---

# Per-workspace terminal sessions

## Definition of Done
- [x] Main-process keeps a `Map<workspaceId, PtyRecord>` (one PTY
      per workspace for v1 — multi-session inside a workspace is
      deferred to a future task).
- [x] Terminal IPC channels (`terminal:spawn`, `terminal:write`,
      `terminal:resize`, `terminal:dispose`, `terminal:data`,
      `terminal:exit`) all carry `workspaceId`. New
      `terminal:attach` returns the backlog so the xterm can rewrite
      in place on switch.
- [x] Renderer keeps a single xterm instance + `attachedTerminalId`.
      Switching workspace re-attaches: `term.reset()` + replay
      backlog.
- [ ] Tab strip inside the terminal pane for multiple sessions per
      workspace — deferred follow-up.
- [x] PTYs persist across workspace switches; only killed on
      explicit dispose or app exit.
- [x] Backscroll: 256 KB ring buffer per PTY in main; replayed on
      attach.

## Notes
The simplest path: maintain a single xterm instance in the
renderer and clear/re-write its buffer on session switch using
each session's backlog (kept in main, sliced to a sensible
buffer cap — say 1 MB / session).

PTYs are owned by main; renderer is a view. main's session
registry survives workspace tab switches; the xterm in the
renderer is reused.
