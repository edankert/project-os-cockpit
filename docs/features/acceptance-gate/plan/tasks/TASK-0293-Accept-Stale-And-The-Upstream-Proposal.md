---
type: "[[task]]"
id: TASK-0293
aliases: ["TASK-0293"]
title: "The ACCEPT-STALE warning, and the convention proposed upstream"
status: backlog
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0064-The-Acceptance-Gate]]"]
parent: "[[FEAT-0064-The-Acceptance-Gate]]"
effort: S
depends: ["[[TASK-0291]]"]
blocks: []
related: []
tests: []
---

# The ACCEPT-STALE warning, and the convention proposed upstream

## Definition of Done

- Local validator warning when `done` + `requested` exceeds the age threshold; warning not error, per the phase's rubber-stamp argument.
- The upstream proposal note files the field, the stamp discipline and the warning with project-os — the close-out-rule route.
