---
type: "[[task]]"
id: TASK-0358
aliases: ["TASK-0358"]
title: "The board replaces the desk's empty state — occupied columns at width, empty kinds on one line"
status: backlog
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-09
source: ["[[DES-0010-The-Desk-Shows-What-It-Owes]]"]
parent: "[[FEAT-0082-The-Desk-Shows-What-It-Owes]]"
effort: M
due: ""
depends: ["[[TASK-0357-Obligation-Groups-And-Verbs-In-The-Payload]]"]
blocks: []
related: []
tests: []
---

# The board is the desk's landing

## Definition of Done
- [ ] `buildReviewEmpty` is replaced by a board built from `payload.groups`
- [ ] Only occupied kinds get a column; empty kinds render as one line (`nothing to decide · …`)
- [ ] A card carries id, type, state, full title, owning phase and age — every field the 240 px row hides in a tooltip
- [ ] Clicking a card opens the existing detail view, unchanged
- [ ] Columns cap at N cards with a `+ K more` disclosure, and the cap is logged in the note rather than silent
- [ ] The all-clear state says so in one sentence rather than rendering an empty grid

## Steps
- [ ] Build the board from `groups.filter(g => g.items.length)`, no count-conditional layout
- [ ] Reuse `.now-board` / `.now-col` (renderer.css:3291) rather than adding a second grid vocabulary
- [ ] Ids through `shortNoteId` with the full value on hover (ISS-0084)
- [ ] Empty-kind rail from the groups with zero items, so it stays honest without a second source

## Notes
No `count === 0` branch anywhere. The precedent is `buildNowBoard()`, gated behind `phases.length === 0` and consequently never seen in a repo that has phases — a layout that changes shape by count is a layout somebody will never encounter.

Occupied-columns-only is the decision that keeps this from being the status kanban that was rejected: five of six kinds are empty here, and drawing them all would reproduce exactly the "mostly empty board" failure.
