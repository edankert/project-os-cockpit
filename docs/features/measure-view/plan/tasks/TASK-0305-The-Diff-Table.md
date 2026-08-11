---
type: "[[task]]"
id: TASK-0305
aliases: ["TASK-0305"]
title: "The differences as a table, copyable as markdown"
status: done
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0068-The-Measure-View]]"]
parent: "[[FEAT-0068-The-Measure-View]]"
effort: S
depends: ["[[TASK-0303]]"]
blocks: []
related: []
tests: []
---

# The differences as a table, copyable as markdown

## Definition of Done

- Both elements' metrics side by side, differences highlighted; copy produces the markdown table shape PHASE-022's issues used as evidence.

## Done — 2026-08-11

Both elements side by side, grouped, with **differences tinted** — and the copy button emits the markdown table shape PHASE-022's issues used as evidence.

Two judgments in the table:

- **Every property is shown, differences merely marked.** *What is the same* is half the answer when two surfaces look different; a table filtered to differences sends the reader back to the inspector for the rest.
- **The markdown is differences-only.** The full table is on screen; an issue quoting forty identical rows buries its own point. An all-same comparison says so in one line rather than emitting an empty table.

Only the differing rows are tinted — highlighting every row makes the table one colour, which is the same as no colour.

The panel is `position: fixed`: the subject is whatever is already on screen, and reflowing it to make room would change what is being measured.
