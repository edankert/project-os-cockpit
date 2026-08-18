---
type: "[[task]]"
id: TASK-0520
aliases: ["TASK-0520"]
title: "Restore tier → surface → rows on the generated page, with a progress bar per group"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
parent: "[[FEAT-0128-The-Tests-View-Leads-With-The-Work]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Restore tier → surface → rows on the generated page, with a progress bar per group

DES-0012 D1. Reverts TASK-0513, which flattened the surface headings away — the request it answered was about the left pane, and it was applied to the page.

The bar is the one the overview already uses for phases (`.ov-phase-under` / the segmented `.ov-mixbar`), per surface and per tier.

## Done 2026-08-19

`paintCheckList` renders **tier → surface → rows** again, and `checkProgress` draws the overview's own `.ov-mixbar` per surface and per tier.

**Four segments, because three would lie.** `done` / `to run` are the obvious pair; `attention` carries a check run-and-failed or not understood, which is neither; and a **stale** tick is drawn apart from `done` rather than folded in — that folding is what made `your-trainer`'s honest blocking number 113 against a reported 60. The percentage counts only unstale ticks, and a guard asserts it.

**One process note.** The first attempt at this edit computed an empty `old` slice — the second index preceded the first — so `str.replace("", new, 1)` inserted the whole block at **position 0 of the file**. `tsc` caught it immediately because the code referenced names that do not exist at the top of a module. That is the sixth silent-substitution failure this phase and the first one a type-checker caught for free; the pattern is always the same, an anchor assumed rather than verified.
