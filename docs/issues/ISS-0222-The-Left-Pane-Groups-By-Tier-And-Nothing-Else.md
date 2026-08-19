---
type: "[[issue]]"
id: ISS-0222
aliases: ["ISS-0222"]
title: "The surfaces and the progress bar landed on the generated page and not in the left pane — where they were asked for, and where every other progress bar in the tool lives"
status: fixed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: medium
component: cockpit-desktop
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[DES-0012-Tests-In-Two-Flows]]", "[[FEAT-0128-The-Tests-View-Leads-With-The-Work]]", "[[ISS-0223-The-Bar-Is-The-Wrong-Instrument-In-The-Editor]]", "[[TASK-0520-The-Checks-Page-Groups-By-Surface]]"]
---

# Right feature, wrong pane

Edwin, 2026-08-19: *"I was not very clear apparently, I expected the %bar and the areas/surface to group things in the left hand pane."*

## What is there now

`cockpit._acceptance_tier_groups` builds the nav's acceptance section from **`tier` alone**. Measured: three groups — Tier 1, Tier 2, Tier 3 — each a count and a link, with no surface level beneath them and **no progress of any kind**.

The surfaces and the segmented bar both exist, and both are on the **generated checks page** ([[TASK-0520]]).

## Why it went there

[[DES-0012]] records the request as *"I want to see a bar the same as we do for phases on the overview page … this could nicely be per scope/surface"*, and the note it was written into was about the generated page. So it was built where the note was, not where the sentence pointed — **"the same as we do for phases"** is a statement about the left pane, which is the only place a phase bar appears.

That is the failure worth recording: the request named its *model surface* and the implementation matched its *containing document*.

## Suggested fix

**Three levels in the nav, and the middle one is new:** tier → surface → count.

1. `_acceptance_tier_groups` gains a `children` level keyed on `area:`, the same field the generated page groups by. `area` and `section` are 1:1 in all three repos (21/21, 77/77, 20/20 — measured 2026-08-19), so there is one obvious key and no choice to make.
2. Each surface row carries a **percentage**, not a bar — the nav's rows are one line tall, and the phase bars Edwin is comparing to sit in the *overview's* cards, which are not one line tall. See [[ISS-0223]]: the same reasoning decides both, in opposite directions.
3. **The tier row keeps a bar**, because it is a group header with room for one and it is the level a person compares against a phase.
4. Collapsed by default. `your-trainer` has **77 surfaces**; expanding all of them into the nav is the wall [[REQ-0047]] exists to prevent, one pane to the left.

## Done when

- [x] The nav shows tier → surface → count, collapsed at the surface level.
- [x] A tier row carries a bar; a surface row carries a percentage.
- [x] Clicking a surface opens the generated page scrolled to it — the two panes agree about what a surface is, or the grouping is decoration.
- [x] Proved on `your-trainer` (77 surfaces) that the nav does not become the wall it was built to avoid.

## Fixed 2026-08-19 — [[TASK-0550]]
