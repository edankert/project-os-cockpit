---
type: "[[task]]"
id: TASK-0318
aliases: ["TASK-0318"]
title: "One sentence pattern for every empty state"
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

# One sentence pattern for every empty state

## Definition of Done

- Every empty state says what the pane shows and the shortest path to having some; one voice, guarded by a sweep test over the literals.

## Done — 2026-08-11

**The pattern**: say what the pane shows, then the shortest path to having some — both halves, one sentence. The design register already did it (*"No design notes yet. A design is a note with type: [[design]]."*) and nothing had copied it.

Nine rewritten. The three that said nothing at all:

| was | now |
|---|---|
| `(no items)` | No features or issues in this phase yet — add one with a `phase:` naming it. |
| `(no children)` | Nothing names this phase yet — a note joins it by setting `phase:`. |
| `All clear.` | Nothing is waiting on you — proposals, questions and manual test runs appear here. |

Plus six that named the absence without the path: committed revisions, documented work, files touched, workspaces discovered, acceptance tests in scope, and nothing-in-flight.

**Guarded by a sweep, not by a helper.** There is no shared empty-state constructor to hang a rule on — each pane builds its own element — so the test reads the literals out of `renderer.ts` and requires both halves. A pane written next week is covered without anyone remembering this task. It also asserts the sweep found at least 8, because a sweep that swept nothing passes for the wrong reason.

**Two deliberate exceptions, recorded as data with their reasons** rather than left as strings that quietly fail to match:

- *"Empty — nothing to triage."* — an empty inbox is the **success** condition (`LIFECYCLE.md`: *"its success condition is being empty"*). Offering the shortest path to having some would be instructions for making work for yourself.
- *"+ to add"* — the workspace rail is a column of ~40px squares and a sentence cannot render in it. The pattern is split across two carriers: the visible label is the path, and a `title` says what the rail shows.

A fourth test asserts every exception still matches a live literal, so the list cannot silently become permission for strings nobody renders.

**One bug in the test itself, worth recording.** The extractor used `unicode_escape` to decode `—` in the source, which re-decoded real UTF-8 em dashes as latin-1 and turned them into mojibake — so a live literal stopped matching its own exception. The exception-still-used test caught it. It now decodes only `\uXXXX`.
