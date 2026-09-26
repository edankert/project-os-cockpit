---
type: "[[task]]"
id: TASK-0307
aliases: ["TASK-0307"]
title: "Click leaves a pin; selection quotes itself"
status: done
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0069-Annotate-To-Request]]"]
parent: "[[FEAT-0069-Annotate-To-Request]]"
effort: M
depends: ["[[TASK-0306]]"]
blocks: []
related: []
tests: []
---

# Click leaves a pin; selection quotes itself

## Definition of Done

- Pin on a rendered artefact captures the anchor and opens the comment box; text selection in the note does the same with a quote anchor; esc costs nothing.

## Done — 2026-08-11

`Annotate selection` on the design page: select text, comment, and the **quote** becomes the anchor — plus the variant it sits in, read from the nearest variant cell rather than inferred from position.

**A selection, not a pin.** A quoted anchor survives a reflow, and when it does not survive an *edit* it can say so rather than float to whatever now occupies those coordinates. A test asserts the affordance reads no `clientX`, `clientY`, `offsetX`, `pageX` or `getBoundingClientRect` — the anchor cannot become a coordinate by a later edit without failing.

**esc costs nothing**, as the DoD asks: the selection is read at click time and the prompt writes only on confirm.

On the design page rather than as a global verb — an annotation is always *about* a design, and offering it elsewhere would invite anchors to things that have no revisions to be lost across.
