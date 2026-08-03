---
type: "[[feature]]"
id: FEAT-0059
aliases: ["FEAT-0059"]
title: "note_writes widens: the human-owned transition table as data, criteria ticks, and issue creation — behind the guards it already has"
status: planned
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[DES-0005-The-Actuator-Grammar]]"]
goal: "Extend the existing guarded writer with the three verbs the actuator grammar needs — transition, tick, create — each behind the same allow-lists, mtime preconditions and loopback checks the module already enforces."
requirements: ["[[REQ-0026-Only-Human-Owned-Transitions]]", "[[REQ-0027-Every-Write-Guarded]]"]
tasks:
  - "[[TASK-0278-The-Transition-Table-As-Data]]"
  - "[[TASK-0279-The-Tick-Path]]"
  - "[[TASK-0280-Create-Issue-And-The-Hardening-Suite]]"
release: ""
related: ["[[RISK-0005-The-Write-Surface]]"]
tests: []
---

# The write service widens

## Goal

`note_writes.py` already holds the whole discipline — field allow-lists, `DECIDE_TRANSITIONS`, mtime preconditions, path canonicalisation, atomic writes, loopback-only callers. Three verbs join it: **transition** (the human-owned table from [[DES-0005]]'s matrix, one dict, one module), **tick** (a single criterion line rewritten in the exact `[x] … — evidence:` / `[~]` shapes REQ-BOXES and PHASE-BOXES validate), and **create** (an issue from its template, next ID from the index).

## Why this is the foundation

Every other feature in PHASE-023 and the PHASE-024 runner calls these three verbs. Building them first, server-side, with the mutation-grade test suite, means the renderer work that follows is display only.

## Out of Scope

- Any agent-owned transition — refused by the table's absence, tested by mutation.
- Generic frontmatter or prose editing.
- Creating any type but issue. Each further type earns its own review of what "next ID" and "which template" mean.
