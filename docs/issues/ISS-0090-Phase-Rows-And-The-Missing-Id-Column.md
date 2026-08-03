---
type: "[[issue]]"
id: ISS-0090
aliases: ["ISS-0090"]
title: "Phase rows still differ from the overview's, and a plan's empty id drops it out of the id column so it sits 78px left of its sibling requirements"
status: fixed
severity: low
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["Edwin 2026-08-03: 'Can you make the phases on the features/phases page look the same or similar as the phases on the overview page? Remove the pills from there, since these are in the completed section. Any plans underneath the features should be indented the same as the requirements.'"]
component: desktop-renderer
related: ["[[ISS-0089-A-Card-Head-Names-A-Category-Not-A-Thing]]"]
fixed_by: ["[[TASK-0275-Settled-Groups-Are-Collapsed-Cards]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# Phase rows, and the missing id column

## The two rows, measured

[[ISS-0089]] moved the phase head off the label treatment and onto the row treatment. It stopped one step short of the row it was aiming at:

| | overview `scope-row` | features head |
|---|---|---|
| height | 24px | 28px |
| weight | **400** | 500 |
| colour | `rgb(166,166,166)` — `--text-muted` | `rgb(222,222,222)` — `--text` |
| gap | 7px | 6px |
| trailing | `✓ 8`, green, 10.5px | `2 · done` **and** a `done` pill |

The pill is the visible part. It is also redundant twice over: the summary beside it already says `done`, and the whole band it sits in is headed `Completed`. The overview never had one — it says `✓ 8` and stops.

## The plan's indentation

A plan child is built with `"id": ""` (`_plan_child_item`, deliberate — an untyped plan still gets a row). `buildNavRow` renders the ID span only `if (item.id)`, so a plan has none and its **title takes the id column's place**.

Measured under FEAT-0006, nine requirements and a plan:

```
requirement titles   left: 153px
plan title           left:  75px      <- 78px adrift
```

Two rows in one list, on two different grids. The empty id was a reasonable choice for a note that has no ID; **what it did not account for is that the id column is a column** — an absent value has to occupy it, not skip it.

## Fix

- The phase head takes `scope-row`'s weight, colour, gap and trailing form: `✓ N` for a settled phase, the plain count for a live one. No pill.
- A nested child with no ID renders its **type** as the handle — `PLAN` — type-coloured like every other ID. An absent value that still occupies its column, and it reads as what it is.

## Evidence it is fixed

A phase row and a scope row are the same row; a plan's title starts where its sibling requirements' titles start.


## Measured after

| | overview `scope-row` | features head |
|---|---|---|
| height | 24px | **24px** |
| weight | 400 | **400** |
| colour | `rgb(166,166,166)` | **`rgb(166,166,166)`** |
| gap | 7px | **7px** |
| trailing | `✓ 8` green | **`✓ 3`, `rgb(124,182,163)`** |
| pill | none | **none** |

Under FEAT-0006 — nine requirements and a plan — every title now starts at the same x: **one distinct value across ten rows**, where there were two.

## The part that took three attempts

Giving the plan a `PLAN` handle closed 78px of the gap and left 27. Setting a `min-width: 9ch` on the column closed all but 6. The last six were the stand-in's own `font-size: 10px`: **`ch` is relative to the font**, so a smaller handle makes a narrower column and puts its row back on a grid of its own. Only the opacity distinguishes it now.

A column is only a column if every cell in it is the same width — including the ones standing in for something absent.
