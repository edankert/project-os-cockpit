---
type: "[[task]]"
id: TASK-0304
aliases: ["TASK-0304"]
title: "The cockpit measures itself — the by-hand CDP loop made a feature"
status: backlog
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0068-The-Measure-View]]"]
parent: "[[FEAT-0068-The-Measure-View]]"
effort: M
depends: ["[[TASK-0303]]"]
blocks: []
related: []
tests: []
---

# The cockpit measures itself

## Definition of Done

- The shell injects the same probe into its own webContents; any visible cockpit surface can be a measure pane.
- Explicitly scoped to self: no external targets (the phase's out-of-scope, restated where the code would grow it).
