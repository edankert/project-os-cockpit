---
type: "[[risk]]"
id: RISK-0006
aliases: ["RISK-0006"]
title: "The unattended worker — compounding wrong judgment at machine speed, spend without ceiling, and an audit trail that lags the actions it explains"
status: open
severity: high
phase: "[[PHASE-031-The-Supervised-Week]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["Preflight risk scan for PHASE-027"]
component: driver
mitigation: "[[REQ-0030-The-Worker-Never-Outruns-Its-Policy]]"
related: ["[[REQ-0031-The-Loop-Always-Halts]]", "[[RISK-0005-The-Write-Surface]]", "[[ADR-0009-The-Principal-Is-A-Role]]"]
tests: []
---

# The unattended worker

## The hazard

Three shapes, all downstream of removing the human's cadence from the loop:

1. **Compounding judgment** — a wrong assumption at hour one is the context of every decision after it; twelve human-caught corrections in PHASE-022 argue the delegate will be wrong sometimes, and unattended wrongness compounds until the digest is read.
2. **Spend** — sessions cost; a loop that finds ever more work (its own filed issues are backlog) can fund itself indefinitely.
3. **Audit lag** — the record is only protective if writes land before the next action reads them; a worker racing its own ledger produces history that explains nothing.

## Why open

The mitigations are designed ([[REQ-0030]], [[REQ-0031]], the digest's assumed-answers lift) and none implemented. This risk closes when a repo has run a **supervised** week — worker on, human watching daily — with the drill log green and the audit query returning zero orphans. Unattended operation before that standard is the risk realised, not accepted.

## Trigger review

Any budget raise, any new delegated judgment kind, the first correction of a delegate's assumption, and the push ADR ([[TASK-0328]]) whatever it decides.

## Re-homed to [[PHASE-031]] — 2026-08-11

**Still `open`, and nothing about it has been decided.** Edwin's call while closing out [[REL-0001]]: the risk moves to a phase that owns the supervised week, rather than holding [[PHASE-027]] open around it or being marked `deferred`.

`STATUSES.md` provides exactly this: *"`deferred` does not resolve a child: park it under a real future phase so the relationship, not the status word, records where the work went."* The distinction matters here more than usual — `deferred` would say the week was descoped, and it has not been. It has an owner and a date-less home.

**What changed is where it lives, not what it requires.** The closing condition is unchanged: a supervised week, worker on, human watching daily, drill log green, audit query returning zero orphans against real data. [[PHASE-031]]'s exit criteria restate it as the phase's own work.

**What PHASE-027 delivered toward it** is listed on that phase: the policy defaulting closed, six drilled halt paths, an escalation clock nothing waits silently under, permission prompts brought onto it, turn checkpoints with principal-owned restore, a picker that records its passovers, and a delegate that cannot write without naming its authority. The week starts with brakes rather than hope.
