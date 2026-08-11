---
type: "[[phase]]"
id: PHASE-031
aliases: ["PHASE-031"]
title: "The supervised week — the worker runs, a human watches daily, and the risk closes on evidence rather than on confidence"
status: planned
order: 31
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
goal: "Run the standing worker under daily human supervision for a week, and close RISK-0006 on what the ledger actually shows — the one thing PHASE-027's machinery cannot supply for itself."
features: []
requirements: []
tasks: []
issues: []
risks: ["[[RISK-0006-The-Unattended-Worker]]"]
related: ["[[PHASE-027-The-Standing-Worker]]", "[[RISK-0006-The-Unattended-Worker]]", "[[REL-0001-The-Human-Has-Levers]]", "[[ADR-0009-The-Principal-Is-A-Role]]"]
tags: [phase]
---

# The supervised week

## Why this phase exists

[[PHASE-027]] built every mechanism an unattended worker needs and could not supply the one thing that makes it safe to trust: **evidence that it behaves**. [[RISK-0006]] states the standard in its own words —

> This risk closes when a repo has run a **supervised** week — worker on, human watching daily — with the drill log green and the audit query returning zero orphans. Unattended operation before that standard is the risk realised, not accepted.

That is elapsed time under observation. No amount of implementation substitutes for it, and PHASE-027 was closing around it rather than through it.

**Re-homed rather than deferred**, per `STATUSES.md`: *"`deferred` does not resolve a child: park it under a real future phase so the relationship, not the status word, records where the work went."* Edwin's call, 2026-08-11. The risk is not smaller and nothing about it has been decided — it has an owner and a home.

## What PHASE-027 handed over

Working and tested, so the week starts with brakes rather than hope:

- **The policy defaults closed** — no approved `DELEGATION.md`, no worker ([[FEAT-0075]]).
- **Six halt paths, each drilled** — stop-switch, no-delegation, validator-red, parked-items, session-budget, wall-clock; a human stop outranks every computed one ([[REQ-0031]]).
- **Nothing waits silently** — every queue kind times out into a recorded assumption or alarms, and an unknown kind alarms ([[FEAT-0076]]).
- **Permission prompts are on that clock** — the most likely way a worker stops is no longer invisible to the alarm ([[ISS-0094]]).
- **Turn checkpoints with a principal-owned restore** — the undo unit is a turn, and a worker cannot rewind itself ([[FEAT-0078]]).
- **A picker that records what it passed over** — so "why is it working on that?" has an answer three hours later ([[TASK-0322]]).
- **A delegate is distinguishable from a person** at a glance, and a delegate write that cannot name its authority is refused ([[REQ-0029]]).

## Exit Criteria

- [ ] An approved `DELEGATION.md` exists, delegating a deliberately narrow first set — evidence: <the policy, and what it names>
- [ ] The worker runs for a week with a human reading the digest daily — evidence: <the week's ledger, and what the digest showed>
- [ ] The audit query "all autonomous judgments in range" returns zero orphans **against real data** — evidence: <the query, and its count>
- [ ] Every halt that fired in the week fired for a reason a person agreed with — evidence: <the halts, and the reading>
- [ ] [[RISK-0006]] closes on that evidence, or the week's findings reopen the design — evidence: <the risk's closing note>

## What would make this phase fail honestly

The week producing corrections is **not** failure — [[RISK-0006]]'s first hazard is compounding judgment, and catching it is the point of watching. Failure is the week not being watched: a ledger nobody read, closing the risk because seven days elapsed. The criterion is *supervised*, and supervision is reading.
