---
type: "[[plan]]"
title: "Plan — history navigation"
status: active
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
implements: ["[[FEAT-0053-History-Navigation]]"]
related: ["[[PHASE-018-History-You-Can-Reach-And-Traverse]]"]
---

# Plan

1. **[[TASK-0258]]** — the payload. Everything waits on it.
2. **[[TASK-0259]]** — the grid. Depends on 0258.
3. **[[TASK-0260]]** — the rail button. Independent; could land first.

## Why this is a second payload rather than a field on the first

[[FEAT-0052]]'s history payload is **deliberately uncached**: its uncommitted band is the one part whose whole value is being current, and a cache keyed on HEAD would serve a stale "not saved yet" list.

The grid is the opposite. It needs a full-history pass — 0.57 s and 3.3 MB of diff on this repo — and its answer changes **only** when HEAD changes. Caching it on HEAD is free and correct.

Two opposite caching requirements is the reason these are two endpoints and not one payload with an extra key. Merging them would force one of the two to be wrong.

## The three corrections, and why each is not cosmetic

**Relative intensity.** GitHub's buckets stop at 10+. This repo's median active day is 34 transitions, so fixed buckets would saturate every lit cell and the grid would carry one bit of information per day: worked / did not.

**Absent ≠ empty.** A cell before the first commit is not a day with no activity; it is a day the project did not exist. Rendering them identically is why every young repo's graph reads as neglect, and this repo would show 40 of 52 weeks as apparent inactivity.

**No controls without a second year.** A year selector on a twelve-week repo offers navigation to nothing. It arrives when it means something — the same rule the fleet roll-up's empty state follows.

## One thing to watch

**A day cell must be a destination or it is a decoration.** The sparkline it replaces was pure ornament; if the grid ships without the click landing correctly, it is the same ornament at higher resolution and the entry-point complaint is unanswered.
