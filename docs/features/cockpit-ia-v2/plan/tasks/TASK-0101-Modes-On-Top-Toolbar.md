---
type: "[[task]]"
id: TASK-0101
aliases: ["TASK-0101"]
title: "Modes-on-top toolbar with inner-edge collapse"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0015"
related: ["[[TASK-0098]]"]
tests: []
---

# Modes-on-top toolbar

## Definition of Done
- [ ] `<header id="ws-nav-toolbar">` sits at top of `#ws-nav`.
- [ ] 5 mode icons left-grouped: Features, Tasks, Issues, Library,
      Recent. Icons reuse those from FEAT-0014's ribbon.
- [ ] Hide-completed toggle (eye-strike icon) follows the modes.
- [ ] Left-pane collapse caret on the far right, immediately
      adjacent to splitter-nav.
- [ ] Active mode highlighted (accent-soft background).
- [ ] The 52 px left ribbon goes away — its column collapses.

## Notes
The terminal-toggle icon currently lives on the ribbon. It moves
to the modes toolbar (right of hide-completed) so toolbar = nav
context + nav actions.
