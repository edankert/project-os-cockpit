---
type: "[[issue]]"
id: ISS-0092
aliases: ["ISS-0092"]
title: "A severity bucket holding both open and fixed issues had to be placed whole, so one open issue could keep fifty-six fixed ones above the completed divider"
status: fixed
severity: medium
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["Edwin 2026-08-03: 'can we remove the lines between the phases, can we make the completed section a card like is done on the other pages? On the issues view left hand pane, can we have 2 sets of cards (based on severity), one set with done items underneath the completed items and the set with open items at the top?'"]
component: server
related: ["[[FEAT-0058-One-Shape-Per-Navigator]]", "[[ISS-0091-Two-Handles-And-A-Shrinking-Id]]"]
fixed_by: ["[[TASK-0276-The-Divider-Where-Names-Do-Not-Say-Finished]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# Severity buckets straddled the completed split

## What

`_issues_groups` bucketed by **severity alone**, and the navigator's live/completed split then had to place each bucket **whole**. A severity holding one open issue and fifty-six fixed ones went live — so `Medium · 57` sat above the divider with fifty-six fixed issues inside it.

Today's corpus hides this: every issue is fixed, so every bucket is homogeneous by accident and the split looks correct. Opening a single medium issue would have restored the fault silently.

## Fix

Split on **completion first**, then bucket each half by severity. Every bucket becomes homogeneous, so the navigator's existing rule — settled groups go below the divider — places each half correctly without knowing anything about severity.

`Medium` can now appear twice, once per half. The keys carry the half (`medium`, `medium:done`) because the collapse memory keys off them and two cards for one severity would otherwise share a state.

Verified against a corpus built to disagree:

```
medium        Medium         ['ISS-0001']   <- open
high:done     High           ['ISS-0003']
medium:done   Medium         ['ISS-0002']   <- fixed
risk:high     Risks · high   ['RISK-0001']
```

## Also, two pieces of chrome

- **The lines between phases go.** Eighteen frames read as clutter, so [[ISS-0089]] replaced them with eighteen hairlines — which read as a table. The rows are separated by being rows; the overview's scope pane has never needed anything between them.
- **The completed band becomes a card.** It was a heading over a border-top, on the reasoning that a card containing cards nests two identical frames. That holds where its children are framed and **not in the features view**, where the phases inside it are things and carry no frame. One border per object: the band gets it, its children do not.

## Evidence it is fixed

A severity with both open and fixed issues renders two cards, one in each set; the features pane has no rule between phases and one frame around the completed section.


## Measured after

Issues view: **`Open · 3`** (the three risk severities) above, **`Completed · 4`** (critical, high, medium, low) below. Features view: **zero** rules between phases, one card frame around the completed section and none on the phases inside it.

## The guard that had to be reversed

`test_nav_groups_carry_the_card_frame` asserted the band was **frameless** — written at [[ISS-0088]], on the reasoning that a card containing cards nests two identical borders. That reasoning was sound where the band's children are framed (tasks, issues) and wrong in the features view, where its children are *things* and carry no frame, so the section read as whatever was left at the bottom.

The rule that survives both cases is **one border per object**. The guard now asserts that instead, and records why it flipped — a reversed assertion with no explanation is indistinguishable from a broken one.
