---
type: "[[task]]"
id: TASK-0270
aliases: ["TASK-0270"]
title: "A group longer than the fold threshold shows its head and a count, keyed on length and never on status, so the switch collapses rather than hides"
status: done
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["[[FEAT-0056-Completed-Work-Ordering]]"]
parent: "[[FEAT-0056-Completed-Work-Ordering]]"
effort: M
depends: ["[[TASK-0267-One-Comparator-Open-Before-Done]]", "[[TASK-0268-Groups-With-Open-Work-Sort-First]]"]
blocks: []
related: []
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# Folding keyed on length

## Definition of Done

- A group longer than the threshold renders its first N items and a row that names what it withheld and reveals it on click.
- The condition is **length**, never status: an over-long group of entirely open items folds too. Folding on status is what produced the empty views this phase exists to undo.
- `Hide completed` becomes the collapse control: on, groups fold at their first **completed** item; off, only the length limit applies. It can no longer produce an empty view.
- Counts are always visible — a fold that hides the fact that it hid something is indistinguishable from having nothing there.

## Notes

Last on purpose. Ordering ([[TASK-0267]], [[TASK-0268]]) is cheap and reversible and may be sufficient for the features and issues views; the measured volume problem is the tasks view's **270 rows, 261 of them in a single `done` bucket**, and that is where the threshold should be chosen from real numbers rather than guessed.

## Verification

The 261-row `done` bucket renders folded with an accurate count; a 50-row group of entirely open items folds identically, proving the key is length. `head + hidden == items.length` holds for every limit including 0 and negative — the invariant the count rests on.
