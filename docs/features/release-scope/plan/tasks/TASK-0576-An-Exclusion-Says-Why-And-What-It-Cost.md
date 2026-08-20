---
type: "[[task]]"
id: TASK-0576
aliases: ["TASK-0576"]
title: "An exclusion says why, and the page says what the selection cost"
status: backlog
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
source: ["[[FEAT-0142-A-Release-Says-What-Is-In-It]]", "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]"]
parent: "[[FEAT-0142-A-Release-Says-What-Is-In-It]]"
effort: S
due: ""
depends: []
blocks: []
related: ["[[ADR-0028-Publication-Is-The-Third-Phase]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]"]
tests: []
---

# An exclusion says why, and the page says what it cost

**The last outstanding criterion of [[FEAT-0142]]** — six of its seven are met, five delivered under [[FEAT-0129]]'s tasks and one ([[FEAT-0142]] c5, `chronic`) found already true and now guarded.

## Definition of Done

- [ ] Holding a feature back records a **reason**, stored on the release note beside the selection
- [ ] The release page reads `N features held back · M checks no longer gating`
- [ ] A total that fell **says why it fell** — the number and its cause appear together, never a smaller number alone
- [ ] No write path to a check appears on the release page ([[ADR-0035]] unweakened)

## Measured before starting, 2026-08-20

`publication.py` already computes the held-back set — from the note's frontmatter, correctly, after a first cut read `held.get("features")` and could never fire. What does **not** exist:

| | state |
|---|---|
| `held_back` count in the payload | absent |
| any `held back` / `no longer gating` string in `renderer.ts` | **absent** — grep returns nothing |
| a `reason` on an exclusion | absent |

So this is additive: the mechanism is built and the **reporting** is not.

## Why the reason matters more than the count

A count that shrinks with no cause beside it is the defect this whole phase exists to remove — [[ISS-0243]] (90% complete over checks with no recorded result), [[ISS-0241]] (89 executed by CI with no observed run). A gate that drops from 59 to 23 because somebody deselected six features, rendered as *"23 blocking"* with nothing beside it, is the same lie in a new place.

[[ADR-0040]] chose subtraction over division partly to avoid emptying `chronic`. This task is the other half of that argument: **subtraction must be visible, not just conservative.**

## Not in scope

- Changing what subtracts. [[ADR-0040]] decided it and `blocking_minus` implements it.
- Anything that writes to a check from the release page.
