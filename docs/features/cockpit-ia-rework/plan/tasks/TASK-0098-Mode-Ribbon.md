---
type: "[[task]]"
id: TASK-0098
aliases: ["TASK-0098"]
title: "Mode ribbon (52 px vertical icon strip on the left)"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0014"
related: ["[[TASK-0083]]", "[[TASK-0084]]"]
tests: []
---

# Mode ribbon

## Definition of Done
- [x] Existing 52 px left column becomes the mode ribbon (no
      workspace pills — those moved to tabs in TASK-0097).
- [x] Top section: 5 nav modes, vertical, top-down — Features,
      Tasks, Issues, Library, Recent.
- [x] Bottom section: Search, Pinned, Graph view (disabled). A
      separate Tools section pins Terminal (active) + Settings
      (disabled) at the bottom.
- [x] Active mode visually highlighted (accent-soft background +
      accent left-bar via `.ribbon-btn.active::before`).
- [x] Tooltips via `title="…"`.
- [x] Clicking a mode icon swaps the nav panel content.

## Notes
Icons sourced from existing `.type-icon` / `.group-icon` SVGs
where the mode maps onto a project-os type (Features → feature
diamond, Tasks → task square, Issues → bug, Library → book,
Recent → clock). New SVGs only for non-type modes in the bottom
section.

The current in-panel mode-pill row gets deleted (it was
`#ws-nav-modes`).
