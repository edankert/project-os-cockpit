---
type: "[[issue]]"
id: ISS-0102
aliases: ["ISS-0102"]
title: "The attention count borrowed the agent-state vocabulary, a red used nowhere else for it, and the shape of a control it did not have"
status: fixed
severity: low
phase: "[[PHASE-016-The-Overview-Answers-Questions]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-05
source: ["Edwin 2026-08-05: 'Not sure I like this needs you red box, I think we use different terminology and colours elsewhere?' then 'Where does the attention pill take me?' and 'If it doesn't take me anywhere can we have the x attention directly after the x in flight option and use the same font but different color?'"]
component: desktop-renderer
related: ["[[ISS-0101-Four-State-Fields-One-Counted-Twice]]", "[[DES-0004-Attention-In-The-Squares]]"]
fixed_by: ["[[TASK-0271-One-Line-Rows-In-Both-Panes]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# The attention count borrowed another surface's words

## Three things wrong, all mine, all from [[ISS-0101]] the day before

**The word.** The stat legend on that same page reads `done · in flight · attention · backlog`, the right pane has an ATTENTION section, and three CSS classes already carry `is-attention`. I named the pill `needs you` — which is the **agent-state** vocabulary: `needs-input` formats to exactly that phrase, for a terminal waiting on a keystroke. Two unrelated ideas under one name, on one screen.

**The colour.** `--status-blocked`, a red used nowhere else for this. Every other attention marker — `.ov-phase-attention`, `.ov-health-flag.is-attention`, `.scoped-next-lead.is-attention` — uses `--severity-medium`, amber. Red read as an alarm; this is a queue.

**The shape.** Edwin asked where it took him. Nowhere: an inert `<span>` styled as a pill, on a page whose premise is that every number leads somewhere.

## What the third one taught

The obvious fix was to make it navigate, and I did — to the phase. Then it became clear that **clicking the row already opens the phase**, so the navigation would have been decoration on a duplicate.

> A number that leads nowhere should not be dressed as a control.

So it is not a pill at all. It reads inline after `in flight`, in the progress field's own font and size, differing only in colour — one more reading of the same phase, on the same line as the others:

```
PHASE-0008  Feedback, Refresh & Energy   active   74/95 · 78% · 16 in flight · 20 attention
```

Measured: same `font-size`, `font-weight` and `font-family` as the text it joins; `rgb(209,181,97)` against the progress field's `rgb(166,166,166)`.

## A guard that had to move with it

`test_the_phase_header_carries_what_squares_cannot` ([[DES-0004]]) asserted `ov-phase-pill is-waiting` was in the renderer. The requirement it protects is real — a *collapsed* phase renders its squares with `offsetParent: null`, so the header is the only place that count survives — but it was asserting the **widget** rather than the **fact**. It now checks that the header reports the count from the payload at all, which is what DES-0004 actually requires.

## Where the fields finally settled

Two more passes, both Edwin's, both about order rather than content:

> "Can you move this to the right now?" — then, seeing it: "the phase state does not look right now, can you move this to after the attention but make sure all the states align?"

The row now reads **`chevron · id · title · [flags] · progress · state`**, with the progress field right-aligned in its column and the state chip left-aligned in a fixed last column, so every chip on the page starts at the same x:

```
PHASE-0008  Feedback, Refresh & Energy      74/95 · 78% · 16 in flight · 20 attention   active
PHASE-0011  Nutrition: What Is Already…                                    0/10 · 0%   planned
```

The argument for the state going last is that **it is the row's verdict on everything before it**. Sitting between the title and the numbers, it split the sentence; at the end it closes it. And the numbers now end where the row ends, instead of stopping short so the usually-empty flags column could trail after them.

Two measurements the reorder forced:

- `--col-count` had been 148px since it held `74/95 · 78%` alone. It absorbed `in flight` and then `attention` without ever being resized, and only *looked* right because it overflowed left into a flags column that is empty in both corpora. Measured at its real worst case, 213px, and sized to 216px.
- The worst case has therefore never actually rendered, so it was synthesised: a long count plus `awaiting close-out` on one row leaves 48px clear between them, on one line.

The bug this pass produced is recorded under [[ISS-0100]] — it is a column-model defect, not a vocabulary one.
