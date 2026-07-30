---
type: "[[phase]]"
id: PHASE-019
aliases: ["PHASE-019"]
title: "Overview legibility — the page names what it is showing"
status: superseded
order: 19
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
goal: "Close the small 'I cannot tell what I am looking at' gaps on the project overview, so items are identifiable without hovering or inferring."
features: []
requirements: []
issues:
  - "[[ISS-0076-Phase-Rows-Do-Not-Show-Their-Phase-Id]]"
superseded_by: "[[PHASE-016-The-Overview-Answers-Questions]]"
depends: ["[[PHASE-018-History-You-Can-Reach-And-Traverse]]"]
related: ["[[FEAT-0040-Overview-Rework]]"]
tags: [overview]
---

# Overview legibility

## Goal

A standing home for the small legibility fixes on the overview, so each one does not need a phase of its own and none of them ends up parked in the sentinel — the two failure modes [[PHASE-015]] spent itself cleaning up.

## Scope

- **[[ISS-0076]]** — the Phases section shows a phase's title and never its ID.

## Out of Scope

- **Labelling the strip's squares or its feature groups.** Tried on the way to this and reverted at Edwin's word: it was the wrong surface. [[DES-0004]] spent the square's budget on state deliberately, and [[ISS-0068]] deleted a list for restating what the squares already draw.

## Exit Criteria

- [x] A phase's ID is readable on the overview without hovering — evidence: all 20 rows render `PHASE-NNN` beside the title, including the collapsed Completed group

## Notes

**Seventh phase opened on 2026-07-30.** More phase notes in one day than the preceding twelve weeks produced. Each was defensible alone; the aggregate is worth Edwin's attention, and this one is deliberately shaped as a *standing* phase that later small overview fixes can join rather than another single-issue phase.


## Closed 2026-07-30

[[ISS-0076]] fixed: the ID was already in `buildPhaseRow` as `p.key`, routing the title click, and simply never rendered.

**Two attempts, and the first one was reverted.** I read "the feature id is not visible on the project overview" as the phase strip's squares — built labels on the feature groups, and Edwin reverted it on sight. He meant the phase ID next to the phase title, which is a different surface and a much smaller change.

The cost of guessing was about twenty minutes and a clean `git checkout`, because none of it was committed. The cost of *asking* would have been one message. Worth remembering which of those is cheaper: I had the whole overview inventoried and could have shown him the four places a feature appears before writing anything.

## Superseded 2026-07-30 — merged into [[PHASE-016]]

This phase's work shipped and is unchanged; what changed is where it is recorded. [[PHASE-016]] absorbed it along with the other two legs of the same push, because their shared goal states without listing them: **every number on the overview leads somewhere, and everything on it says what it is.**

Four phases for one afternoon was the drift [[ISS-0077]] measured — nine phases opened in a day against nine in the preceding twelve weeks, at a fifth of the historical size. Each was minted reactively, one per request.

The note stays as the record of this leg. Its items now name PHASE-016, which is the phase that delivered them.
