---
type: "[[risk]]"
id: RISK-0006
aliases: ["RISK-0006"]
title: "The unattended worker — compounding wrong judgment at machine speed, spend without ceiling, and an audit trail that lags the actions it explains"
status: open
severity: high
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
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
