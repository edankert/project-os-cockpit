---
type: "[[feature]]"
id: FEAT-0074
aliases: ["FEAT-0074"]
title: "The standing worker — acquire, select, dispatch, watch, record, release, next; with a lease that refuses and stops that hold"
status: doing
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[DES-0009-The-Standing-Worker]]"]
goal: "The driver: LIFECYCLE's own selection rule as code with a reasoned ledger entry per choice, sessions dispatched through the existing instrumented terminals, a lease that makes two workers a refusal rather than a race, and stop conditions proven by drill."
requirements: ["[[REQ-0030-The-Worker-Never-Outruns-Its-Policy]]", "[[REQ-0031-The-Loop-Always-Halts]]"]
tasks:
  - "[[TASK-0322-Selection-With-Reasons]]"
  - "[[TASK-0323-The-Session-Loop]]"
  - "[[TASK-0324-The-Lease]]"
  - "[[TASK-0325-Stop-Conditions-By-Drill]]"
release: ""
related: ["[[RISK-0006-The-Unattended-Worker]]"]
tests: []
---

# The standing worker

## Goal

A caller of existing machinery, not a second runtime: the shell already spawns and instruments sessions, the ledger already records dispatches, the validator already gates close-out. The driver sequences them and adds the two things sequencing needs — a claim (the lease) and a reason to stop (the conditions). Default state everywhere: **no worker**; the driver runs only where an approved DELEGATION.md exists.

## Out of Scope

- Judgment quality. The driver makes bad judgment bounded and visible; it does not make it good.
- Multi-repo. One repo clean for weeks earns the fleet loop its own phase.
