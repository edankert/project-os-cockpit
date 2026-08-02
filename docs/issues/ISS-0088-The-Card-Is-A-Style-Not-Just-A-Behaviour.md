---
type: "[[issue]]"
id: ISS-0088
aliases: ["ISS-0088"]
title: "The completed sections behave like the right pane's cards but do not look like them, and the group heads carry an icon, an uncoloured id and an inconsistent pill"
status: fixed
severity: medium
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["Edwin 2026-08-02, itemised: design view should match the overview; the overview's completed section should be a card like the right pane's; the phase-scoped record cards say 'Verification here'; phase heads should show a coloured id and name with no icon and consistent pills; a feature's expand affordance should be on its own row's line, without border rules; tasks and issues should read as cards"]
component: desktop-renderer
related: ["[[FEAT-0058-One-Shape-Per-Navigator]]", "[[ISS-0087-Nav-Group-Headers-Are-Twice-The-Height-They-Copy]]"]
fixed_by: ["[[TASK-0275-Settled-Groups-Are-Collapsed-Cards]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# The card is a style, not just a behaviour

## What

[[FEAT-0058]] gave the navigators the right pane's **behaviour** — settled groups shut, live groups open, a count in the head. It did not give them its **look**, so nothing reads as a card. Measured:

| complaint | measured |
|---|---|
| heads carry an icon | `icon: true` on every phase head |
| the id is not coloured | `idColoured: false` — the head's label is one string, `PHASE-999 · FUTURE / UNPHASED` |
| pills are inconsistent | PHASE-001 none, PHASE-002 one, PHASE-003 one, PHASE-004 none |
| `Completed · 1  1 ITEM` on the design view | `ROLLUP_NOUNS` has no `design` entry and falls back to `item` |
| `Verification here` | four record cards built with a literal `here` suffix |
| the feature expand is on the next line | `renderItemChildren` returns a `<details>` appended *after* the row |

**The pill inconsistency has a cause, which is worse than a bug.** [[TASK-0272]] suppresses a group's own status chip when the head summary already ends in it: PHASE-001's summary is `2 · done` and its status is `done`, so it is hidden; PHASE-002's is `2 · 2 done` (mixed items) so it is shown. The rule is defensible and the result looks arbitrary, which is the point — *a reader cannot see the rule, only the inconsistency.*

## Fix

- Heads render a type-coloured ID and a name, no icon — the row grammar, applied to the head.
- The phase's own status chip shows **always**. It is a different fact from its items' states and hiding it conditionally is what made it look random.
- The completed band, in the navigator **and** in the overview's scope pane, takes `.ctx-card`'s look.
- `here` goes from all four record-card titles.
- A feature's children get an inline expand affordance on the row itself, and the nested list loses its rules.
- `ROLLUP_NOUNS` gains the remaining modes.

## The review desk

Edwin: *"Review view I am not sure what to do."*

**Recommendation: leave it.** It is the one navigator whose left pane is not a list of notes but a list of *obligations*, and it already has the shape this phase was after — `Queue`, `Changes requested · 10`, `Tests · 23/23`, then `Completed · 2` last with a card per verdict.

The remaining difference is that its sections are headings rather than framed cards, and that is worth keeping: the desk's sections are **kinds of obligation**, not collections you open and close. A card invites collapsing, and there is nothing here you want collapsed — the queue being empty is the point of looking.

If it should change at all, the smallest honest version is to frame only `Completed`, which is the one section you would ever want shut. That is a one-line change and it is deliberately not made yet.

## Evidence it is fixed

A phase head, a task card, an issue card and a context card are the same object in four places.


## Measured after

| | |
|---|---|
| phase heads | no icon, type-coloured ID, a pill on every one |
| feature rows | expand affordance **on the row's line**, 47 of them, zero second-row summaries |
| nested lists | no rules down the side |
| nav groups | framed as cards — features 18, tasks 5, issues 7, design 2 |
| completed band | a heading over cards, not a card around cards |
| design view | `Completed · 1 · 1 design`, not `1 item` |
| record cards | `Verification`, `Decisions`, `In flight`, `Attention` |

The tasks navigator now reads exactly as asked: `Deferred` and `Unset` open, `Done · 268`, `Cancelled · 2` and `Superseded · 2` shut, one card each. Issues shows the open severities and risks above a divider, and `Critical`, `High` and the rest below it.
