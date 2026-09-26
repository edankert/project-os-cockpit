---
type: "[[task]]"
id: TASK-0320
aliases: ["TASK-0320"]
title: "The desk's headings and the Library's file rows, written into the design system"
status: done
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0073-One-Voice]]"]
parent: "[[FEAT-0073-One-Voice]]"
effort: S
depends: []
blocks: []
related: []
tests: []
---

# The desk's headings and the Library's file rows, written into the design system

## Definition of Done

- DES-0002 gains the deliberate-exceptions section (obligations-not-collections; files-not-lifecycle-notes) so the next session inherits reasoning, not just appearance.

## Done — 2026-08-11

[[DES-0002]]'s new `Deliberate exceptions` section carries both, with the reasoning rather than the appearance:

- **The desk's headings are obligations, not collections.** The registers are headed by what is owed (`Decisions`, `Proposals`, `Questions`, `Test runs`) while every navigator groups by type or phase. A queue's reader asks *"what is waiting on me"*; grouping by type answers *"what kinds of note exist"*, which they did not ask. [[ADR-0020]] later generalised this.
- **The Library's rows are files, not lifecycle notes.** No status chip, no type colour, no ID — because the Library is a file browser over `docs/` and most of what it lists has no project-os identity ([[TASK-0036]] emits reference rows with `id: ""` by design). Giving them the lifecycle grammar would assert a lifecycle they do not have.

The second one also records the boundary [[ISS-0125]] and [[FEAT-0091]] kept: a standing document appears in the Library as a file *and* on Intent with its freshness. One item, two addresses, deliberately — and not [[ISS-0068]]'s two-lists failure, because the Library lists files rather than obligations.

The section exists so a later pass reads these as decisions rather than as inconsistencies to tidy away.
