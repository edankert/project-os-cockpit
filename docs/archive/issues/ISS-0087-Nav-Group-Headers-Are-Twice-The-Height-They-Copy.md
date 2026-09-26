---
type: "[[issue]]"
id: ISS-0087
aliases: ["ISS-0087"]
title: "The navigator's group headers are twice the height of the context cards they were aligned to, because only their type was matched and not their padding"
status: fixed
severity: low
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["Edwin 2026-08-02: 'I still like the way things are presented (including the collapse and expand functionality) in the right pane a lot and this could be a nice way to present the stuff on the left as well. If anything it should at least use more of the minimum look of the overview pane.'"]
component: desktop-renderer
related: ["[[FEAT-0057-The-Record-Grammar]]", "[[ISS-0086-The-Rollup-Hid-The-Taxonomy]]"]
fixed_by: ["[[TASK-0272-Status-Said-Once-At-The-Head]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# The headers are twice the height they copy

## What

[[FEAT-0057]] matched the two panes' **type** and stopped there. Measured in the running app:

| | height | padding |
|---|---|---|
| left `nav-group-header` | **42px** | `10px 14px` |
| left completed band | 29px | `6px 10px` |
| right `ctx-card-head` | **22px** | `3px 2px` |
| right section `h3` | 16px | `0` |

Font size, weight, transform, letter-spacing and colour are already **identical** — 11px / 600 / uppercase / `--text-faint`. Every remaining difference is padding, plus a `background` and `border-bottom` the right pane's heads do not carry.

The features navigator renders **19 group headers**, so that gap is roughly **380px** of pure chrome, on a pane whose rows are 27px.

## Why it happened

I aligned the type because the type is what a "grammar" sounds like. Density is set by the box, and I never put the two headers side by side to compare — the same failure as [[ISS-0085]] (checked one renderer of four) and [[ISS-0086]] (collapsed heads as if they were bodies).

**Three corrections in a row, one cause: I verified the thing I changed rather than the surface it lives on.**

## Fix

`.nav-group-header` takes the context card head's box. Its `background` and `border-bottom` go too — a bar per group is what makes nineteen of them read as nineteen bars rather than as a list of names, and the right pane demonstrates that a head needs neither.

The group's own body loses its remaining inset for the same reason.

## Evidence it is fixed

A nav group header and a context card head measure the same height in the same app.


## Measured after

| | before | after |
|---|---|---|
| nav group header | 42px | **25px** |
| completed band | 29px | 24px |
| context card head | 22px | 22px |
| nav row | 24px | 24px |

Everything within 3px of everything else, which is what one grammar looks like when the box is matched and not only the font.

The last 3px is the chevron and the chip, which the context head does not carry — the chip was itself 21px against the head text's 16px, so it alone decided the height until it was trimmed to sit inside the line. The chip in a *row* is untouched: there it is the row's own subject.
