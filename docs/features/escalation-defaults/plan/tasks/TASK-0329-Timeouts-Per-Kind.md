---
type: "[[task]]"
id: TASK-0329
aliases: ["TASK-0329"]
title: "Timeouts per queue kind, read from the approved policy"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0076-Escalation-With-Defaults]]"]
parent: "[[FEAT-0076-Escalation-With-Defaults]]"
effort: S
depends: []
blocks: ["[[TASK-0330-Proceed-On-Recorded-Assumption]]", "[[TASK-0331-The-Stall-Alarm]]"]
related: []
tests: []
---

# Timeouts per kind

## Definition of Done

- Queue entries age against their kind's policy timeout; entries whose kind has no policy line have no timeout and fall to the alarm path.
- Ages and thresholds visible on the desk rows — the human sees the clock the system is on.
- No policy note → no timeouts → nothing proceeds by default anywhere (the unconfigured repo stays fully manual).

## Done — 2026-08-11

`escalation.assess()` ages an entry against its kind's policy and returns the state **plus the reasoning**, so a surface can show the clock the system is on rather than only its verdict.

**A kind with no policy line does not get a silent pass — it alarms.** That is the judgment that makes the invariant real: a kind nobody wrote a timeout for is a kind nobody decided about, and the safe reading of an undecided kind is *ask a person*, never *proceed quietly*. Defaulting to silence there would have hollowed out the whole feature while every test still passed.

The policy lives in `DEFAULT_POLICY` rather than a config file, for the reason `MAX_CHECKPOINTS` does: the number **is** the decision, and a decision nobody can find is a decision nobody reviews.
