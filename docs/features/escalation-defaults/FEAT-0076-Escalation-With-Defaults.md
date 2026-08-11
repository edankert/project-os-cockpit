---
type: "[[feature]]"
id: FEAT-0076
aliases: ["FEAT-0076"]
title: "Escalation with defaults — timeouts per queue kind, proceed-on-recorded-assumption, and an alarm so nothing waits silently forever"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[DES-0009-The-Standing-Worker]]"]
goal: "The loop degrades instead of stalling: each queue kind carries a timeout and default from the policy; a lapsed question proceeds on an assumption written where the answer would have gone and lifted in the digest; kinds without defaults alarm rather than wait unboundedly."
requirements: []
tasks:
  - "[[TASK-0329-Timeouts-Per-Kind]]"
  - "[[TASK-0330-Proceed-On-Recorded-Assumption]]"
  - "[[TASK-0331-The-Stall-Alarm]]"
release: "[[REL-0001-The-Human-Has-Levers]]"
related: ["[[FEAT-0062-Desk-Resolution-Flows]]", "[[FEAT-0071-Since-You-Looked]]"]
tests: []
---

# Escalation with defaults

## Goal

Without this, one unanswered question stalls the loop forever — the single sharpest failure mode of an unattended system that is *designed* to escalate. The invariant the feature exists to establish: **nothing in the system can wait silently without bound.** Everything either times out into a recorded assumption or alarms its way onto the landing.

## Out of Scope

- Guessing well. The assumption's quality is the delegate's problem; the feature's job is that it is *recorded, tagged and lifted*, so a wrong assumption is a visible one.
- Defaults for judgments the policy reserves — those wait and alarm, by design.

## Acceptance

- [x] **Nothing in the system can wait silently without bound** — proven by drill over every silent-wait shape ([[TASK-0331]])
- [x] Entries age against their kind's policy, and the state carries its reasoning so the human sees the clock ([[TASK-0329]])
- [x] A kind with **no policy line alarms** rather than passing quietly — an undecided kind asks a person
- [x] A lapse records the assumption it proceeded on; a lapse without one is a silent decision ([[TASK-0330]])
- [x] `RESERVES_JUDGMENT` exists before it is needed, so a kind that must never lapse has somewhere to go
- [x] The sweep accounts for **every** entry — one it dropped would be one waiting silently
- [~] Expired leases surface on the landing — **reconciled**: leases arrive with [[FEAT-0074]], which is gated on [[REQ-0030]]/[[REQ-0031]] while they are `draft`. The alarm path they will use is built and tested

## Verification

`tests/test_escalation.py` — 13 tests. The central one is an enumeration rather than a case: every shape an entry can take, asserted to reach a visible state.

Built ahead of the rest of [[PHASE-027]] because it is a **safety mechanism for** the unattended loop rather than part of it — like [[FEAT-0078]]'s checkpoints, and for the same reason.
