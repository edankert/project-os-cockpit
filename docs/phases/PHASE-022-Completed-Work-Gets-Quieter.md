---
type: "[[phase]]"
id: PHASE-022
aliases: ["PHASE-022"]
title: "Completed work gets quieter, never absent — ordering first, folding second, and never in the context pane"
status: done
order: 22
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
goal: "Replace a switch that empties three views and the whole context pane with ordering that puts open work first, and folding applied to volume rather than to meaning."
features:
  - "[[FEAT-0056-Completed-Work-Ordering]]"
requirements: []
issues:
  - "[[ISS-0082-Phantom-Phase-Group-From-The-016-Merge]]"
depends: ["[[PHASE-021-Git-Is-Not-The-Users-Job]]"]
related: ["[[DES-0004-Attention-In-The-Squares]]", "[[PHASE-010-Surface-Ownership]]"]
tags: [ia, overview]
---

# Completed work gets quieter

## Where this came from

Edwin, 2026-08-02: *"In some cases completed items are still important to be visible but in other cases these are really not very interesting… we should instead hide/collapse these completed items… instead of not making them visible at all using the hard visible or not switch."*

## The measurement

**99% of this corpus's lifecycle notes are terminal** — 528 of 531 on 2026-08-02: tasks 99%, features 98%, and issues, changes and requirements all at 100%. Across every note type including phases, ADRs and designs it is 90% (600 of 665, excluding templates). Any design that treats "done" as a thing to remove is designing against nearly all of it.

(An earlier draft said "91%", which was neither figure. The per-type numbers were right and the aggregate was invented — corrected at review.)

What `Hide completed` actually does:

| view | ON |
|---|---|
| Features | **1 of 18 groups survives** |
| Issues | **0 of the 4 severity buckets survive** — only the 3 risk buckets, and risks are not issues |
| Tasks | **5 item rows of 270**, in 2 of 5 groups |
| **Right pane, FEAT-0051** | **entirely empty** |
| **Right pane, ISS-0080** | **entirely empty** |

It is not a filter. In three views and most of the context pane it is a demolition, and since almost every lifecycle note is complete, the emptied state is the normal one.

## What Edwin corrected, and it mattered

My first review said the **tasks** view needed folding most. Wrong: tasks group *by status* with completed statuses last, so their ordering is already correct. What I saw was 270 rows — 261 of them in one bucket — and I called a **volume** problem an **ordering** problem.

The two need different fixes, and separating them is what makes this phase small: **ordering is wrong in features and issues; volume is high in tasks; the context pane needs neither.**

## The model

Each view groups on a different axis — status, severity, phase — and **state is orthogonal to all three**. No grouping axis can carry it, which is exactly why a global switch got invented: it sidesteps ordering instead of solving it.

| pane | what state does | what length does |
|---|---|---|
| **Left** — a selection list | orders groups *and* items; the done tail folds | — |
| **Right** — a description | orders items only | folds long groups, regardless of state |

**Fold on volume, never on meaning.** A done task under a feature is what the feature is made of; a done task in a list of 261 is something you are scrolling past. Same status, different job.

## Scope

- **[[ISS-0082]]** — the phantom `PHASE-016` group, from my own merge.
- **[[FEAT-0056]]** — the comparator, the left-pane ordering, the right-pane rule, and the fold.

## Out of Scope

- **Changing what counts as complete.** `statuses.COMPLETED_STATUSES` is the vocabulary and stays.
- **The phase strip and History.** Both already encode done rather than hiding it ([[DES-0004]]); nothing to do.

## Exit Criteria

- [x] No group without open work sorts above a group with it — evidence: `test_the_phase_in_flight_leads_the_features_navigator` (groups band in-flight / upcoming / finished). **The evidence first written here was "PHASE-022 moved from 17th of 18 to 1st" — measured mid-flight, and false by close-out, because closing the phase settled it. An assertion that only holds while the work is open is not an assertion.**
- [x] No completed item sorts above an open one in the same group — evidence: `test_a_done_feature_with_a_lower_id_still_sorts_below_an_open_one`, on a corpus built so ID order and open-first order disagree. (The first version cited ISS-0082 leading the Medium bucket; ISS-0082 is now `fixed` and sorts to the back, so that expired on close-out too.)
- [x] The context pane never empties — evidence: FEAT-0051 0 → 9 rows, ISS-0080 0 → 5, measured against the live sidecar
- [x] Folding is keyed on length, never on state — evidence: `folding is keyed on length, not on status` (50 open items fold at 8)
- [x] The switch cannot empty a view — evidence: 0 groups lost across tasks/features/issues with it on; `head + hidden` accounts for every item

## Notes

**The switch was a reasonable answer to a real problem** — at 99% done an unfiltered list is unusable, and hiding is the cheapest thing that works. What it could not do is distinguish the two reasons a done item might be in front of you. That distinction is the whole phase.


## Closed 2026-08-02

Built in the order the plan set: the phantom first, then ordering, then the context pane, then the fold. Then reworked substantially after independent review returned `changes-requested` — see [[FEAT-0056]] for the ten findings and what each cost.

**Measured 2026-08-02 on the closed corpus, switch on.** A *row* is one item row, plus the group's `… N more` row where it has one.

| view | groups | items | before: groups / rows | after: groups / rows |
|---|---|---|---|---|
| Tasks | 5 | 270 | 2 / 5 | **5 / 8** |
| Features | 18 | 56 | 1 / 1 | **18 / 18** |
| Issues | 7 (4 issue + 3 risk) | 86 | 3 / 4 | **7 / 8** |
| Context — FEAT-0051 | 4 | 9 | 0 / **0** | 4 / **9** |
| Context — ISS-0080 | 4 | 5 | 0 / **0** | 4 / **5** |

Every group survives in every view; the two context panes that rendered nothing now render everything they have.

**What the review changed, beyond the numbers.**

*The right pane's length fold did not exist.* Both this note and [[FEAT-0056]] described one; the code did not have it, and the stated reason — "the largest group anywhere is 11 items" — was 11 measured on **one note**. Swept across the corpus, 11 of 3192 context groups exceed the limit and PHASE-007 renders a 79-item backlinks group. The wall was real. The fold is now built on both surfaces.

*A two-band sort put the backlog pen permanently on top.* `PHASE-999 · Future / Unphased` is permanently `planned`, so under settled/unsettled it outranked the phase being worked — forever. And closing a phase settles it, so the phase you just finished sank and the pen took the top. Three bands (in flight / upcoming / finished), ranked on the phase note's **authored status**, fix both.

*Five guards guarded nothing.* Mutation testing found that deleting the open-first sort from `_features_groups`, deleting `_settled_last` from the issue buckets, and re-introducing ISS-0082 itself all left the suite green — and mode 1's hand-written twin had no guard at all. The corpus could not catch the first two (its feature IDs already run open-first, and it has zero open issues), so those now run against a fixture corpus built so ID order and open-first order **disagree**. Mode 1's helpers are executed through node and checked against mode 3's. Ten mutations were tried against the rebuilt suite; all ten fail.

*A settled group used to keep one row.* Seeing `PHASE-007 · 19 → 1 shown + 18 more` against the real corpus killed it: the row shown is the first by ID and presenting it reads as though it were the notable one. A settled group now cuts to **zero** rows and a count. `Done · … 261 more` is the honest rendering; the header keeps the group visible.

**Both surfaces.** Mode 1 (`static/cockpit.js`) got the same treatment *and* the same guards, rather than the treatment alone.

**Not done:** whether 12 is the right threshold is still one corpus's answer. It folds the four groups that are unreadable here and leaves twenty-six whole; nothing makes it configurable.
