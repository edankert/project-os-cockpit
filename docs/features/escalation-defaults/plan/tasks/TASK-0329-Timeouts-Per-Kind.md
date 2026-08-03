---
type: "[[task]]"
id: TASK-0329
aliases: ["TASK-0329"]
title: "Timeouts per queue kind, read from the approved policy"
status: backlog
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
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
