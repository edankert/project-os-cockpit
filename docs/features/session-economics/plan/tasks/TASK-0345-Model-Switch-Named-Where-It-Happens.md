---
type: "[[task]]"
id: TASK-0345
aliases: ["TASK-0345"]
title: "A model switch that discards a warm prefix is named, with the tokens it cost"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["user:edwin"]
parent: "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"
effort: S
due: ""
depends: ["[[TASK-0343-The-Cache-Reader]]"]
blocks: []
related: ["[[ISS-0104-Model-Switch-Discards-The-Warm-Cache]]"]
tests: []
---

# A model switch that discards a warm prefix is named, with the tokens it cost

## Definition of Done
- [x] The full scan splits sub-hour invalidations into `model-switch` and `other`, comparing each full-prefix re-write's model against the preceding turn's.
- [x] The retrospective payload reports the model-switch bucket with its token count and estimated cost.
- [x] A live session whose most recent turn switched model while discarding ≥50k cached tokens reports that fact, with the discarded token count and the two model names.
- [x] Tests cover a switch above and below the threshold, and a sub-hour re-write with no switch (must classify as `other`, not `model-switch`).
- [x] Nothing blocks, intercepts, or warns *before* a switch — the cockpit does not own the session ([[ISS-0104]], scope note).
- [x] [[ISS-0104]] moves to `fixed`.

## Steps
- [x] Carry `prev_model` through the classification in `session_cache.py`.
- [x] Add the bucket to the history payload and the live-state shape.
- [x] Surface the live case in the strip's cache badge.
- [x] Tests.

## Notes
Threshold is 50k discarded tokens: below that the finding is noise, and the measured events are two orders of magnitude above it (252k–986k). The number is a constant with a name, not a literal.

"Other" is not a failure of classification — cache entries can be evicted before their TTL, so some sub-hour re-writes have no discoverable cause. 6 of the measured 17 fall here. Reporting them as `other` rather than forcing them into a bucket is the honest shape.
