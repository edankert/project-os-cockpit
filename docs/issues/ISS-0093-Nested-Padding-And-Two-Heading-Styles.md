---
type: "[[issue]]"
id: ISS-0093
aliases: ["ISS-0093"]
title: "Three nested paddings pushed a phase id further right than the features beneath it, and a second section-heading style was written without checking the first existed"
status: fixed
severity: low
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["Edwin 2026-08-03: 'the phases nodes are further indented then the feature nodes underneath, can you move the phases nodes to the left closer to what they look like on the overview view?' and 'Also make sure the left hand-panes all align on the same fonts, widgets and sizings'"]
component: desktop-renderer
related: ["[[ISS-0092-Severity-Buckets-Straddled-The-Completed-Split]]", "[[ISS-0089-A-Card-Head-Names-A-Category-Not-A-Thing]]"]
fixed_by: ["[[TASK-0271-One-Line-Rows-In-Both-Panes]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# Nested padding, and two heading styles

## The indent

Measured from the pane's left edge, a phase id sat at **45px** — 23 right of the overview's 22, and **2px right of the features nested beneath it**. A parent indented further than its children is the one arrangement a tree must never produce.

Nothing was individually wrong. Three paddings compounded — the band's 6, the group's 2, the head's 8 — and the chevron's 7px gap sat on top. Each was chosen sensibly and in isolation.

## The audit

Asked to align the panes, I measured all six. Three things disagreed:

| | navigators | overview / review desk |
|---|---|---|
| section heading | 11px / 600, spaced with **padding** | 10px / 700, spaced with **margin** |
| row height | 24px | — |
| design's rows | **27px** | — |
| title column | 98 / 103 / 96px | — |

- `.nav-set-heading` is a second style for a role `.scope-heading` already filled. I wrote it without checking.
- Design's rows were 3px taller **only because a status chip was present** — the same failure mode as the group head at [[ISS-0087]]: the chip is the tallest thing on the line and it is not the line's subject.
- Titles started at three different x because the id column is as wide as the longest id in the mode, and that differs.

**Deliberately not unified:** a head naming a *thing* is 12.5px/400 and one naming a *category* is 11px/600. That is [[ISS-0089]]'s rule, not drift.

## Fix

- Band padding 6→4, group padding 2→0, head padding 8→4, chevron gap tightened. The **body** takes the 5px indent instead of the group, so the head moves left while its children stay indented from it.
- `.nav-set-heading` adopts `.scope-heading`'s metrics and spaces itself with margin.
- A chip cannot set a row's height.
- One id column width across every navigator.

## Evidence it is fixed

Phase id 36, its features 46. Every navigator's rows: 24px, left 12, titles at 109.


## Measured after

Indent: phase id **36**, its features **46**. Parent left of children, and 9px closer to the overview's 22 than the 45 it started at.

Across all four navigators, identical:

| | |
|---|---|
| section heading | 15px tall, 10px / 700 |
| row | 24px, left 12 |
| row title | 18px, left 109, 12px / 400 |

Design's rows were the outlier at 27px and are now 24.

## The mutation that did not apply

One of the four checks reported green while its mutation had silently failed to match — my replacement string was written against an older version of the block. It looked exactly like a passing guard.

`assert old in s` in the mutation script, not just in the guard: **a mutation that does not apply is indistinguishable from a guard that does not work**, and only one of those is worth knowing about.
