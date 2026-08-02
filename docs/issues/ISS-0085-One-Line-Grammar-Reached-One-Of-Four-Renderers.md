---
type: "[[issue]]"
id: ISS-0085
aliases: ["ISS-0085"]
title: "The one-line grammar reached one of the left pane's four row renderers, and the subtitle put a second line back on that one"
status: fixed
severity: medium
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["Edwin 2026-08-02: 'in the left pane, I still see for features and issues and possibly others that there are multiple lines, let's remove the second line for these items. Also for some types (risks, requirements, designs and plans under features), they still use the more complex format (the review tab shows more the simpler format that we should be using for the left side as well)'"]
component: desktop-renderer
related: ["[[FEAT-0057-The-Record-Grammar]]", "[[TASK-0271-One-Line-Rows-In-Both-Panes]]"]
fixed_by: ["[[TASK-0271-One-Line-Rows-In-Both-Panes]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# The grammar reached one renderer of four

## What

[[TASK-0271]] rewrote `navItem` and stopped. The left pane has **four** row renderers, and `pickItemRenderer` chooses between them per group:

| renderer | used by | state |
|---|---|---|
| `navItem` | features, issues, tasks | rewritten — but see below |
| `navItemStacked` | **risks, designs** | untouched, two lines plus a mono subtitle |
| `navItemNested` | **requirements and plans under features** | untouched, two lines |
| `navItemCompact` | the Library docs tree | already one line; a filename row, out of scope |

And the rewritten one still renders `item.subtitle` as a second paragraph, so the rows it *did* fix are two lines again wherever the server sends one — which is every feature (`goal`), every design and every risk (`_first_body_paragraph`).

## Measured

Live, `your-health`'s workspace:

```
FEATURES   nav-item-line    56 rows, max 66px   "FEAT-0038 | Load & Refresh Feedback | AGENT | review | | Ev…"
           nav-item-nested 103 rows, max 49px
ISSUES     nav-item-line    36 rows, max 42px
           nav-item-stacked  5 rows, max 90px   "RISK-0001 | open | | Vendor-locked devices…"
DESIGN     nav-item-stacked  1 row,  max 56px
```

50 rows carry a subtitle. The target is 27px; nothing is at it.

## Why it happened

The task said "a nav row renders `ID · title · chip` on one line" and I checked the one renderer I had edited. `pickItemRenderer` is three lines away from `navItem` and I never followed it. The guard was written against `navItem` too, so it agreed with me.

**The shape to remember: a guard written from the same reading as the change confirms the reading, not the behaviour.** The height check should have run over every renderer the picker can return, and it will now.

## Fix

One row builder, used by all three lifecycle renderers, differing only in an indent class. The subtitle is dropped from the left pane entirely — it is the second line, and the pane is a selection list, not a summary.

`navItemCompact` stays as it is: a filename with a file icon, already one line, and not a lifecycle row.

## Evidence it is fixed

Every renderer `pickItemRenderer` can return produces a 27px single-line row, asserted over all of them rather than over one.
