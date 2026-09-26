---
type: "[[task]]"
id: TASK-0272
aliases: ["TASK-0272"]
title: "A status-uniform group says its status once in the head and drops the per-row chip"
status: done
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["[[FEAT-0057-The-Record-Grammar]]"]
parent: "[[FEAT-0057-The-Record-Grammar]]"
effort: S
depends: ["[[TASK-0271-One-Line-Rows-In-Both-Panes]]"]
blocks: []
related: []
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# Status said once

## Definition of Done

- A group head carries its item count, and — when every item shares one status — that status: `PHASE-007 · Agent instrumentation · 19 · done`.
- In that case the per-row chip is **not** rendered. It is one word repeated; the tasks view prints "done" 261 times today.
- A **mixed** group keeps its per-row chips and its head says the mix (`6 · 5 done`), because there the chip is the only thing distinguishing one row from another.
- Both surfaces.

## Notes

This is the record column's own move: `DECISIONS · 7 · all accepted` prints the status once for seven rows. Worth stating as a rule — **repeat a fact per-row only when it varies per-row.**

## Verification

A uniform group renders zero chips and one in its head; a mixed group renders a chip on every row. Guarded on both surfaces, since this is exactly the kind of parallel change that drifted twice in [[FEAT-0056]].
