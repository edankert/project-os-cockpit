---
type: "[[phase]]"
id: PHASE-022
aliases: ["PHASE-022"]
title: "Completed work gets quieter, never absent — ordering, then folding, then the density that makes folding readable"
status: done
order: 22
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
goal: "Replace a switch that empties three views and the whole context pane with ordering that puts open work first, and folding applied to volume rather than to meaning."
features:
  - "[[FEAT-0056-Completed-Work-Ordering]]"
  - "[[FEAT-0057-The-Record-Grammar]]"
  - "[[FEAT-0058-One-Shape-Per-Navigator]]"
requirements: []
issues:
  - "[[ISS-0082-Phantom-Phase-Group-From-The-016-Merge]]"
  - "[[ISS-0085-One-Line-Grammar-Reached-One-Of-Four-Renderers]]"
  - "[[ISS-0086-The-Rollup-Hid-The-Taxonomy]]"
  - "[[ISS-0087-Nav-Group-Headers-Are-Twice-The-Height-They-Copy]]"
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
- [x] A finished group costs one line, not a header and a fold row — evidence: the features navigator went 1440px → **286px**, sixteen finished phases behind `16 finished phases · 54 features`
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


## Reopened 2026-08-02 — [[FEAT-0057]]

Edwin, on the shipped result: *"it still shows too many done items and too much info, not concise enough… I kinda like the very minimalist new way to present the ADR, TSTs etc FEAT, ISS etc as they are shown in the project overview context."*

[[FEAT-0056]] fixed **what** was shown. It did not touch **how densely**, and at this density the fix is hard to see: measured in the running app, a nav row is **60px** against the record column's **27px** for identical text, and a nav group header is **53px** against a record card head's **15px**. The features view renders eighteen 53px headers whether or not anything in them is live — so after all that folding, the headers *became* the noise.

That is a density problem, not an ordering one, and it is why the phase reopened rather than a new one being minted: the goal sentence is unchanged.

Standing-phase behaviour, working as documented in CLAUDE.md — set back to `active`, take the work, close it again.


## Closed again 2026-08-02 — [[FEAT-0057]]

Measured in the running app, this repo's workspace:

| | before | after |
|---|---|---|
| nav row | 60px | **27px** |
| group header | 53px | 29–42px, one line, ellipsised |
| features navigator | ~1440px | **286px** — 2 live groups + one roll-up line |
| tasks navigator | — | **490px** |
| context pane, FEAT-0051 | 9 rows always open | **4 closed cards**: `TASKS 5 · done` … |

**Two bugs found on the way, both pre-existing and both filed:**

- **[[ISS-0083]]** — `refreshActiveNavRow` selected `li.nav-item` while `navItem` puts that class on the div inside the `li`. It matched nothing, so the navigator has never highlighted the open note. Measured at `f5e6637`: 112 rows, `is-active` on zero. It surfaced because [[TASK-0273]] needs the active row in order to open the group holding it — a decorative no-op became a functional one.
- **[[ISS-0084]]** — Edwin, looking at the new rows: *"Why are the change notes shown with the full file name?"* A change note's `id:` **is** its description (`CHG-YYYYMMDD-Short-Description`, LIFECYCLE.md line 95), so a row printed the description twice at five times the width of every other ID. Invisible while the ID had its own line; expensive the moment [[TASK-0271]] put ID and title on one. **A layout change made an existing inconsistency costly** — the scheme was not wrong before and is not wrong now, it just stopped being free.

**What did not change:** [[TASK-0269]]'s rule. `contextGroupRows` still takes no collapse parameter, and its guards pass untouched — a closed card still names the type and its count, where the old filter rendered nothing at all. That distinction is the reason a disclosure default is allowed where a filter was not.


## Closed a third time 2026-08-02 — [[ISS-0085]]

Edwin: *"in the left pane, I still see for features and issues and possibly others that there are multiple lines… Also for some types (risks, requirements, designs and plans under features), they still use the more complex format."*

Both correct, and both my omission. The left pane has **four** row renderers and `pickItemRenderer` chooses between them per group; [[TASK-0271]] rewrote one. Risks and designs (`stacked`) and requirements and plans (`nested`) kept the old two-line card at up to 90px, and the one renderer I did fix still printed `item.subtitle` — which the server sends for every feature (`goal`), design and risk.

Measured before: `nav-item-line` up to 66px with 50 subtitles, `nav-item-nested` 103 rows, `nav-item-stacked` up to 90px. After: **every card 24–27px, one class, zero subtitles**, and the features navigator content at 97px.

**Why the guard did not catch it.** I wrote the task against `navItem`, checked `navItem`, and wrote the guard against `navItem`. `pickItemRenderer` is three lines away and I never followed it.

> A guard written from the same reading as the change confirms the reading, not the behaviour.

The replacement asserts over **every renderer the picker can return**, and fails if a fifth appears without going through the shared builder.

**And the guard itself was vacuous on first writing** — its body regex closed on `\n}` at column 0, but `cockpit.js` is one IIFE whose functions close at `\n  }`, so the "body" ran past the end and swallowed the helper it was looking for. Mode 1's mutation passed. Caught by mutation testing, not by reading. That is now three times in this phase that a guard needed to be *run against a break* before it could be believed.


## Closed a fourth time 2026-08-02 — [[ISS-0086]]

The roll-up [[TASK-0273]] built was the wrong shape, and Edwin named the reason: *"I don't think the top level phases, task states, issue severities are shown."* They were not — the features navigator's entire top level had become two rows.

**The distinction I had missed: quantity lives in a group's body, structure lives in its head.** Collapsing bodies is right; collapsing heads deletes the taxonomy. A phase list is not a backlog.

The overview's scope pane has had this right since [[FEAT-0043]] — `Completed · 22` as a *heading*, with every phase still named beneath it. The navigator now uses that band, that wording, and that default (open, persisted per mode). Both panes now say `Completed · N` for the same idea.

And the alignment ran in both directions: the overview gained the ID column it never had, and lost a `max-width: 55%` that was truncating 13 of 24 rows with 200px of the pane unused.

**Four reopenings in one day** is worth recording as a smell, not a success. Each was a real correction — but three of the four were things a careful look at the running app would have caught before Edwin did, and the fourth ([[ISS-0083]]) had been broken for months. The standing-phase mechanism worked exactly as CLAUDE.md describes; what it could not do is make me check the surface I had just changed.


## Closed a fifth time 2026-08-02 — [[ISS-0087]]

Edwin: *"I still like the way things are presented… in the right pane a lot and this could be a nice way to present the stuff on the left as well. If anything it should at least use more of the minimum look of the overview pane."*

[[FEAT-0057]] had matched the two panes' **type** — 11px, 600, uppercase, `--text-faint`, identical on both — and stopped there. Density is set by the box: 42px against 22px, nineteen headers over, plus a background and a bottom border the right pane's heads do not carry. Now 25px against 22px.

**Five corrections, one cause.** [[ISS-0085]] checked one renderer of four. [[ISS-0086]] collapsed heads as if they were bodies. [[ISS-0087]] matched fonts and called it a grammar. Each time I verified the thing I changed instead of the surface it lives on, and each time Edwin found it by looking at the app.

The cheap fix is not a rule but a habit: **render the thing beside the thing it is copying and measure both**, which is what every one of these investigations did in its first two minutes once someone asked.


## Closed a sixth time 2026-08-02 — [[FEAT-0058]]

Edwin specified all four navigators. The three he described view-by-view turned out to be one rule:

**A completed divider is needed only where a group's own name does not already say it is finished.**

| view | before | after |
|---|---|---|
| **Tasks** | one `Completed · 3` band | **no divider** — `Done · 265`, `Cancelled · 2`, `Superseded · 2` shut in place; 367px |
| **Issues** | band with severity heads | divider + a shut card per severity; risks live above; 297px |
| **Features** | band of phase heads | divider + 16 phases, each opening to features and on to requirements and plans; 654px |
| **Review** | flat list of 82 with `70 older` | `Changes requested · 10` live, `Completed · 2` last with `approved · 70` and `accepted · 2` |

**The review desk was not missing a completed section — `Reviewed · 82` already was one.** What the data showed is that **10 of those 82 were `changes-requested`**: a reviewer asked for work and nothing recorded it happening. That is a terminal-looking label on an open obligation, which is the precise error this whole phase exists to have removed — and it was still live on the one surface whose job is to track obligations.

Six closings in a day. The first five were corrections to work I had just shipped; this one was a specification Edwin wrote out in full, and it is the only one that produced a rule rather than a fix.
