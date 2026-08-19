---
type: "[[feature]]"
id: FEAT-0135
aliases: ["FEAT-0135"]
title: "Everything downstream is a query — the walk list, the release gate and the cross-platform burndown are computed from ledgers, never maintained"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
goal: "A maintained matrix rots and a computed query cannot — so every question about verification state is answered by reading ledgers, including the one nobody can currently ask: where does one platform stand against another."
requirements: ["[[REQ-0054-Absence-Is-The-Initial-State]]"]
tasks: ["[[TASK-0533-The-Run-List-Is-A-Query]]", "[[TASK-0534-The-Release-Gate-Reads-The-Shipping-Platforms-Ledger]]", "[[TASK-0535-The-Cross-Platform-Burndown]]"]
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ISS-0208-Retire-The-Tier-Rule]]", "[[DES-0012-Tests-In-Two-Flows]]"]
tags: [feature]
---

# The queries

## Goal

| question | query |
| --- | --- |
| Is this automated on platform P? | `method` of its latest entry for P |
| What must a person run for release R? | No terminal entry since the last invalidation, and not covered by this cycle's CI |
| Where does platform B stand against A? | A-`pass` with no terminal B entry; `na` drops out by construction |
| Release gate | Every gated check has a terminal entry (`pass` or `na`) for the shipping platform |
| Was release R walked? | Read its ledger; it is immutable |

## The rule that makes all of them work

**A check with no entry for a platform is owed on that platform.** No `applies:` field, no per-platform key, no backfill when a platform is added. The absence *is* the initial state and it is the honest one. The escape hatch is a `mark: na` event with a required reason, which a later event can invalidate through the same machinery that re-arms a stale pass.

## The gate moves, and that is the deliverable

`Suite.blocking_for(subjects)` already scopes to any subject set ([[FEAT-0124]]). What changes is where its settled-ness comes from. Two movements, in opposite directions, and both must be stated per repo **before** that repo migrates:

- **124 `todo` notes become "no entry"** — same blocking state, no movement.
- **546 `pass` entries become platform-specific.** On `your-trainer` this is a sharp tightening: 513 Android passes stop counting toward an iOS release. On single-platform repos it is a no-op.

*"Quieter is the one direction a gate must never move without somebody deciding it"* ([[ISS-0208]]). This moves it louder, deliberately, and the number is measured rather than discovered.

## Out of scope

- The tier filter and the fail-closed clause. [[ISS-0208]]. Where a verdict is stored says nothing about which checks gate, and folding the two would make one issue impossible to reason about.
- Rendering. [[FEAT-0136]].

## Acceptance

- [ ] Each of the five queries has one implementation and one test.
- [ ] A check with no entry for a platform reports as owed there, with no field declaring applicability.
- [ ] Adding a platform to a repo requires no note edit and no schema change.
- [ ] The gate delta is measured and recorded per repo before that repo migrates.
- [ ] `was release R walked` returns the same answer twice across an intervening working-ledger append.
