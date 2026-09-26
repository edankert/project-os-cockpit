---
type: "[[task]]"
id: TASK-0103
aliases: ["TASK-0103"]
title: "Right-pane collapse caret on the inner (left) edge"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0015"
related: ["[[TASK-0085]]"]
tests: []
---

# Right-pane inner-edge collapse

## Definition of Done
- [ ] `#right-pane-toggle` moves out of `.right-pane-header`.
- [ ] Placed as an absolute button anchored to the top-left of
      `#right-pane`, immediately to the right of splitter-right.
- [ ] Chevron flips direction based on collapsed state.
- [ ] When collapsed, the button remains visible (28 px column
      shows just the button vertically centered).

## Notes
Symmetric with the left-pane collapse caret on the right edge of
the modes toolbar (TASK-0101). Reachable next to the splitter
where the user is already aiming for the resize.
