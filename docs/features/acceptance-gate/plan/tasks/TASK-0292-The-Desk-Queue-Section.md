---
type: "[[task]]"
id: TASK-0292
aliases: ["TASK-0292"]
title: "Awaiting your acceptance — the queue's most human section, first"
status: done
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0064-The-Acceptance-Gate]]"]
parent: "[[FEAT-0064-The-Acceptance-Gate]]"
effort: S
depends: ["[[TASK-0291]]"]
blocks: []
related: []
tests: []
---

# Awaiting your acceptance

## Definition of Done

- Features at `acceptance: requested` render above Changes requested with age; opening one starts the runner.
- Empty state follows FEAT-0073's voice.

## Done — 2026-08-11, re-homed rather than built where it was specified

Written for **the desk queue**, which [[ADR-0020]] retired and [[FEAT-0090]] removed. The obligation now lives with its subject, which is that ADR's rule.

- **The marker**: a feature at `acceptance: requested` is flagged owed by the obligation registry and counted on the Features badge ([[FEAT-0088]], [[FEAT-0089]]).
- **The offer**: the feature note's actuator row carries `▶ Accept…`, opening `~accept/<id>` ([[TASK-0288]]). This closes the door-to-nothing [[REL-0001]] recorded as reconciled-not-ticked — *"a feature at `acceptance: requested` is marked but offers no run… A door to nothing teaches the reader the feature works."*
- **The empty state**: nothing renders when nothing is requested, which is [[FEAT-0073]]'s voice applied by absence rather than by a sentence — an `Awaiting your acceptance · 0` band would be the permanent zero this surface has been taught about twice.

*"Above Changes requested"* and *"with age"* do not survive the re-homing: there is no queue to sit above, and the age question is answered corpus-wide by `ACCEPT-STALE` ([[TASK-0293]]) rather than per row.
