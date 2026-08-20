---
type: "[[issue]]"
id: ISS-0237
aliases: ["ISS-0237"]
title: "`Item` does not read `command:` at all, so a check the runner owns is counted as an owed manual walk — nine of your-trainer's sixty-eight blocking checks are automated"
status: fixed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
severity: high
component: cockpit-server
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
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

## Fixed 2026-08-20 — [[PHASE-039]]

**The deeper half first, because it was the cause.** `item_from_note` now reads `command:`, so the acceptance reader can tell an automated check from a manual one at all. Measured through the reader itself afterwards: 89 checks in `your-trainer` carry a command, and **nine of the 68 blocking its release were executed by a machine** — the same figure this issue reported, arrived at independently.

**The gate delta, measured per repo before it landed** ([[TASK-0571]]): `your-trainer` **68 → 59**; `project-os-cockpit` 0 → 0; `your-sudoku` 56 → 56; `your-health` and `project-os-dev` hold no suite. That is the nine leaving, and nothing else moving.

An automated check is no longer part of the manual list at all — not discounted within it. [[ADR-0039]] makes `Automated tests` a derived section, and the generated page renders it with no checkbox and no completed fraction.

## Corrected 2026-08-20 after independent review

**The gate delta was measured against `your-trainer`'s WORKING TREE, and the committed record moves the other way.**

| measured against | before | after |
| --- | --- | --- |
| working tree (588 uncommitted files) | 68 | **59** — the nine automated checks leave |
| `HEAD`, i.e. what a fresh clone has | 62 | **68** — six Tier 3 checks *enter* |

**At `HEAD`, zero acceptance checks in `your-trainer` carry a `command:`.** All 89 live only in uncommitted work, so nothing leaves the gate there today. What does happen is the other half of the same rule: `TST-0592`..`TST-0597` are Tier 3, carry no command, and are therefore manual and owed — exactly what [[ADR-0039]] decides, and exactly what `blocking()`'s own comment described on 2026-08-18 as *"a NEW and tighter gate, which is a decision for a person"*. It is that person's decision now; the comment has been corrected to say so.

Both numbers are true of what they measure. Only one of them is true of what ships.
