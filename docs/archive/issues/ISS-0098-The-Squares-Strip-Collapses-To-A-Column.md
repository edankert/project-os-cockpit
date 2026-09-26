---
type: "[[issue]]"
id: ISS-0098
aliases: ["ISS-0098"]
title: "A feature's task squares wrap into a one-square-wide column when the row is tight, blowing one row to 116px against its neighbours' 32"
status: fixed
severity: medium
phase: "[[PHASE-016-The-Overview-Answers-Questions]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-05
source: ["Edwin 2026-08-05: 'the feature section (very much jumbled up)' — your-health PHASE-0010"]
component: desktop-renderer
related: ["[[DES-0004-Attention-In-The-Squares]]"]
fixed_by: ["[[TASK-0271-One-Line-Rows-In-Both-Panes]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# The squares strip collapses to a column

## Measured

your-health PHASE-0010, feature rows:

```
row heights   32 32 32 33 33 32 33 116 33 33 32 93
FEAT-0071's squares strip   width 9px · height 105px · 9 squares · flex-wrap: wrap
```

Nine squares in a **9px-wide column**, 105px tall. The neighbouring rows are 32px. `Loose items` does the same at 93px with 37 squares.

## Why

`.scoped-feat-sqs` is a wrapping flex container with **no minimum width** and no reserved column. Its row-mates — the name, the fraction, the chip, and the annotation trail — are all allowed to take what they want, so on a row where the annotations are long the squares container is squeezed to a single square's width and wraps to nine lines.

It is not a squares bug: the strip does exactly what `flex-wrap: wrap` says. **The row has no column model**, so whichever child is most compressible absorbs every shortfall — and a 3-pixel square is the most compressible thing on the row.

## Fix

Give the row a column model rather than letting flex negotiate it per row: a fixed width for the squares strip sized to a sensible run (with overflow expressed as a `+N` the way the fleet grid already does), a `min-width: 0` title that ellipsises, and the annotation trail clamped to one line with the rest behind its existing disclosure.

**Rows in a list must not be free to have different heights** — that is what makes a list scannable, and it is the same rule ISS-0093 established for the navigator's rows and ISS-0087 for its heads.

## Evidence it is fixed

Every feature row in PHASE-0010 measures the same height, and the squares read as a horizontal run at every column width the pane supports.


## Fixed 2026-08-05

Three changes, because the row had three ways to grow:

1. `.scoped-feat-sqs` is `flex: 0 0 auto` and `flex-wrap: nowrap` — it can no longer be squeezed below its content, nor wrap.
2. The strip renders at most `FEATURE_SQUARE_LIMIT` (12) squares and then `+N`. Capping rather than shrinking is the honest fix: squares are a per-item signal, and forty of them say no more than twelve plus a number.
3. The annotation trail shows **one** item — failing, then doing, then triage, then next — with `+N` carrying the rest in its tooltip. Three of them stacked 78px tall.

Measured on your-health PHASE-0010, twelve feature rows:

```
before   32 32 32 33 33 32 33 116 33 33 32 93     (min 32, max 116)
after    32 32 32 33 33 32 33  33 33 33 32 32     (min 32, max 33)
```

**A row whose height depends on its child count is not a row.**