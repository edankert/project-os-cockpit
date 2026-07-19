---
type: "[[plan]]"
id: PLAN-FEAT-0014
aliases: ["PLAN-FEAT-0014"]
title: "Plan — FEAT-0014 cockpit IA rework"
status: doing
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
parent: "[[FEAT-0014-Cockpit-IA-Rework]]"
---

# Plan — FEAT-0014

## Sequence

1. **TASK-0097 — workspace tabs.** Add a `<nav id="tab-strip">`
   directly under the title-bar drag region. Render one button per
   workspace + a `+`. Keyboard: `Cmd+1..9`, `Cmd+W` close.
   Drag-to-reorder via HTML5 DnD. Agent-state dot per tab,
   re-using the existing `ws-waiting-pulse` animation. Demote the
   old `.ws-rail` to the mode ribbon (next task) — keep the IDs
   stable to avoid IPC churn.

2. **TASK-0098 — mode ribbon.** Replace the rail's workspace pills
   with a vertical icon strip. Reuse the existing 52 px column.
   Each icon is the `.type-icon` SVG already in `cockpit.css` for
   the relevant type (or a hand-picked SVG for non-type modes like
   Recent / Search). Bottom section: visually grouped, marked
   `disabled` until features land. Tooltips via `title=`.

3. **TASK-0099 — item-render port.** Lift `pickItemRenderer`,
   `renderItemStacked`, `renderItemCompact`,
   `renderItemNested`, `renderItemChildren` from `cockpit.js`.
   Port the related selectors from `cockpit.css`. Wire
   `renderRightPane` to use the same. Remove the local mini-
   renderers in `renderer.ts`.

## Notes

- Agent-state dot lives on tabs (TASK-0097) AND in the status
  footer (FEAT-0009). The tab dot is the always-visible "alert
  me" signal; the footer dot reflects the *active* workspace
  (already shipped).
- We keep `multi-window` intact — each `BrowserWindow` owns its
  tab set. `Cmd+N` still opens a new window with one tab.
- The workspace picker (`+` button) reuses
  `cockpitApi.app.workspaceManagerOpen` which already exists; no
  new main-side handler needed.
- For the item-render port we copy CSS *by selector* rather than
  inlining the whole file — drift-risk acknowledged in the
  FEAT note. Selectors needed: `.nav-item`, `.nav-item-stacked`,
  `.nav-item-compact`, `.nav-item-nested`, `.nav-item-children*`,
  `.type-icon[*]`, `.group-icon[*]`, `.status-chip[*]`,
  `.nav-title*`, `.nav-meta`, `.nav-subtitle`.
