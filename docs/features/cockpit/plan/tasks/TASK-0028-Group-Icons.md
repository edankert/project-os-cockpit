---
type: "[[task]]"
id: TASK-0028
aliases: ["TASK-0028"]
title: "Cockpit: type-aware group icons in left-pane group headers"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-09
updated: 2026-05-23
source: []
parent: "[[FEAT-0006]]"
fixes: []
effort: S
due: ""
depends: ["[[TASK-0023]]"]
blocks: ["[[TASK-0029]]"]
related: []
tests: ["[[TST-0002]]"]
---

# TASK-0028 — Type-aware group icons per nav mode

## Definition of Done
- [x] Each left-pane group header carries an icon between the chevron and the label.
- [x] Library mode:
  - [x] `pinned` → star
  - [x] `docs-tree` → folder-tree
  - [x] `rare:<type>` → matching type icon (per-type colour reused via `[data-type]`)
- [x] Features mode → layers icon (phase grouping marker).
- [x] Tasks mode → list-checks icon.
- [x] Issues mode → alert-octagon (same shape as the issue type icon).
- [x] Recent mode → clock icon.
- [x] Section icons sit in muted neutral; rare-type icons keep their per-type colour.

## Steps
- [x] Added `GROUP_ICONS` table + `makeGroupIconSvg` + `groupIcon(mode, group)` to `cockpit.js`.
- [x] Mounted `groupIcon(mode, g)` as the first headerChildren entry in `renderLeftPane`.
- [x] Added `.group-icon` CSS — neutral muted colour, flex-shrink 0, vertical-align tweak.
- [x] Updated `.group-header-inner` to `align-items: center` so icons line up with text.

## Notes
Status groups in Tasks mode already carry the right-aligned status chip — the left icon doesn't repeat that, it just marks the section as a task list. Same idea for the issues alert-octagon vs the severity label on the right.
