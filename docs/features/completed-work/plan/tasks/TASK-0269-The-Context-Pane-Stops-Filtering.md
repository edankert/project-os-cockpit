---
type: "[[task]]"
id: TASK-0269
aliases: ["TASK-0269"]
title: "The right context pane orders by state and never filters by it, because a note's completed children are what the note is made of"
status: done
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["Edwin 2026-08-02: 'That is perfect to support the left selection pane but we still need a solution for the right context pane, how should that be handled?'"]
parent: "[[FEAT-0056-Completed-Work-Ordering]]"
effort: S
depends: ["[[TASK-0267-One-Comparator-Open-Before-Done]]"]
blocks: []
related: []
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# The context pane stops filtering

## Definition of Done

- `renderContextGroup` no longer drops items on `isItemHidden`, and no longer returns `null` for a group whose items are all complete.
- Items within each group sort open-first ([[TASK-0267]]).
- The `Hide completed` switch does not reach this pane at all.

## Why

Measured with the switch on:

| note | right pane |
|---|---|
| FEAT-0051 | **entirely empty** — all 4 groups gone |
| ISS-0080 | **entirely empty** — all 4 groups gone |
| PHASE-016 | 1 of 7 groups survives |
| FEAT-0028 | 3 of 11 survive |

With almost every lifecycle note terminal, the emptied pane is the *normal* case. The left pane is a selection list, where a done item is one you will not click; the right pane is a **description**, where a done item is part of what the note *is*. Removing FEAT-0051's five completed tasks does not declutter its description — it deletes it.

**Corrected at review.** This originally claimed the pressure that justifies folding elsewhere is absent here — "the largest group measured across the corpus is 11 items, there is no wall to scroll past". That 11 was measured on **one note**. Swept across every note, 11 of 3192 context groups exceed 12 and PHASE-007 renders a 79-item backlinks group. The wall is real, so the **length** fold applies here exactly as it does on the left. What does not apply is the state filter — which is the point of its being a length rule.

The types are the proof: `change` is 100% complete, `test` 96%, `adr` and `reference` effectively always. A state filter on this pane does not thin those groups, it forbids them.

## Verification

FEAT-0051 and ISS-0080 — both empty today — render their full context with the switch on.
