---
type: "[[issue]]"
id: ISS-0091
aliases: ["ISS-0091"]
title: "Two levels of one tree drew different expand handles, and a group head's id shrank to 7px because flex:none was scoped to rows"
status: fixed
severity: low
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["Edwin 2026-08-03: 'I still cannot see the full phase-ids and why would we use different open/close handles for the tree-nodes for phases and features? Can we use the smaller features ones throughout?'"]
component: desktop-renderer
related: ["[[ISS-0090-Phase-Rows-And-The-Missing-Id-Column]]"]
fixed_by: ["[[TASK-0275-Settled-Groups-Are-Collapsed-Cards]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# Two handles, and a shrinking id

## The id

Measured across the features navigator:

```
PHASE-005   40px shown of 62 needed
PHASE-006   56px shown of 62
PHASE-007    7px shown of 62      <- eleven percent of it
```

`.nav-item-line .nav-id { flex: none; }` was scoped to **rows**. In a group *head* the id is a flex child of `.group-header-inner`, which carries `min-width: 0` and `overflow: hidden` — so a long phase title took the space and the id gave it up. `PHASE-007 · Agent instrumentation (hooks-aware terminal)` is the longest title in the corpus and lost the most.

The ellipsis was also on the wrong element: **a flex container cannot ellipsise its children**, so `text-overflow` on the inner did nothing and `overflow: hidden` just clipped. It belongs on the name, which is the part that should shorten.

## The handles

Three shapes for one gesture:

| where | shape |
|---|---|
| group heads (`.group-chevron`) | an **8px caret** from two rotated borders |
| feature rows (`.nav-children-toggle`) | a **4px solid triangle** |
| the right pane and overview (`.ov-chev`) | a 4px solid triangle |

Two levels of the same tree disagreed, and the third surface already had the shape Edwin asked for. A caret built from two rotated borders also never quite sits on the text baseline — it needs a `translateY` nudge per state, which is why the two states used different ones.

## Fix

One handle. `.group-chevron` becomes `.ov-chev`'s triangle, geometry for geometry. `flex: none` on any `.nav-group-header .nav-id`, and the ellipsis moves to the name.

## Evidence it is fixed

No id in any group head is clipped, and the phase and feature handles measure identically.


## Measured after

**0 of 18** group-head ids clipped, where three were. The phase and feature handles are the same object — 12×12, a 4px solid triangle, rotated 90° when open — and both now match `.ov-chev`, which had the right shape all along.

## Worth noting

The surface Edwin pointed at as the odd one out was the one already correct. The right pane and the overview had been drawing the small triangle since [[FEAT-0043]]; the group heads kept an older caret, and the feature toggle I added at [[ISS-0088]] independently reinvented the triangle rather than reusing it. **Three declarations of one shape, two of them identical by coincidence** — the third only looked deliberate.
