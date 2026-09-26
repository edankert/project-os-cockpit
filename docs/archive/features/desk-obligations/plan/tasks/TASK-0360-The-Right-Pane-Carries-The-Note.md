---
type: "[[task]]"
id: TASK-0360
aliases: ["TASK-0360"]
title: "The desk's right pane carries the selected note's context instead of being cleared on entry"
status: superseded
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-10
source: ["[[DES-0010-The-Desk-Shows-What-It-Owes]]"]
parent: "[[FEAT-0082-The-Desk-Shows-What-It-Owes]]"
effort: S
due: ""
depends: ["[[TASK-0358-The-Board-Is-The-Desks-Landing]]"]
blocks: []
related: []
tests: []
---

# The right pane carries the note

## Definition of Done
- [ ] With an item selected, the right pane shows that note's context — what it specifies, its source, its owning phase — using the existing context payload
- [ ] With nothing selected the pane is empty, and that is deliberate rather than incidental
- [ ] No new endpoint: the desk uses `/api/cockpit/context` as every other note view does

## Steps
- [ ] Remove the unconditional `rightPaneContent.replaceChildren()` at `renderReviewPage` entry; clear only when landing on the board
- [ ] Fetch context for the selected note id and render with the existing right-pane group renderer
- [ ] Check the question and orphaned-request views, which have no note behind them and must keep an empty pane

## Notes
The clear-on-entry is `renderer.ts:4105`. It made sense when the desk had no selected note to describe; with a detail view open it means the desk is the one place a note is read without its relationships.

Reviewing a requirement without seeing which features it specifies is the concrete cost — that is the context the judgment needs.


## Superseded 2026-08-10 — [[ADR-0020]]

Its point survives structurally: judging happens on the note, where the context already is.
