---
type: "[[task]]"
id: TASK-0295
aliases: ["TASK-0295"]
title: "The ACCEPTANCE DEBT record card with drill-down"
status: done
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0065-Acceptance-Debt-Surface]]"]
parent: "[[FEAT-0065-Acceptance-Debt-Surface]]"
effort: S
depends: ["[[TASK-0294]]"]
blocks: []
related: []
tests: []
---

# The ACCEPTANCE DEBT record card with drill-down

## Definition of Done

- Record-grammar card on the overview: three numbers, each opening to its rows, rows navigating to their notes.
- Absent entirely when all three are zero — a zero-debt banner is noise.

## Done — 2026-08-11

`Acceptance debt · 28` on the overview's record column, with a band per number and drill-down rows into the requirements themselves.

**A record card, not a badge**, and deliberately so: none of this is owed to a person on a deadline. It is the gap between claimed and shown, and the value is that the gap was previously invisible — not that somebody must close it today. Putting it on a view button would have made it a nag, which is the mistake [[ISS-0122]] and the close-out pill are both about.

Absent at zero, like every other card here. An empty band inside it is omitted rather than rendered as `0`.
