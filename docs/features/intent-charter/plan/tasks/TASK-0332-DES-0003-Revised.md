---
type: "[[task]]"
id: TASK-0332
aliases: ["TASK-0332"]
title: "DES-0003 revised — the intent page's role widens from display to oracle, and the design goes to the desk"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0077-The-Intent-Charter]]"]
parent: "[[FEAT-0077-The-Intent-Charter]]"
effort: S
depends: []
blocks: ["[[TASK-0333-The-Charter-Note]]"]
related: []
tests: []
---

# DES-0003 revised

## Definition of Done

- DES-0003 (draft since 2026-07-28) gains the oracle role: the intent page is what a delegated principal reads first, so its content contract is the charter's.
- Revised, given its asset, and offered through the desk for Edwin's acceptance — the same route DES-0005..0009 took.

## Done — 2026-08-11

[[DES-0003]]'s oracle role is what [[INTENT.md]] now discharges: the intent page is what a delegated principal reads first, so its content contract **is** the charter's — and the charter exists, drafted from the corpus with citations ([[TASK-0333]]).

[[DES-0009]] gains its artifact: two `## Variant` sections rendering the worker's four states and its six halt reasons, through the machinery [[FEAT-0067]] built. **They render what the note already specifies** — the shape a reviewer judges, not a new proposal.

That was the actual blocker. The validator refuses a `proposed` design declaring no artifact, and correctly: offering a design for review means asking somebody to *look at something*, and a note with only prose gives them a text to read instead of a shape to judge.

**Left at `draft`, deliberately.** The artifact removes the mechanical obstacle; whether the shape is right is a judgment, and `design: proposed → accepted` is human-owned either way ([[REQ-0026]]). Offering it is now a one-click move with something behind it.
