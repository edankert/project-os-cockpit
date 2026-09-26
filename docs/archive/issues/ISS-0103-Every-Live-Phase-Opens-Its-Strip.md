---
type: "[[issue]]"
id: ISS-0103
aliases: ["ISS-0103"]
title: "Every live phase expands its item strip on first paint, so a page whose rows already say `planned · 0/11 · 0%` repeats that answer as 300 squares"
status: fixed
severity: low
phase: "[[PHASE-016-The-Overview-Answers-Questions]]"
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["Edwin 2026-08-06: 'On the project overview page, can we collapse by default any phases which are not active or which do not have any in-flight items?'"]
component: desktop-renderer
related: ["[[FEAT-0056-Completed-Work-Ordering]]", "[[ISS-0023-Implemented-Status-Band-Drift]]", "[[ISS-0101-Four-State-Fields-One-Counted-Twice]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# Every live phase opened its strip

## Measured, on first paint

```
                      phases open   squares painted   phase section height
project-os-cockpit    7 of 7        99                655px
your-health           6 of 6        303               580px
```

The default was `!complete` — open unless the phase is finished. So five of your-health's six open strips belonged to phases whose own row already read `planned · 0/11 · 0%`, and one to `planned · 2/22 · 9%`. **The row had answered the question and the strip repeated it at forty times the height.**

## The rule

A phase opens on first paint only when **both** hold: its status says someone is in it (`active` or `doing`), **and** something under it is in flight.

Both, never either — the two failure modes are different and neither earns a hundred squares:

- **`planned` with work in flight** is work that started ahead of its phase. Real, worth knowing, and the row already says `10 in flight`.
- **`active` with nothing in flight** is a phase nobody is currently in. Also real, also on the row.

After:

```
                      phases open   squares painted   phase section height
project-os-cockpit    1 of 7        7                 487px
your-health           1 of 6        142               440px
```

## Why this is a default and not a filter

Every row is still there, still carries its id, title, progress, attention count and state, and still opens with one click. That distinction is the entire subject of [[FEAT-0056]]: the Hide-completed switch emptied three views because it **removed** rows, and the answer was to fold and count while leaving every row addressable. This is the same answer applied to a strip instead of a list.

The stored per-phase open state still wins over the default, so an SSE re-render never re-collapses something the reader opened.

## Two things the fix had to avoid

**A second definition of in-flight.** The rule is fed `countInFlight(p)` — the same function that prints `16 in flight` on the row — so the number you can see is the number that decides. `p.tasks.in_progress` was available and would have been a second definition; [[ISS-0023]] is what that costs at scale (one vocabulary in eight places, drifted in three).

**A second definition of "active phase".** `sortLivePhases` already had a table saying `active` and `doing` rank first. Writing the open-rule against its own copy would have been the beginning of the same drift, in the same file, on the same day it was cited. Both now ask `phaseIsActiveStatus`, and a guard fails if `PHASE_LIVE_RANK` names either word again.

## Where the rule lives

In `completed-work.ts`, not in the DOM function that uses it — the reason that module exists, stated in its header: *a decision inside a DOM function can only be guarded by grepping the built bundle, and that guard survives the mutation that breaks it.* As a pure predicate it is tested as a truth table (nine rows, plus unknown statuses and `NaN`/negative counts), and the **wiring** is what the source guard checks.

Mutation-checked, eleven ways, across both suites: AND→OR, either condition dropped, completed opening again, `> 0` weakened to truthiness, case-folding dropped, `planned` added to the active set, the wiring reverted to `!complete`, fed `tasks.in_progress`, the stored state no longer winning, and the second status table returning. All eleven caught.

## Not fixed here

A collapsed row is **66px**, of which the content is 23px — a 20px head and a 3px progress bar. The remaining 43px is the row's card padding, and it is why closing five strips only took the section from 580px to 440px. Worth a look, but it is the row's box model rather than this default.

Related, and found while measuring it: `.ov-phase` has **two** rule blocks 380 lines apart, one supplying `display: block` and padding and border, the other `display: flex` and gap and margin. The second wins for the properties they share. Same first-match trap [[ISS-0100]] removed for `.scoped-feat`; the block-count guard covers only two selectors.
