---
type: "[[task]]"
id: TASK-0595
aliases: ["TASK-0595"]
title: "Landing opens the note in the reader that already exists, so the field never becomes a second document pane"
status: backlog
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-09-05
updated: 2026-09-05
source: ["[[FEAT-0144-The-Corpus-Has-An-Inside]]"]
parent: "FEAT-0144"
effort: ""
due: ""
depends: ["TASK-0594"]
blocks: []
related: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]"]
tests: []
---

# Landing opens the note

## Objective

Double-clicking a node opens that note in the cockpit's document pane. Any note can send you the other way — "show this in the field" — with the camera flying to it rather than cutting.

## Detail

The temptation is a panel inside the field showing a summary of the note. That panel becomes a second, worse renderer, and this project has a rule about second parsers ([[ISS-0151]]) for exactly this reason.

**No verb is discharged in the field.** What is owed on a note appears where the note is ([[ADR-0020]]). The field may show *that* something is owed — a halo, a mark — and landing is how you act on it.

## Acceptance

- Landing routes through the existing navigation, so back/forward, tabs and pins all work unchanged
- A note offers "show this in the field" and the camera flies rather than cuts, so the reader keeps their bearings
- No note content is rendered inside the field beyond id, title, status and the edge sentence
