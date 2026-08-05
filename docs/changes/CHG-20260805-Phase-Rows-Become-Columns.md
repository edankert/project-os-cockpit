---
type: "[[change]]"
id: CHG-20260805-Phase-Rows-Become-Columns
title: "Overview rows get a real column model, four state fields become three, and the phase row's fields settle into id · title · progress · state"
status: merged
owner: user:edwin
created: 2026-08-05
updated: 2026-08-05
source: ["Edwin 2026-08-05, four passes: 'the status pills are not aligned', 'do we need all those states or can they be collapsed', 'move this to the right', 'move this to after the attention but make sure all the states align'"]
commit: ""
pr: ""
impacts: [desktop-renderer]
issues: ["[[ISS-0100-Rows-Are-Flex-Chains-Not-Columns]]", "[[ISS-0101-Four-State-Fields-One-Counted-Twice]]", "[[ISS-0102-The-Attention-Pill-Borrowed-Another-Surfaces-Words]]"]
features: []
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[PHASE-016-The-Overview-Answers-Questions]]", "[[CHG-20260805-Scoped-Overview-Rows]]", "[[TST-0023-Completed-Work-Ordering]]"]
---

# Overview rows become columns

## Summary

Three related changes to the project overview's phase rows and the phase page's feature rows, landed over four passes.

**Rows have columns.** Both row types were flex chains, so every field sat after the natural width of the one before it: chips measured at six different x down the project overview and seven down a feature list. They are CSS Grid now, with each field assigned a column, widths tokenised in one place and sized to each field's worst case, and exactly one flexible column — the title, which is the only field with no natural limit ([[ISS-0100]]).

**Four state fields become three.** `x waiting` and `x in flight` were two readings of one phase and sat apart; `waiting` was also a word no other surface used. The progress field now carries the whole reading — `74/95 · 78% · 16 in flight · 20 attention` — and the trailing flags column holds `awaiting close-out` alone ([[ISS-0101]], [[ISS-0102]]).

**The fields settle in reading order.** `chevron · id · title · [flags] · progress · state`. Progress is right-aligned so the numbers end where the row ends; the state chip is left-aligned in a fixed last column so every chip starts at the same x. The state reads last because it is the row's verdict on everything before it — between the title and the numbers it split the sentence.

```
PHASE-0008  Feedback, Refresh & Energy      74/95 · 78% · 16 in flight · 20 attention   active
PHASE-0011  Nutrition: What Is Already…                                    0/10 · 0%   planned
```

## Impact

- Mode 3 only. The scoped overview and its phase rows are not rendered by mode 1's `cockpit.js`, so there is no twin to keep in step here.
- Mode 3 is a built bundle: live after the desktop app restarts.
- No payload, endpoint or note-format change. Presentation only.

## What it cost to get right

Two defects the passes produced, both worth remembering because both measured green:

1. **`grid-column` alone is a half-specification.** Moving the chip to the last column left it appended *before* the count in the DOM while owning a *later* column, and sparse auto-placement never moves its cursor backwards — so the count opened a second grid row and the progress field dropped under the title. Every x co-ordinate was still correct; only the screenshot showed it. Every child now pins `grid-row: 1`.
2. **A column keeps the width it was first sized for.** `--col-count` was 148px for `74/95 · 78%` and then silently absorbed `in flight` and `attention`, overflowing left into a flags column that happens to be empty in both corpora. Measured at its real worst case (213px) and sized to 216px; the never-rendered worst case — long count plus `awaiting close-out` — was synthesised and leaves 48px clear.

## Documentation Coverage (All Types Considered)

- features: not-applicable
- requirements: not-applicable
- tasks: updated
- issues: updated
- tests: updated
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new
- snapshot: updated

## Follow-ups

- [ ] `.scoped-feat-top` still has two rule blocks (`display: flex`, then `display: contents`). The second wins and the first is inert, but it is the same first-match trap [[ISS-0100]] removed for `.scoped-feat` — the block-count guard covers only two selectors.
