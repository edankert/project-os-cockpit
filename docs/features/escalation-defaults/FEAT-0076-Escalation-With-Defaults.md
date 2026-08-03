---
type: "[[feature]]"
id: FEAT-0076
aliases: ["FEAT-0076"]
title: "Escalation with defaults — timeouts per queue kind, proceed-on-recorded-assumption, and an alarm so nothing waits silently forever"
status: planned
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[DES-0009-The-Standing-Worker]]"]
goal: "The loop degrades instead of stalling: each queue kind carries a timeout and default from the policy; a lapsed question proceeds on an assumption written where the answer would have gone and lifted in the digest; kinds without defaults alarm rather than wait unboundedly."
requirements: []
tasks:
  - "[[TASK-0329-Timeouts-Per-Kind]]"
  - "[[TASK-0330-Proceed-On-Recorded-Assumption]]"
  - "[[TASK-0331-The-Stall-Alarm]]"
release: ""
related: ["[[FEAT-0062-Desk-Resolution-Flows]]", "[[FEAT-0071-Since-You-Looked]]"]
tests: []
---

# Escalation with defaults

## Goal

Without this, one unanswered question stalls the loop forever — the single sharpest failure mode of an unattended system that is *designed* to escalate. The invariant the feature exists to establish: **nothing in the system can wait silently without bound.** Everything either times out into a recorded assumption or alarms its way onto the landing.

## Out of Scope

- Guessing well. The assumption's quality is the delegate's problem; the feature's job is that it is *recorded, tagged and lifted*, so a wrong assumption is a visible one.
- Defaults for judgments the policy reserves — those wait and alarm, by design.
