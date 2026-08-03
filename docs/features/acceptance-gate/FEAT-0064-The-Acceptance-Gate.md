---
type: "[[feature]]"
id: FEAT-0064
aliases: ["FEAT-0064"]
title: "Acceptance as an explicit, opt-in gate: requested at close-out, owed on the desk, satisfied only by a run"
status: planned
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[DES-0006-The-Acceptance-Desk]]"]
goal: "An `acceptance:` field on features — absent / requested / accepted — with the desk queueing what is requested, a validator warning when it goes stale, and the upstream proposal that would make the convention fleet-wide."
requirements: []
tasks: []
release: ""
related: ["[[FEAT-0063-The-Acceptance-Runner]]"]
tests: []
---

# The acceptance gate

## Goal

The second question, distinct from independent review: *is this what I asked for?* Opt-in per feature because a mandatory gate on the one unautomatable judgment becomes a rubber stamp — [[PHASE-024]]'s framing. `requested` never blocks the agent's close-out; it keeps the debt visible until a run ([[FEAT-0063]]) stamps it.

## Integration points (investigated)

- The field joins the feature template and TAXONOMY; the sync script propagates nothing new (notes stay the source).
- Desk queue: `Awaiting your acceptance · N` above Changes requested — the queue's most human item first.
- Validator: a local warning (`ACCEPT-STALE`) when `done` + `requested` exceeds an age; upstream proposal task files the convention with project-os, the close-out-rule route.

## Out of Scope

- Blocking anything. The gate nags; ADR-0011's deadline mechanism is available later if nagging proves too weak.
