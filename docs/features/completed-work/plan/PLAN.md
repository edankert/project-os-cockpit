---
type: "[[plan]]"
title: "Plan — completed work gets quieter"
status: done
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
parent: "[[FEAT-0056-Completed-Work-Ordering]]"
---

# Plan

Ordering before folding, deliberately: ordering is cheap, reversible and may well be enough. Folding is the heavier change and should be built against evidence that ordering did not suffice — which is why [[TASK-0270]] is last rather than first.

1. **[[TASK-0267]]** — one comparator, `openFirst`, applied to items within every group. Foundational; the other three consume it.
2. **[[TASK-0268]]** — groups sort by whether they still contain open work, then by their natural axis. Depends on 0267 only for the shared "is this open" predicate.
3. **[[TASK-0269]]** — the context pane stops filtering by state and starts ordering by it. Independent of 0268; the smallest change and the largest fix, because it is the one place that currently empties.
4. **[[TASK-0270]]** — the fold, keyed on length. Last, and only where measurement shows length is the problem.

The switch survives all four, meaning something different at the end: collapse, not hide.
