---
type: "[[task]]"
id: TASK-0468
aliases: ["TASK-0468"]
title: "The considered obligation — absent on an in-flight feature is owed, none-with-reason discharges forever, and no check ever reaches a badge"
status: backlog
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["[[FEAT-0115-The-Sweep-Is-Continuous]]"]
parent: "[[FEAT-0115-The-Sweep-Is-Continuous]]"
effort: S
depends: ["[[TASK-0467-The-Impact-Sweep-At-Close-Out]]"]
blocks: []
related: ["[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0028-Work-Has-Three-Phases]]"]
tests: []
---

# The considered obligation

`acceptance_impact:` has three states because two would lie: a **date** (swept), **`none — <reason>`** (considered, nothing to do — discharged permanently), **absent** (owed). A boolean collapses *nothing to do* into *not done* and nags forever — the [[ADR-0027-The-Registry-Counts-What-Needs-A-Person]] failure by construction.

Routing per [[ADR-0028-Work-Has-Three-Phases]]: a feature at `doing`/`review` with no `acceptance_impact` owes the sweep, on the features view, as one row; a feature at `backlog` owes nothing (nothing has changed); a terminal feature is settled — the field records whether the sweep happened at close-out. And the guarantee that outranks the feature: **no per-check obligation exists anywhere** — `"check"` is declared owed-nothing and a test pins it, because the granularity's most tempting use is the one that floods the badges.

## Done when

- [ ] The obligation appears exactly for in-flight features without the field, disappears on either authored state, and never returns after `none`.
- [ ] A test asserts no `CHK-*` ever contributes to any badge, any Needs-you group, any digest — and `your-trainer`'s badge total is unchanged.
