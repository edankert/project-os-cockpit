---
type: "[[task]]"
id: TASK-0301
aliases: ["TASK-0301"]
title: "Variants sit beside each other"
status: done
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0067-Designs-Render-Their-Artefacts]]"]
parent: "[[FEAT-0067-Designs-Render-Their-Artefacts]]"
effort: S
depends: ["[[TASK-0300]]"]
blocks: []
related: []
tests: []
---

# Variants sit beside each other

## Definition of Done

- Two-up (wrapping beyond two) with the variant name as each pane's head; single-variant designs render full-width unchanged.

## Done — 2026-08-11

A horizontal strip: each variant a titled cell, scrolling sideways rather than wrapping.

**A row that scrolls, not a grid that wraps** — two arrangements are compared by looking *across*, and wrapping one beneath the other turns a comparison into a list, which is the thing a variant strip exists not to be.

Placement follows what the note actually is: a design **with an artifact** keeps the artifact as the stage and puts the strip beneath it; a design **with variants and no artifact** *is* its variants, so the strip becomes the stage. Compare mode is untouched — revision-vs-working-copy stays two frames at one viewport.
