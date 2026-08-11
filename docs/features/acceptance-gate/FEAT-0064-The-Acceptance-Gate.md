---
type: "[[feature]]"
id: FEAT-0064
aliases: ["FEAT-0064"]
title: "Acceptance as an explicit, opt-in gate: requested at close-out, owed on the desk, satisfied only by a run"
status: done
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[DES-0006-The-Acceptance-Desk]]"]
goal: "An `acceptance:` field on features — absent / requested / accepted — with the desk queueing what is requested, a validator warning when it goes stale, and the upstream proposal that would make the convention fleet-wide."
requirements: []
tasks:
  - "[[TASK-0291-The-Field]]"
  - "[[TASK-0292-The-Desk-Queue-Section]]"
  - "[[TASK-0293-Accept-Stale-And-The-Upstream-Proposal]]"
release: "[[REL-0001-The-Human-Has-Levers]]"
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

## Acceptance

- [x] `acceptance:` exists as a documented field with three states — absent / `requested` / `accepted` — in the feature template and `TAXONOMY.md` ([[TASK-0291]])
- [x] It is **opt-in and never blocks close-out** — absent is the default and stays the default; a mandatory gate on the one unautomatable judgment becomes a rubber stamp
- [x] The agent asks and never answers: an agent may stamp `requested`; only a completed run writes `accepted`, refusing features that never requested it ([[REQ-0028]])
- [x] A stale request is **warned about, not blocked** — `ACCEPT-STALE`, proven to fire at 587 days and stay silent when fresh ([[TASK-0293]])
- [x] A requested feature is marked owed and offers its run, re-homed to the note's actuator row ([[TASK-0292]])
- [~] The queue section renders "above Changes requested, with age" — **reconciled**: [[ADR-0020]] retired that desk. The marker and the offer moved to the feature; the age question is answered corpus-wide by `ACCEPT-STALE` rather than per row

## Verification

The warning is proven both ways — fires on a crafted stale request, silent on a fresh one — which matters more than usual here, because a nag that fires wrongly is the fastest way to teach someone to ignore it.
