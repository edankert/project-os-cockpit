---
type: "[[task]]"
id: TASK-0137
aliases: ["TASK-0137"]
title: "Status-aware verbs — when-lists in the registry, filtered menus"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
parent: "[[FEAT-0026-Verb-Polish]]"
effort: "S"
depends: []
blocks: []
related: []
tests: ["[[TST-0014]]"]
---

# Status-aware verbs

## Definition of Done
- [x] Registry entries accept `when: [statuses]`; defaults carry sensible lists (implement not on done/cancelled, close-out not on backlog).
- [x] Menus filter by the row's status everywhere verbs surface; entries without `when` always show.
