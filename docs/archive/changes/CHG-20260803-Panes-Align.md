---
type: "[[change]]"
id: CHG-20260803-Panes-Align
title: "A phase sits left of its own features again, and every left pane uses one heading style, one row height and one title column"
status: merged
reviewed_by: model:claude-opus-5
review_date: 2026-08-03
review_verdict: approved
date: 2026-08-03
owner: user:edwin
component: [static, desktop-renderer]
related: ["[[PHASE-022-Completed-Work-Gets-Quieter]]", "[[ISS-0093-Nested-Padding-And-Two-Heading-Styles]]"]
---

# The panes align

## What changed

**A phase is no longer indented further than its features.** Its id sat at 45px from the pane edge — 23 right of the overview's, and 2px right of the features nested beneath it. It is now at 36, with its features at 46.

**Every navigator matches.** Measured across features, tasks, issues and design:

| | |
|---|---|
| section heading | 15px tall, 10px / 700 |
| row | 24px, left 12 |
| row title | 18px, left 109, 12px / 400 |

Three things had drifted: the navigators had their own section-heading style (11px/600, spaced with padding) alongside the overview's (10px/700, margin); design's rows were 27px because a status chip was present; and titles started at three different x because the id column was as wide as each mode's longest id.

**Not unified, deliberately:** a group head naming a *thing* stays 12.5px/400 and one naming a *category* stays 11px/600. That is the rule from [[ISS-0089]], not drift.

## Paths

- both stylesheets — the nested paddings, `.nav-set-heading`, the row chip, the id column
- `desktop/src/renderer/renderer.css` — the body carries the indent rather than the group

## Restart required

Mode 3 is a built bundle. The change is live after the desktop app restarts.
