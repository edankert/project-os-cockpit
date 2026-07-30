---
type: "[[task]]"
id: TASK-0260
aliases: ["TASK-0260"]
title: "A History button in the workspace rail, so the page is reachable from anywhere"
status: done
phase: "[[PHASE-018-History-You-Can-Reach-And-Traverse]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0053-History-Navigation]]"]
parent: "[[FEAT-0053-History-Navigation]]"
effort: S
depends: []
blocks: []
related: ["[[FEAT-0032-Agents-Screen]]"]
tests: []
---

# History in the rail

## Definition of Done
- [x] A History button in `.ws-rail-tools`, beside Agents
- [x] Navigates to `~history` from any page
- [x] Carries a title and an `aria-label`, like every button beside it
- [x] Reflects the active state when `~history` is open, as the other tools do

## Steps
- [x] Add the button, its icon and its handler
- [x] Test: a guard that the button exists and points at `~history`

## Notes

**The rail, not the top bar.** Top-bar buttons set `currentNavMode` — each changes what the **left pane lists**. History has no left-pane listing, so putting it there would mean a mode that modes nothing. `~agents` is the exact precedent: a page, reached from a rail tool.

Bending the top bar's meaning to fit one page is how a surface's grammar erodes, and [[PHASE-010]] spent itself undoing that class of drift.

## Done 2026-07-30

`#history-toggle` in `.ws-rail-tools`, beside Agents, using the `history` glyph **that already existed** in `GROUP_ICONS` — I had added a second one and the compiler caught the duplicate key.

Verified live: from `~overview`, clicking it lands on `~history` with 170 rows and the grid rendered above the timeline.

Guarded by a test asserting the button exists in the built HTML *and* that its handler navigates to `~history` — a button with no handler would pass a markup-only check.
