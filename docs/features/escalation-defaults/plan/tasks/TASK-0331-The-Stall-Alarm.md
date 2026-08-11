---
type: "[[task]]"
id: TASK-0331
aliases: ["TASK-0331"]
title: "The stall alarm — anything past twice its clock with no default joins NEEDS-YOU"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
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

## Done — 2026-08-11

**The invariant is tested by drill**, as the DoD asks: every silent-wait candidate is constructed and shown to land in a visible state — long-lapsed, timeout-less, unknown-kind, timestamp-less, and brand-new.

`waiting` counts as visible: the entry sits in the queue with its age and the human sees the clock. What must never exist is a state that is neither actionable nor observable.

`sweep()` asserts the stronger property — **every entry is accounted for**, because an entry the sweep dropped is an entry waiting silently, and a sweep that quietly skipped a shape would look identical to one that handled it.

The alarm path covers entries past twice their timeout with no default and kinds that reserve judgment. Expired leases join it when [[FEAT-0074]] introduces leases — that feature is gated on [[REQ-0030]]/[[REQ-0031]], which are still `draft`.
