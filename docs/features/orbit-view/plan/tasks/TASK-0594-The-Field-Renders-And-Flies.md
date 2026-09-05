---
type: "[[task]]"
id: TASK-0594
aliases: ["TASK-0594"]
title: "The field renders and flies — 1537 nodes and 16148 edges, coloured by status band, at a frame rate that survives a laptop"
status: backlog
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-09-05
updated: 2026-09-05
source: ["[[FEAT-0144-The-Corpus-Has-An-Inside]]"]
parent: "FEAT-0144"
effort: ""
due: ""
depends: ["TASK-0593", "TASK-0596"]
blocks: ["TASK-0595"]
related: ["[[DES-0013-Nine-Ways-To-Read-The-Record]]"]
tests: []
---

# The field renders and flies

## Objective

`~orbit` draws the field and lets you move through it: drag to turn, scroll to close in, hover an edge to read the sentence that made it.

## Detail

Canvas, not SVG — 16148 edge elements in the DOM is a different and worse problem.

Colour is the **status band**, read from the same source the rest of the cockpit reads. Size is inbound links. Clusters are phases.

The treatment — the holographic field or the lit workshop of blocks — is [[TASK-0596]]'s decision and arrives before this task starts. The two differ in more than palette: blocks are opaque and stack, so occlusion carries meaning, and edges have to be drawn differently or not at all.

**Reduced motion is not an afterthought.** The field must not drift on its own for a reader who has asked for stillness; it still turns under the pointer.

## Acceptance

- Interactive at this repo's real size on the development laptop, with the frame budget stated in the note rather than described as "smooth"
- `prefers-reduced-motion` stops the idle rotation and nothing else
- Hovering an edge shows the containing sentence from the source note
