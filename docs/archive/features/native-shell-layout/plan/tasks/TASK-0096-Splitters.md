---
type: "[[task]]"
id: TASK-0096
aliases: ["TASK-0096"]
title: "Resizable column splitters"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[CHG-20260525-FEAT-0009-Chrome-Polish]]"]
parent: "FEAT-0009"
related: []
tests: []
---

# Resizable splitters

## Definition of Done
- [x] Drag handle between rail and nav (resizes nav width).
- [x] Drag handle between centre and right pane (resizes right).
- [x] Constraints: min/max widths per column.
- [x] Persisted widths in `localStorage`.

## Notes
Lots of UX testing for what feels right (e.g. should rail itself be
resizable?). Defer until users complain about the fixed widths.

## Implementation
Two thin `.splitter` strips, absolute-positioned along the right edge
of `.ws-nav` and the left edge of `.right-pane` (z-index 50, 6 px
wide, `cursor: col-resize`). The grid template reads from CSS
variables `--nav-width` and `--right-width`; the drag handler updates
them via `appEl.style.setProperty(...)` and persists to
`cockpit:nav-width` / `cockpit:right-width`. Clamps: nav 180–480 px,
right 200–520 px. Dragging the right splitter when the pane is
collapsed is a no-op (the splitter is hidden via
`.app.right-collapsed .splitter-right`).
