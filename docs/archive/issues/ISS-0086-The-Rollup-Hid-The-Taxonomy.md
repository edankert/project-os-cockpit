---
type: "[[issue]]"
id: ISS-0086
aliases: ["ISS-0086"]
title: "The roll-up collapsed the phase list, the status vocabulary and the severity ladder into one line — structure, not noise, and the overview never made that mistake"
status: fixed
severity: medium
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["Edwin 2026-08-02: 'I don't really like the completed buckets and I also don't think the top level phases, task states, issue severities are shown, I like the review view and I like the way the right pane handles this. Also the overview view shows things differently to the other views, would probably also be good to re-align.'"]
component: desktop-renderer
related: ["[[TASK-0273-Finished-Groups-Roll-Up]]", "[[FEAT-0057-The-Record-Grammar]]"]
fixed_by: ["[[TASK-0273-Finished-Groups-Roll-Up]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# The roll-up hid the taxonomy

## What

[[TASK-0273]] put every finished group behind one expandable line. Measured now, the features navigator's entire top level is:

```
PHASE-999 · FUTURE / UNPHASED    1 · BACKLOG   planned
17 FINISHED PHASES · 56 FEATURES
```

Two rows. **Which phases exist is no longer on the page.** The same applies to the tasks navigator (the status vocabulary) and the issues navigator (the severity ladder).

## Why that is wrong, and why the right pane is not

A group *head* and a group *body* carry different things:

- the **body** is a list of items you might open — at 99% completion, mostly work nobody is doing
- the **head** is a name in a taxonomy — `PHASE-007 · Agent instrumentation`, `Done`, `Critical`

Collapsing bodies is what the right pane does, and it is right: a closed `TASKS · 5 · done` card still names the relationship. Collapsing *heads* removes the taxonomy itself, and 22 phase names is not a wall to scroll past — it is the shape of the project.

**The distinction I got wrong: quantity lives in the bodies, structure lives in the heads.** I applied one rule to both.

## The overview already had this right

Its scope pane, unchanged since [[FEAT-0043]]:

```
IN FLIGHT
   Future / Unphased          0%
COMPLETED · 22
   MVP                        ✓ 8
   Project-os adapter         ✓ 49
   …
```

Every phase named, 24px a row, the finished ones under a **heading** rather than behind a door. That is the same "quiet, never absent" rule this phase exists for — and it predates the phase.

The review desk agrees: full rows with `ctx-disclosure` heads reading `70 older`, and the register visible above them.

## Fix

Replace the roll-up with a **section heading**: `COMPLETED · 17`, and below it every finished group as its own one-line closed head. Nothing is hidden that was not hidden before; the door becomes a label.

Align the counts with the overview's while there: it says `✓ 8`, the navigator says `8 · done`.

## Also found

The review desk renders `CHG-20260802-Completed-Work-Collapses` in full — [[ISS-0084]]'s shortening reached the nav rows and the context pane but not the desk's `queue-row`. The same "one renderer of N" shape as [[ISS-0085]], for the third time.

## Evidence it is fixed

Every phase, every task status and every issue severity is named in its navigator without expanding anything.


## Also corrected, same pass

Edwin, on the overview being the model: *"the overview section is not perfect, it does not show the ids and it seems to do cut down some characters while there is lots of space."*

Both true, and both measured:

- **No IDs.** 24 phase rows reading `MVP`, `Downstream pilot` — the one surface in the cockpit that never named its notes. It now carries `PHASE-001` in the same `nav-id mono ov-typed` grammar as every other row, which brings the type colour and the [[ISS-0084]] shortening with it.
- **Truncation with room to spare.** `.scope-name { flex: none; max-width: 55% }` capped every name at **224px in a 424px row** — a cap that exists to leave room for the progress bar, applied also to completed rows that carry no bar. 13 of 24 rows truncated with ~200px unused. The name now takes the slack and the bar has a fixed 64px; name width 224 → **312px**, truncation 13 → 10, and the remaining ten are titles genuinely longer than the pane.

So the alignment ran both ways: the navigator took the overview's `Completed · N` band, and the overview took the navigator's ID column.
