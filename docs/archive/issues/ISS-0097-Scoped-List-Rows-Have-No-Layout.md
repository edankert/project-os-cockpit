---
type: "[[issue]]"
id: ISS-0097
aliases: ["ISS-0097"]
title: "The scoped overview's Verification and Remaining rows have no layout, so the id, the title and the meta render as one run-on string"
status: fixed
severity: medium
phase: "[[PHASE-016-The-Overview-Answers-Questions]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-05
source: ["Edwin 2026-08-05: 'the spacing and the way the different items are presented is not great' — project-os-cockpit PHASE-006 verification, your-health PHASE-0010 remaining"]
component: desktop-renderer
related: ["[[FEAT-0057-The-Record-Grammar]]"]
fixed_by: ["[[TASK-0271-One-Line-Rows-In-Both-Panes]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# Scoped list rows have no layout

## What

Captured from the running app:

```
PHASE-006 · Verification
  TST-0005GET /api/render — HTML fragment + metadata, error shapes, path-traversal guardauto · ran 2026-05-25  passing
  TST-0009Agent-state pipe — storage, endpoint, SSE delivery, decay, CLIauto · ran 2026-05-25  passing

your-health PHASE-0010 · Remaining
  FEAT-0070Sessions in Health Connect  doing
  TASK-0208Import stage totals onto nights the device recorded coarsely  doing
```

The id runs into the title, and the title runs into the meta. Three separate facts read as one string.

## Why

`buildRemainingList` appends `id`, `title` and a chip as **plain spans into a bare `<li>`**, and neither `.ov-waiting-list li` nor `.verification-list li` declares any layout — no `display: flex`, no `gap` — in either stylesheet. Inline elements with no whitespace between them concatenate; that is all this is.

The stylesheets *do* style the parts (`.verification-meta` has `flex: none` and `margin-left: auto`, which only makes sense inside a flex row) — so the layout was intended and never written. `margin-left: auto` on a non-flex parent silently does nothing, which is why the meta sits flush against the title rather than at the right edge.

## Fix

Give both row types the row grammar the rest of the cockpit uses: flex, `gap: 7px`, an id column that does not shrink, a title that ellipsises, and the meta and chip pushed right. Same values as `.nav-item-line` — this is that row, in another pane.

## Evidence it is fixed

`TST-0005 · GET /api/render — … · ran 2026-05-25 · passing` reads as four fields, and the same row in the navigator and the scoped overview measure the same.


## Fixed 2026-08-05

`.ov-waiting-list li` gains the row grammar — flex, `gap: 7px`, a non-shrinking id column at `min-width: 9ch`, an ellipsising title, and a chip constrained so it cannot set the row's height. Measured after:

```
FEAT-0070 | Sessions in Health Connect | doing        display: flex · gap: 7px
TST-0005  | GET /api/render — HTML fragment + …
```

Four fields, four columns, in both the Verification and Remaining lists.

## And a retirement the fix nearly undid

Writing the first CSS rule these rows have ever had made `test_the_waiting_on_you_list_is_gone` fail — ISS-0068 retired the *"Waiting on you"* section and its guard refuses to see `.ov-waiting` in the stylesheet at all.

The guard was right and the class names were wrong: the Remaining and Verification lists had been **squatting on the retired prefix** since the section went, invisibly, because nobody had styled them. They are now `scoped-rowlist` / `scoped-row-id` / `scoped-row-title` / `scoped-row-clear`.

**Styling a live surface under a dead name is how a retirement gets quietly undone.** The guard caught it at the first moment anyone wrote a rule — which is exactly when it was cheapest to catch.
