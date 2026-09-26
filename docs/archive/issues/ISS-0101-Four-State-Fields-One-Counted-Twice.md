---
type: "[[issue]]"
id: ISS-0101
aliases: ["ISS-0101"]
title: "The phase row carried four state fields and counted some items twice, and a feature's own status rendered after the squares describing its children"
status: fixed
severity: medium
phase: "[[PHASE-016-The-Overview-Answers-Questions]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-05
source: ["Edwin 2026-08-05: 'I don't know what the x waiting item is and the x/x and x% + x in flight seem to be very much related… do we need all those states or can they be collapsed into a fewer set?' and 'the phase states belong to the feature but they are shown after the item boxes'"]
component: desktop-renderer
related: ["[[ISS-0100-Rows-Are-Flex-Chains-Not-Columns]]", "[[DES-0004-Attention-In-The-Squares]]"]
fixed_by: ["[[TASK-0271-One-Line-Rows-In-Both-Panes]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# Four state fields, one counted twice

## What `waiting` was

`_needs_human()` — a specific human action is outstanding: `triage`, `review`, a test that is `ready` (defined, never run), a `failing` test. DES-0004's corner dot, summed.

Edwin could not say what it meant, and the reason turns out to be structural rather than a naming slip.

## The double count

The phase row showed four state fields:

```
active   |   24/51 · 47%   |   15 waiting   |   10 in flight · 2 triage · 1 in review
   ↑              ↑                ↑                  ↑
 status       progress        aggregate        …and a SUBSET of that aggregate,
                                                itemised three columns later
```

`15 waiting` counts triage + review + ready + failing. The row-meta then itemised `2 triage · 1 in review` — **members of the set the pill had just totalled**. One line, two representations of overlapping data, neither labelled as related to the other.

A number that is partly repeated beside itself under a different name is not a number a reader can interpret. "I don't know what the x waiting item is" is the correct response.

Separately, `24/51`, `47%` and `10 in flight` are **three readings of one fact** — how far this phase has got — and sat in three columns with an unrelated pill between two of them.

## Collapsed to three

```
active   |   24/51 · 47% · 10 in flight   |   20 needs you
  own state          progress                  attention
```

- **Progress** is one field, because it is one question.
- **Attention** is one field, named for what `_needs_human` computes, with the breakdown in its tooltip — where a total that wants explaining belongs. It stays a count and not ids: a header listing ids would be the retired Waiting-on-you list again ([[ISS-0068]]), and it still has to exist because a *collapsed* phase renders its squares with `offsetParent` null ([[ISS-0024]]).
- **`awaiting close-out`** survives in the row-meta as the one fact neither field can carry: every item resolved, phase not closed.

## The feature's own status

On the scoped page a feature rendered `name · fraction · squares · chip`. The fraction and the squares describe its **children**; the chip is the feature's **own** state. Last in the row, `planned` read as a label on the squares beside it.

It now sits immediately after the name, ahead of everything about the children — `FEAT-0070 Sessions in Health Connect · doing · 0/3 · □□□`.

## Measured after

```
project   chip 611 · progress 696 · needs-you 853 · 0 overlaps · 0 clipped
scoped    chip 390 · squares 520 · annotation 700 · heights 32–33
```

Widening the progress field to hold `in flight` needed the column token widened with it — at the old 96px the text ran *under* the pill beside it. A merged field needs a re-measured column; the grid will not tell you, it will just overlap.
