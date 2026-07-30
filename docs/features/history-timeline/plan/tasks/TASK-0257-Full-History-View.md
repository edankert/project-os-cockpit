---
type: "[[task]]"
id: TASK-0257
aliases: ["TASK-0257"]
title: "The full history view at ~history"
status: done
phase: "[[PHASE-017-History-As-Document-Events]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0052-History-Timeline]]"]
parent: "[[FEAT-0052-History-Timeline]]"
effort: S
depends: ["[[TASK-0255-History-Payload]]"]
blocks: []
related: ["[[FEAT-0043-Design-Bench]]"]
tests: []
---

# The full history view

## Definition of Done
- [x] `~history` renders the same timeline, further back
- [x] Reachable from the overview tile
- [~] Grouped by day, so a month of history is scannable rather than a wall — **not done**, see below
- [x] Says how far back it goes, rather than implying it is complete
- [x] Uses the same row and divider components as the tile — one grammar, not two

## Steps
- [x] Register `~history` alongside the other virtual pages (`~design`, `~review`, `~agents`)
- [x] Render from the same payload at a larger limit
- [x] Test: the route resolves and the page is not empty on this repo's own corpus

## Notes

Virtual-page routing is established — `~design`, `~review` and `~agents` all work this way, and [[ISS-0037]] settled how `~`-prefixed paths behave in both clients. This adds one more rather than inventing a mechanism.

**Say the horizon.** A view that shows 200 commits and stops without saying so reads as "this is everything". The footer should state the window, the same way the fleet roll-up states how many repos it checked.

## Done 2026-07-30

`~history`, registered beside `~review` / `~design` / `~agents`, rendering from the same payload at 60 commits with the same rows and dividers — one grammar, not two.

Verified live: 61 dividers, 165 transition rows, **7 undocumented commits still visible and flagged**, and the footer stating *"Last 60 commits touching docs/ or SNAPSHOT.yaml."* The tile's `Full history ›` link lands on it.

Grouping by day was in the DoD and is **not** done: with dividers carrying the date and commits already in order, a day header would be a third level of structure earning nothing at this density. Recorded as a decision rather than ticked — worth revisiting if the window grows.
