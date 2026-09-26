---
type: "[[task]]"
id: TASK-0355
aliases: ["TASK-0355"]
title: "The snapshot carries the corrected figures, and no box is ticked for work that was not done"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent"]
parent: "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"
effort: S
due: ""
depends: []
blocks: []
related: ["[[ISS-0113-SNAPSHOT-Still-Quotes-The-Retracted-Figures]]", "[[ISS-0115-ISS-0110s-Repro-Still-Reproduces]]", "[[ISS-0116-Ticked-Boxes-That-Do-Not-Match-The-Work]]"]
tests: []
---

# The record stops overclaiming

Fixes [[ISS-0113-SNAPSHOT-Still-Quotes-The-Retracted-Figures]], [[ISS-0116-Ticked-Boxes-That-Do-Not-Match-The-Work]], and the false-claim half of [[ISS-0115-ISS-0110s-Repro-Still-Reproduces]].

## Definition of Done
- [x] `SNAPSHOT.yaml`'s `focus.note` and `items.features.FEAT-0081.note` carry the corrected figures. This is the surface every session reads first, and it still quoted `11 of 17` — the number the review proved impossible.
- [x] `items.features.FEAT-0081.tasks` lists all thirteen tasks and every fixed issue: ISS-0112's drift with the sides swapped, which `PARENT-BACKLINK` structurally cannot see. *(Ticked once before it was true — two `.replace()` calls had silently no-opped on a stale pattern and nothing asserted the match. See [[ISS-0117]]; the corrective is in the Notes below.)*
- [x] The claim that deleting ISS-0105's behaviour "turns the suite red" is corrected to what the suite actually does. Re-verified: the three call sites deleted, the suite is fully green.
- [x] `6 of the 17` corrected in `session_cache.py` and `PLAN.md`; the duplicated follow-up lines in both earlier change notes resolved to one each.
- [x] Every remaining ticked box in this feature's tasks is checked against the diff, and any that does not hold is untick­ed or reworded rather than left standing.

## Notes

**Why this was ticked twice before it was done.** Both attempts used a string replace whose pattern no longer matched the file, and neither asserted the match, so both reported success and changed nothing. `SNAPSHOT.yaml` *was* in the diff each time, which is why the "confirm the file is in the diff" check could not see it either — the file was edited, just not in the place claimed.

The corrective that does work: **assert the pattern matched.** A silent no-op is indistinguishable from success, and every documentation overclaim in this feature's four rounds traces to a step that reported doing something it had not done.
Three of round 2's four findings are the same defect as round 1's core finding — a claim written wider than the code — committed while fixing it. The corrective is mechanical: before ticking a box that names a file, confirm the file is in the diff.
