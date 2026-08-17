---
type: "[[task]]"
id: TASK-0463
aliases: ["TASK-0463"]
title: "The fleet migrates, trainer last — your-sudoku, then your-trainer only after the schema has survived a real sweep"
status: backlog
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["[[FEAT-0113-The-Check-Type-And-The-Migration]]"]
parent: "[[FEAT-0113-The-Check-Type-And-The-Migration]]"
effort: M
depends: ["[[TASK-0461-Pilot-This-Repo]]", "[[TASK-0462-The-Delta-Reads-Two-Shapes]]", "[[TASK-0467-The-Impact-Sweep-At-Close-Out]]"]
blocks: []
related: ["[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]"]
tests: []
---

# The fleet migrates, trainer last

`your-sudoku` (56 rows), then `your-trainer` (579 rows, 60 blocking, the only corpus that ships) — deliberately last, and gated on the schema having survived a real close-out sweep in the pilot repo, because a schema defect discovered against 579 live rows is a migration re-run in the one repo where the record is load-bearing.

## Done when

- [ ] Both repos migrate with the parity assertions green; `your-trainer`'s blocking number is unchanged across the cut.
- [ ] `your-trainer`'s obligation badge total is measured before and after and has not risen — the [[ADR-0027-The-Registry-Counts-What-Needs-A-Person]] guarantee, checked at the moment it is most at risk.
