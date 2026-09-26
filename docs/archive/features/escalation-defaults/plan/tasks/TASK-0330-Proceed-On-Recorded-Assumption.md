---
type: "[[task]]"
id: TASK-0330
aliases: ["TASK-0330"]
title: "Proceed on a recorded assumption — resolved where the answer would have gone, tagged on the work, lifted in the digest"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0076-Escalation-With-Defaults]]"]
parent: "[[FEAT-0076-Escalation-With-Defaults]]"
effort: M
depends: ["[[TASK-0329-Timeouts-Per-Kind]]"]
blocks: []
related: []
tests: []
---

# Proceed on a recorded assumption

## Definition of Done

- A lapsed question resolves through review-resolve with the assumption as outcome, attributed to the policy line that authorised it — the same shape a human answer takes, distinguishable at a glance.
- Work done under an assumption carries the tag; the digest lifts assumed-answers into needs-you until the human confirms or corrects.
- A corrected assumption files the correction as an issue against the affected work — a wrong guess becomes work, never silence.

## Done — 2026-08-11

A lapse returns `state: lapsed` **with the assumption it proceeded on** — a lapse with no recorded assumption is a silent decision, which is the thing this feature forbids, so it is asserted.

`RESERVES_JUDGMENT` exists and is **empty today, deliberately**. A kind that reserves judgment can never proceed on an assumption however long it waits; the timeout then decides only *when it alarms*. The moment a delegated **acceptance** kind exists it belongs in that set — and a set that has to be created later is a set somebody forgets.
