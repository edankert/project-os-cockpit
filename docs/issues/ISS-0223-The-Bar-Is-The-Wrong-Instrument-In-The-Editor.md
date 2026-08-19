---
type: "[[issue]]"
id: ISS-0223
aliases: ["ISS-0223"]
title: "The segmented bar on the generated checks page is the wrong instrument for that surface — a percentage says the same thing in a tenth of the width"
status: fixed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: low
component: cockpit-desktop
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0222-The-Left-Pane-Groups-By-Tier-And-Nothing-Else]]", "[[DES-0012-Tests-In-Two-Flows]]", "[[TASK-0520-The-Checks-Page-Groups-By-Surface]]"]
---

# A bar where a number belongs

Edwin, 2026-08-19: *"having the areas surfaces in the generated/derived acceptance tests editor I like but having the bar there doesn't make much sense, a % probably does make more sense."*

**The surfaces stay.** This is only about the instrument drawn beside them.

## Why the bar is wrong here and right on the overview

A segmented bar answers *"what is the shape of this set"* — how much is done against failing against stale. That is worth four segments on a **card the reader is scanning**, which is what the overview's phase strip is.

The generated checks page is not being scanned. **It is being worked**: a person opens a surface to walk its checks, and the rows below the header already say, individually and in full, exactly what the bar is summarising. So the bar restates the thing the reader is looking at, in a wide horizontal element, once per surface — 77 times on `your-trainer`.

A percentage is the same claim at a glance and leaves the width for the surface's name.

## Suggested fix

1. `checkProgress()` gains a compact form — `82%` with the same title text the bar carries, so the detail is still one hover away.
2. The generated page's **surface** headers use it. The **tier** header keeps the full bar: a tier is a set the reader scans before choosing where to work, which is the case the bar is for.
3. The percentage counts what the bar's `done` segment counts, so the two cannot disagree — one predicate, as [[TASK-0533]] holds for the run list and the gate.
4. **The stale distinction must survive the compression.** The bar draws a stale tick apart from `done` because folding them made `your-trainer`'s honest blocking number 113 read as 60. A percentage that quietly re-merges them is that defect wearing a smaller element: if any check in the surface is stale, the number is marked.

## Done when

- [x] Surface headers on the generated page show a percentage; tier headers keep the bar.
- [x] The percentage and the bar are computed from one predicate.
- [x] A surface holding a stale tick is visibly distinguished from one that is not.

## Fixed 2026-08-19 — [[TASK-0551]]
