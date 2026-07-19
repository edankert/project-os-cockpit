---
type: "[[task]]"
id: TASK-0100
aliases: ["TASK-0100"]
title: "Discord-style workspace mini-rail (far-left)"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0015"
related: ["[[TASK-0097]]"]
tests: []
---

# Workspace mini-rail

## Definition of Done
- [ ] New `<aside id="ws-rail">` lives in grid column 1 (40 px).
- [ ] One square per workspace (initial letter + agent-state dot).
- [ ] Click switches; right-click context menu (existing handler).
- [ ] `+` button at the bottom adds (rescan / picker).
- [ ] Active workspace highlighted (accent border + indicator bar).
- [ ] Workspace tabs (`#tab-strip`) removed.
- [ ] Title-bar drag region moves to the mini-rail's top padding.

## Notes
The previous letter-pill rail (TASK-0082) had this shape — repurpose
its styles where useful. Difference: this rail is the *only* place
workspaces live, so the visual weight goes up (active gets a clear
indicator).
