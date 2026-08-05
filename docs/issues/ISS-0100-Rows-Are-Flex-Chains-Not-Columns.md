---
type: "[[issue]]"
id: ISS-0100
aliases: ["ISS-0100"]
title: "Overview rows are flex chains, so every field sits wherever the one before it ended — nothing lines up down a column, and a 260px name column wastes 873px of row"
status: fixed
severity: medium
phase: "[[PHASE-016-The-Overview-Answers-Questions]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-05
source: ["Edwin 2026-08-05: 'we have the whole width usually to play with but features only get the first section… the status pills are not [aligned], the open, triage and doing items all have different indentations… phases show the status + x/x and x% + x waiting at different places directly after the feature title'"]
component: desktop-renderer
related: ["[[ISS-0097-Scoped-List-Rows-Have-No-Layout]]", "[[ISS-0098-The-Squares-Strip-Collapses-To-A-Column]]"]
fixed_by: ["[[TASK-0271-One-Line-Rows-In-Both-Panes]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# Rows are flex chains, not columns

## Measured

your-health, before:

```
scoped feature rows (row width 1133px)
  name column   260px fixed  → 873px of the row unused while names truncate
  chip left     352 · 315 · 347 · 340 · 364 · 328 · 340      seven rows, seven x
  annotation    551 · 569 · 557
  annotation id 596 · 611 · 603

project phase rows
  chip left     294 · 264 · 318 · 230 · 377 · 187
  count left    354 · 336 · 390 · 301 · 448 · 258
```

## Why

Both rows are **flex chains**. A flex item sits after the natural width of everything before it, so the chip's position is a function of that row's title length, and the annotation id's is a function of whether its lead word is `doing`, `open` or `triage`. Nothing can line up, because nothing has a column.

The 260px name is the same mistake inverted: a fixed width where the content is unbounded, in a row where every *other* field is bounded. Exactly backwards — **the one field with no natural limit is the one that should absorb the slack.**

[[ISS-0097]] and [[ISS-0098]] fixed *heights* and *fields touching*. This is the third property a row needs and the one that makes a list scannable: **fields at the same x on every line.**

## Fix

CSS Grid with declared columns on both row types, widths tokenised in one place and sized to each field's worst case (`superseded` for a status, `24/51 · 47%` for a count). The name takes `minmax(0, 1fr)`.

Two things the fix taught, both found by measuring after:

1. **Columns must be assigned, not inferred.** Auto-placement fills the first free cell, so a row lacking a pill slid its row-meta into the pill's column — chips still landed at five different x until every field got an explicit `grid-column`.
2. **One flexible column, not two.** With the title on `1fr` and the last column `auto`, the title computed to 518 / 593 / 701px across three rows — its width depended on how much row-meta each row happened to carry, and the chip moved with it. Fixing the last column fixed the first.

## Evidence it is fixed

```
scoped   name 1 width · frac 1 · squares 1 · chip 1 · annotation 1 · annotation-id 1
project  title 93 · chip 614 · count 699 · pill 804 · meta right-edge 1107
```

One value per column, on every visible row of both pages. Names are no longer truncated at 260px.


## A third thing, found by the guard

`.scoped-feat` had **three** rule blocks — a dead first-generation `display: block`, the new grid, and a one-line `align-items` patch. The guard read the first and reported a flex chain that had not existed for an hour; reading the last found the patch.

Both readings were the same mistake. A selector with three blocks has no single answer to *what does this rule say*, so the guard now requires exactly one and the blocks are merged. That is the third time this suite has hit the first-match trap, and the first time the fix removed the trap rather than stepping around it.
