---
type: "[[task]]"
id: TASK-0288
aliases: ["TASK-0288"]
title: "The runner surface — one criterion at a time, four verbs, progress named"
status: backlog
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0063-The-Acceptance-Runner]]"]
parent: "[[FEAT-0063-The-Acceptance-Runner]]"
effort: M
depends: ["[[TASK-0287]]"]
blocks: []
related: []
tests: []
---

# The runner surface

## Definition of Done

- Centre-pane walk per DES-0006: criterion text large, `Pass / Fail… / Skip-reconcile… / 📷`, progress `3 of 7`.
- Pass ticks through the tick path with the machine-composed witness; Fail opens inline issue capture pre-linked to REQ and feature; the run continues after a fail.
- Keyboard-first: enter passes, f fails, esc leaves the run resumable.
