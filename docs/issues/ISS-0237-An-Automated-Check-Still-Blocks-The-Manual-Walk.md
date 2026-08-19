---
type: "[[issue]]"
id: ISS-0237
aliases: ["ISS-0237"]
title: "`Item` does not read `command:` at all, so a check the runner owns is counted as an owed manual walk — nine of your-trainer's sixty-eight blocking checks are automated"
status: open
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: high
component: cockpit-server
phase: "[[PHASE-999-Future]]"
related: ["[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ISS-0238-There-Is-Nowhere-To-Put-An-Automated-Check]]", "[[TASK-0556-Incomplete-First]]"]
---

# The reader is blind to `command:`

`your-trainer` gave 89 acceptance checks a `command:` on 2026-08-19 — the first repo with a real population of automated ones.

## Measured, 2026-08-19

| | |
| --- | --- |
| checks at `level: acceptance` carrying a `command:` | **89** |
| of the **68** blocking that repo's release, how many are automated | **9** |
| `Item` exposes `command` | **no — the field is not in the dataclass** |

The defect is deeper than the count. `acceptance.item_from_note` never reads `command:`, so **the acceptance reader cannot tell an automated check from a manual one at all.** `Item.settled` consults `checked`, `reconciled`, `excepted` and `covered_by_passing` — the last is about `covered_by:` links, not about a command.

## Why that is wrong by the contract

`STATUSES.md` § `[[test]]`, `level: acceptance`:

> **Adding a `command:` is how it becomes automated**, and from that moment the runner owns its status like any other executable test. […] automating a walk **discharges** it instead of leaving it owed.

[[ADR-0031]] decision 3 says the same and calls it the point of the merge: *"Set it and the runner owns the status… so automating a check discharges it instead of buying nothing."* Nine checks are currently buying nothing.

## What it costs beyond the gate

The surface percentage counts them, so a surface's denominator includes work nobody will ever do by hand — and [[TASK-0556]] sorts by percentage incomplete, so those surfaces rise to the top of *what is owed*. **Same class as counting a stale tick**, which this project has already paid for twice.

## Suggested fix

1. `Item` reads `command:`. One field, and everything else follows from it.
2. **`Item.settled` gains the clause [[ADR-0031]] decision 3 already specified** — a check with a `command:` is not owed. Presence of the field is the whole test; the note holds no pass/fail and should not, because the run gates the push and CI and is a louder, more current signal than anything frontmatter could carry.
3. Automated checks leave the numerator **and the denominator** of a manual-walk percentage. A percentage over work nobody will do by hand is not a measure of anything.
4. **The gate delta is measured per repo before it lands** — `your-trainer` goes 68 → 59 blocking. Same rule every gate change in [[PHASE-038]] followed.

## Done when

- [ ] A check with a `command:` is not owed and not counted in a manual-walk percentage.
- [ ] The delta is stated per repo before the change lands.
