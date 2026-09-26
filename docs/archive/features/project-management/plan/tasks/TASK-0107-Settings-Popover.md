---
type: "[[task]]"
id: TASK-0107
aliases: ["TASK-0107"]
title: "Project settings popover"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
parent: "FEAT-0016"
---

# Project settings popover

## Definition of Done
- [ ] `⋮` button to the right of the project name in the in-
      workspace nav header.
- [ ] Click opens a popover with: rename (inline input), choose
      icon, reset icon, reveal in Finder, remove from list.
- [ ] Remove triggers a `confirm()` and kills the sidecar +
      terminal PTY for the workspace on confirm.
- [ ] All edits refresh the rail + header in place.
