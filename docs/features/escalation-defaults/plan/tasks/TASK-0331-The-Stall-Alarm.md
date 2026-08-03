---
type: "[[task]]"
id: TASK-0331
aliases: ["TASK-0331"]
title: "The stall alarm — anything past twice its clock with no default joins NEEDS-YOU"
status: backlog
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0076-Escalation-With-Defaults]]"]
parent: "[[FEAT-0076-Escalation-With-Defaults]]"
effort: S
depends: ["[[TASK-0329-Timeouts-Per-Kind]]"]
blocks: []
related: []
tests: []
---

# The stall alarm

## Definition of Done

- Entries past 2× their timeout with no default, entries whose kind reserves judgment, and expired leases all surface on the landing's NEEDS-YOU with their age.
- The invariant tested by drill: construct each silent-wait candidate and show it alarms — nothing in the system can wait silently without bound.
