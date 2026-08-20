---
type: "[[task]]"
id: TASK-0503
aliases: ["TASK-0503"]
title: "Replace the sixty-row blocking wall with a breakdown by area, each part linking to a filtered `~checks`"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
parent: "[[FEAT-0125-The-Release-Page-Reports-What-Holds-It]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Replace the sixty-row blocking wall with a breakdown by area, each part linking to a filtered `~checks`

The verdict line and confidence roll-up stay. `gate.blocking` carries `area` on every row, so the breakdown is a tally over data already in the payload.

Lossless: the full list stays reachable through the links, and the count in the heading must equal the number of rows behind them.

## Done 2026-08-20

`gateAreaBreakdown` renders in front of the blocking list — never instead of it — on the groups that ask, and each part opens `~checks/area/<area>`.

**Measured before drawing it**, on `your-trainer` at HEAD: **59 blocking rows across 17 areas**, and the shape is the reason the tally is worth the space — `Trainer Compatibility Verification` holds 20 and `Monetization & Licensing` 11, so two areas are more than half the gate. A 59-row scroll hides that; the tally is the first thing on the page that a person can act on.

**The filter is in the ADDRESS**, `~checks/area/<area>`, on [[ISS-0203]]'s rule: a filter that lives in a click cannot be linked to, cannot be reopened with back/forward, and does not survive a navigation. It is also assigned unconditionally, so a bare `~checks` clears it — the sticky-filter defect ISS-0203 removed from the tier axis.

**Lossless, and the guard is on the property that can break quietly.** `test_the_gate_breakdown_is_lossless_and_sums_to_its_list` fails if the tally slices, filters or breaks out of its loop, and asserts the breakdown renders before the rows rather than after them. A breakdown that drops a row is indistinguishable from a shorter gate, which is the one direction a release page must never be wrong in. Proved on a mutant: capping the loop at ten rows fails it.

Below eight rows there is no breakdown — a tally of four over a list of four says nothing the list does not, and `GATE_BREAKDOWN_MIN` states that as one decision rather than a literal in a condition.
