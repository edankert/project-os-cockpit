---
type: "[[task]]"
id: TASK-0349
aliases: ["TASK-0349"]
title: "The model-switch announcement expires instead of permanently suppressing warm, cooling and cold"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent"]
parent: "[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]"
effort: S
due: ""
depends: ["[[TASK-0348-Synthetic-Entries-Are-Not-Turns]]"]
blocks: []
related: ["[[ISS-0107-A-Model-Switch-Permanently-Suppresses-The-Cold-Warning]]"]
tests: []
---

# The switch announcement expires

Fixes [[ISS-0107-A-Model-Switch-Permanently-Suppresses-The-Cold-Warning]].

## Definition of Done
- [x] `model_switch` is attached to the live state only while the switch is still the freshest thing to say; past that window the standing warm / cooling / cold state is what renders.
- [x] The expiry is re-derived on the clock in `_with_age`, so it happens with no new turn and survives a memoised read — the same property [[TASK-0346-Cold-Reads-Grey-And-Actually-Ticks]] needed.
- [x] The badge's colour follows the **actual** temperature. A switch no longer forces `data-cache="cold"` onto a warm session; if a fresh switch deserves colour it gets its own, not cold's.
- [x] Tests cross the expiry boundary in both directions, and assert a cold-after-switch session eventually renders `cold`.

## Notes
The original comment — "the cost is already paid" — is right for the minutes after a switch and wrong forever after. A fact worth announcing once is not a fact worth announcing permanently, and here it was suppressing the warning the feature exists to give.
