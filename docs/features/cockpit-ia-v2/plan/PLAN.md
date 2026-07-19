---
type: "[[plan]]"
id: PLAN-FEAT-0015
aliases: ["PLAN-FEAT-0015"]
title: "Plan — FEAT-0015 cockpit IA v2"
status: doing
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
parent: "[[FEAT-0015-Cockpit-IA-V2]]"
---

# Plan — FEAT-0015

## Sequence

1. **TASK-0105 — bug fixes.** Quick win. Convert `renderer.css`
   from `@media (prefers-color-scheme: dark)` to
   `:root[data-theme="dark"]`. Replace the mouseenter
   `renderQuickResults()` call with a targeted `.is-selected`
   class toggle.

2. **TASK-0100 — workspace mini-rail.** New `<aside id="ws-rail">`
   at column 1 (40 px wide). Render one `.ws-square` per
   workspace. Demote `#tab-strip` to a much thinner element
   (just the traffic-light reserved space + window-drag) OR
   remove it entirely; the title bar drag region moves to the
   workspace mini-rail's top padding.

3. **TASK-0101 — modes toolbar.** New `<header
   id="ws-nav-toolbar">` inside `#ws-nav`. Move the 5 mode-icon
   buttons here. Add a hide-completed toggle + a left-pane
   collapse caret on the right edge.

4. **TASK-0102 — platform pills.** Inside `#ws-nav`, below the
   toolbar. Reuse the `.platform-pill` styles from `cockpit.css`.

5. **TASK-0103 — right-pane inner-edge collapse.** Move
   `#right-pane-toggle` from the header to a small button anchored
   at the top-left of `#right-pane`, immediately inside
   `splitter-right`.

6. **TASK-0104 — per-workspace terminal.** Main-process needs
   per-workspace PTY storage (`Map<workspaceId, TerminalSession[]>`).
   IPC channels gain a `workspaceId` field. Renderer's terminal
   pane keeps a per-workspace `sessions[]` array and renders the
   active workspace's set. Switching workspaces swaps the xterm
   instance (or wraps it in a single xterm with a buffer swap —
   probably simpler to keep one xterm and rewrite to it from
   the active session's backlog).

## Notes

- The 52 px mode ribbon from FEAT-0014 goes away. The Terminal
  toggle moves to either the mini-rail (bottom) or the modes
  toolbar (right end). Pick during implementation; lean toward
  modes toolbar for "in-context" tools.
- The status footer (FEAT-0009 / TASK-0094..0096) keeps its
  splitters + theme picker; no changes there.
- Per-workspace terminal: most invasive change. The main-side
  PTY map is the single source of truth. PTYs do NOT die when
  the workspace tab loses focus — only when the workspace is
  closed (or the app exits).
