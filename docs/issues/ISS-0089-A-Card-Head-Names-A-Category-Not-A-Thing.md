---
type: "[[issue]]"
id: ISS-0089
aliases: ["ISS-0089"]
title: "Copying the context card's head styling made phase names render as labels — a card head names a category, a phase head names a thing, and only one of those can be faint"
status: fixed
severity: medium
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["Edwin 2026-08-03: 'why do we have individual cards for each phase and why is the phase id and title not more visible and the pils are also not visible… The task section cards, why do we need the pills, the card names already capture this… the issues page, I would like to have 2 sets of cards… Overview section: the Completed card should include the completed phases… The design section, why do we need this design system section, why not just have these designs under completed?'"]
component: desktop-renderer
related: ["[[ISS-0088-The-Card-Is-A-Style-Not-Just-A-Behaviour]]", "[[FEAT-0058-One-Shape-Per-Navigator]]"]
fixed_by: ["[[TASK-0275-Settled-Groups-Are-Collapsed-Cards]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# A card head names a category, not a thing

## The mistake, stated once

Measured side by side, the two heads are nearly identical — 11px, weight 600, uppercase, `rgb(128,128,128)`:

| | height | font | colour |
|---|---|---|---|
| right `ctx-card-head` | 22px | 11px / 600 / uppercase | `--text-faint` |
| left `nav-group-header` | 25px | 11px / 600 / uppercase | `--text-faint` |

That match was the goal for four rounds. It is wrong, and this is why:

> **The right pane's head names a CATEGORY. The left pane's head names a THING.**

`TASKS` is scaffolding — you read past it to the rows beneath, so faint, small and uppercase is exactly right. `PHASE-007 · Agent instrumentation` **is the content**. Rendering it in the treatment reserved for labels hides the thing you opened the pane to find.

The same distinction explains the frames: four boxes around four categories reads as structure; **eighteen boxes around eighteen things reads as clutter.**

## The five symptoms

1. **Phase heads are faint** — the name and ID are label-styled, and the pill at `rgb(153,162,178)` on transparent is barely there.
2. **Every phase is individually framed** — 18 boxes.
3. **Task pills are redundant** — the card is called `Done` and carries a `done` pill. [[ISS-0088]] made the pill unconditional to fix an inconsistency, and re-created a redundancy the summary rule had been avoiding. **The right answer was never "always" or "never" — it is "when the name does not already say it"**, which is the `groupNamesStateThemselves` rule already in the file, applied to one thing and not the other.
4. **The overview's completed card frames only its heading** — `bodyInsideBand: false`; the 22 phase rows are a sibling outside the card.
5. **The design view has a `Design system` group** for one note, splitting three designs across two sections for a `role:` field the reader did not ask about.

## Fix

- A group head whose label is a **thing** renders at row weight and colour, with its type-coloured ID; only the count and status stay quiet. A head whose label is a **category** keeps the label treatment.
- Frames follow the same split: categories are framed, things are not.
- The pill obeys `groupNamesStateThemselves` — shown for phases and severities, hidden for statuses.
- The overview's band contains its rows.
- The design view drops the `system`/`proposal` split.
- The issues view gets two explicit sets, each headed.

## Evidence it is fixed

A phase name reads as a name, `Done` carries no `done` pill, and the overview's completed rows are inside the card that counts them.


## Measured after

| | before | after |
|---|---|---|
| phase head | 11px / 600 / uppercase / `--text-faint` | **12.5px / 500 / sentence case / `--text`** |
| phase frames | 18 boxes | none — one hairline between rows |
| phase pill | present but `rgb(153,162,178)` | present and legible |
| task pills | 5 | **0** — the card is called `Done` |
| issues sets | one unnamed block, one named | **`Open · 4`** and **`Completed · 3`** |
| overview card | framed the heading, 22 rows outside it | **contains all 22** |
| design groups | `Designs`, `Design system` | **one list** |

## What generalises

Two answers were wrong before this one, and the shape of the error is the same both times: I reached for **"always"** or **"never"** where the right answer was **"when the name already says it"**.

That question — *is this label already the thing I am about to print?* — now drives three separate decisions: whether a view gets a completed divider, whether a head repeats its status in the summary, and whether a group carries a pill. One rule, three uses, and each of them looked like a special case until the rule was named.
