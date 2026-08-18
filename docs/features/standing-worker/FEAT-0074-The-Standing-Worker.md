---
type: "[[feature]]"
id: FEAT-0074
aliases: ["FEAT-0074"]
title: "The standing worker — acquire, select, dispatch, watch, record, release, next; with a lease that refuses and stops that hold"
status: done
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
release: "[[REL-0001-The-Human-Has-Levers]]"
related: ["[[RISK-0006-The-Unattended-Worker]]"]

---

# The standing worker

## Goal

A caller of existing machinery, not a second runtime: the shell already spawns and instruments sessions, the ledger already records dispatches, the validator already gates close-out. The driver sequences them and adds the two things sequencing needs — a claim (the lease) and a reason to stop (the conditions). Default state everywhere: **no worker**; the driver runs only where an approved DELEGATION.md exists.

## Out of Scope

- Judgment quality. The driver makes bad judgment bounded and visible; it does not make it good.
- Multi-repo. One repo clean for weeks earns the fleet loop its own phase.

## Acceptance

- [x] Selection implements LIFECYCLE step 2 and **records what it passed over and why** ([[TASK-0322]])
- [x] An empty workable backlog returns idle — a stop condition, not a busy-wait
- [x] The lease refuses a second worker **naming the holder**, and an expired lease is an escalation rather than an opening ([[TASK-0324]])
- [x] Six halt paths, each drilled; a human stop outranks every computed one; every halt carries a reason ([[TASK-0325]], [[REQ-0031]])
- [x] Failure compounds toward stopping: two failures park an item, three parked items halt
- [x] One turn checks, claims, selects, dispatches, records and **releases the lease on every path** ([[TASK-0323]])
- [x] A raising dispatcher is a failed session, not a crashed worker; an unknown outcome is a failure, not a success
- [~] *"A repo runs a week of maintenance with the human touching only the digest and the desk"* — **reconciled: not demonstrable by code.** [[RISK-0006]] requires a supervised week, and this feature can only supply the machinery for it

## Verification

`tests/test_worker.py` — 32 tests. Built in [[REQ-0031]]'s own order: *brakes are tested before the hill*, so the halt paths existed and were drilled before the loop that needs them.

**The module spawns nothing.** The dispatcher is injected, which is why every halt path was exercised without a test starting a session, and a guard asserts the file imports no `subprocess`, `threading` or `asyncio`. That guard was itself corrected: its first version searched for the *word* "spawn" and tripped on a docstring describing the property it protects — a guard that fails on prose about itself is a guard people delete.
