---
type: "[[task]]"
id: TASK-0347
aliases: ["TASK-0347"]
title: "A cold session leaves the NEEDS YOU list, so the list means blocked on you and still cheap to pick up"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["user:edwin"]
parent: "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"
effort: S
due: ""
depends: ["[[TASK-0346-Cold-Reads-Grey-And-Actually-Ticks]]"]
blocks: []
related: ["[[ISS-0105-The-Rail-Pulses-The-Same-For-Two-Minutes-And-Two-Hundred-Hours]]"]
tests: []
---

# A cold session leaves the NEEDS YOU list

## Definition of Done
- [x] `attentionEntries()` drops any workspace whose session has gone cold, using the same pure function the rail uses — one rule, one implementation, both surfaces.
- [x] The list re-evaluates on the same tick as the rail, so an entry leaves without an inbound event.
- [x] The panel's empty state is reached when every waiting session has gone cold, and reads as a real answer rather than a rendering accident.
- [x] No resume cost is added to the rows — the rows in question are gone, which is the point.
- [x] The T+59min-present / T+61min-absent boundary is proven. *(Scope, corrected twice. Originally ticked for `cacheTemperature` alone; [[TASK-0351-Pure-Decisions-For-The-Rail-And-The-Badge]] added `attentionIds`, which is the list's own membership rule and is now guarded across the boundary. What remains unproven by any suite is the DOM adapter that calls it — [[ISS-0115]].)*

## Steps
- [x] Filter in `attentionEntries()`.
- [x] Repaint the panel on the temperature tick.
- [x] Check the empty state renders.

## Notes
Supersedes the earlier plan to annotate these rows with their resume cost (Edwin, 2026-08-06): if the entry leaves, there is nothing to annotate, and one rule across both surfaces beats two.

Measured against the fleet on 2026-08-06 this takes NEEDS YOU from five entries to one — the 50h, 185h, 209h and 211h entries go, the 1-minute one stays.

**Known consequence, recorded in [[ISS-0105]]:** a session that is genuinely blocked becomes invisible here an hour after it blocks, leaving the grey rail square as its only trace. Deliberate — a list that never forgets is what is being fixed — but it is a lost nag, not a free win.
