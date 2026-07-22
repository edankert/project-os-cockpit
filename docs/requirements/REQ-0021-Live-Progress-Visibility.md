---
type: "[[requirement]]"
id: REQ-0021
aliases: ["REQ-0021"]
title: "Live progress visibility at the console — session work items shown as the coloured block notation, filling in as the agent completes them"
status: implemented
owner: user:edwin
created: 2026-07-22
updated: 2026-07-22
source: ["user-request"]
features: ["[[FEAT-0038]]"]
related: ["[[FEAT-0036]]", "[[FEAT-0023]]"]
---

# REQ-0021 — live progress visibility at the console

## Requirement

While an agent session runs, the collapsed console surface (the bar above the terminal that already shows agent state, ctx % and $) MUST show the session's documented work items — requirements, issues, changes, tasks, features — using the same coloured block notation as the overview (`.ov-phase-sq`: type-coloured border, square fills when the item reaches a done-equivalent status), and the blocks MUST fill in live as the agent completes items, without the user expanding anything.

## Rationale

User statement 2026-07-22: "I am actually on the overview page looking for these blocks to be filled in by the LLM as it completes the prompt. I think it could be nice to have this clearly shown in the collapsed bar above the console." The block notation has become the project's primary at-a-glance progress language; surfacing it at the console removes the need to sit on the overview page to watch delivery.

## Acceptance criteria

- With the console strip visible and a session that has edited at least one documented item for the current prompt, the in-flight boxes are visible inline in the strip (before ctx) without expanding anything.
- Blocks use the overview notation: type colour by note kind, outline = open, filled = done-equivalent; the item currently being worked on is visually distinguished (pulse/highlight).
- A status transition to a done-equivalent status fills the corresponding block within one SSE round-trip (no manual refresh).
- Blocks are clickable (navigate to the note) and hoverable (id, title, current status).
- The boxes show only the current prompt's in-flight items — never the whole session's or project's backlog — and never hide the state/ctx/$ information.

## Design decision (2026-07-22, revised same day)

Initially the user chose a second thin rail under the strip; after seeing the first delivery ([[ISS-0018]]) the design was revised: the boxes render **inline in the main strip line, before the ctx meter**, and are scoped to the items in flight **for the current prompt** (not the whole session), with server-enriched title/status/done per item. Delivered by [[FEAT-0038]] (TASK-0191/0192).
