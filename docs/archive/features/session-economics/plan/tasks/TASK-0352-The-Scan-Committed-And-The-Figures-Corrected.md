---
type: "[[task]]"
id: TASK-0352
aliases: ["TASK-0352"]
title: "The measurement becomes a command anyone can run, and every quoted figure is re-derived from it"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent"]
parent: "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"
effort: M
due: ""
depends: ["[[TASK-0348-Synthetic-Entries-Are-Not-Turns]]"]
blocks: []
related: ["[[ISS-0111-The-Measured-Figures-Do-Not-Reproduce-And-No-Scan-Script-Was-Committed]]"]
tests: []
---

# The scan committed, the figures corrected

Fixes [[ISS-0111-The-Measured-Figures-Do-Not-Reproduce-And-No-Scan-Script-Was-Committed]].

## Definition of Done
- [x] The fleet scan is committed as a script that runs against `~/.claude/projects/` and prints the figures the notes quote, using the **shipped module** so the two cannot diverge again.
- [x] Every quoted figure in FEAT-0081, [[ISS-0104-Model-Switch-Discards-The-Warm-Cache]], both change notes and `SNAPSHOT.yaml` is re-derived after [[TASK-0348-Synthetic-Entries-Are-Not-Turns]] and corrected, with the correction visible rather than silent.
- [x] One definition of "staleness" is chosen and used everywhere; the `~3.5%` / `5.0%` inconsistency is resolved in favour of whichever the sentence actually means.
- [x] The notes state that `/api/cockpit/session-cache` is **per-workspace** and is not the cross-fleet measurement, so no reader mistakes one for the other.

## Notes
Two of the seven quoted figures fell on re-derivation. Counts of past events cannot fall, so the originals came from logic that never shipped — which is the whole argument for committing the scan rather than the prose.
