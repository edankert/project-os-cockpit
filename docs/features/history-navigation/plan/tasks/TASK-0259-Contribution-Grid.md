---
type: "[[task]]"
id: TASK-0259
aliases: ["TASK-0259"]
title: "The contribution grid, replacing the sparkline, with days that are destinations"
status: done
phase: "[[PHASE-018-History-You-Can-Reach-And-Traverse]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0053-History-Navigation]]"]
parent: "[[FEAT-0053-History-Navigation]]"
effort: M
depends: ["[[TASK-0258-Activity-Grid-Payload]]"]
blocks: []
related: ["[[TASK-0256-History-Tile-On-The-Overview]]"]
tests: []
---

# The contribution grid

## Definition of Done
- [x] A rolling 52-week grid, 7 rows, replacing `ov-history-spark` — the sparkline is **deleted**
- [x] Days before `first_commit` render as **absent** (hairline), visibly unlike a zero-activity day
- [x] Intensity uses the payload's buckets, so this repo's 199-day and its 6-day differ visibly
- [x] **Clicking a day scrolls History to that day** — a cell is a destination, not a decoration
- [x] Hover names the date and both counts
- [x] Year controls render **only** when history spans more than one year
- [x] Month labels along the top, so a cell is locatable without hovering
- [x] Readable without colour — intensity must not be the only channel

## Steps
- [x] Build the grid from the payload; column = ISO week, row = weekday
- [x] Anchor each commit divider with a date id so a click can scroll to it
- [x] On the overview tile the grid replaces the header sparkline; on `~history` it sits above the timeline
- [x] Test: bucket assignment, the absent/zero distinction, and that a click resolves to a date anchor

## Notes

**A cell that does not navigate is the sparkline again.** The thing it replaces was pure ornament; shipping this without the click working would be the same ornament at higher resolution, and the entry-point complaint would be unanswered.

**Colour cannot be the only channel.** Five intensity steps of one hue is exactly the encoding [[DES-0004]] refused for the phase squares. A size or border step alongside the fill keeps it readable in greyscale and for a colour-blind reader.

## Done 2026-07-30

`contribution-grid.ts` as a pure module (dates and counts in, a grid description out), rendered by `renderer.ts`. Same split as `health-marks.ts` and `validation-rows.ts` — the PHASE-013 review's lesson, applied by default now rather than after a reviewer demonstrates it.

### Live pass

```
371 cells   absent 286 · empty 69 · step1 5 · step2 4 · step3 3 · step4 4
13 month labels   0 year controls   "since 2026-05-07"
legend: steps ≤22, ≤36, ≤64, more — scaled to this project's own busiest days
sparkline: gone
```

**286 absent vs 69 empty** is the correction working: the grid distinguishes "the project did not exist" from "nothing happened". Without it this repo would show forty weeks of apparent neglect.

**Zero year controls**, correctly — one year of history offers nothing to navigate to.

### The live pass caught a real bug, and it is the one this task warned about

The note said *"a cell that does not navigate is the sparkline again"*. The first cut navigated to `~history` and scrolled to a `data-date` anchor — which works only for dates inside the loaded window. The grid spans all history; the page loads 60 commits. **Clicking 2026-05-07 landed on 2026-07-28**, the oldest commit that happened to be loaded, with nothing indicating anything was wrong.

Fixed by anchoring the window instead of scrolling into it: `~history/<date>` passes `until=` to the payload, so the day is loaded by construction and the scroll cannot miss. Re-verified: clicking the 2026-05-07 cell lands on the 2026-05-07 divider, header reads *"what changed state on or before 2026-05-07"*.

The uncommitted band is suppressed for an anchored window — work in flight belongs to now, and showing today's unsaved edits above a window ending in May would place them inside May.

Guarded by four tests including a malformed-`until` case, since `until` is the only caller-supplied value reaching the git argv. Mutation-verified both ways.

### Second channel, as required

Intensity carries an inset ring that thickens with the step, so the scale survives greyscale and colour-blindness. Five shades of one hue is the encoding [[DES-0004]] refused for the phase squares, and it would have been the easy thing to copy from GitHub.
