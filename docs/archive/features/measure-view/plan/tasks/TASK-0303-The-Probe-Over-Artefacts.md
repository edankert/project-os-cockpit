---
type: "[[task]]"
id: TASK-0303
aliases: ["TASK-0303"]
title: "Pick an element in an artefact, harvest its computed story"
status: done
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0068-The-Measure-View]]"]
parent: "[[FEAT-0068-The-Measure-View]]"
effort: M
depends: []
blocks: []
related: []
tests: []
---

# Pick an element in an artefact, harvest its computed story

## Definition of Done

- Element pick by click in same-origin iframes; harvest of box, font, colour, spacing; hover preview of what will be picked.

## Done — 2026-08-11

`harvest(el, label)` in `measure.ts`: box, type, colour and space, grouped so the table reads by question rather than alphabetically.

**Computed, not declared.** `getComputedStyle` resolves everything — a `width: auto` comes back as the used pixel value — which is the point: a design question is about what the browser *did*, not what the stylesheet asked for. Box metrics come from `getBoundingClientRect` rather than the style, because `width` reports the content box under `box-sizing: content-box` and *"how big is this on screen"* is about the border box.

**Click, not hover.** Hover commits by accident, and the thing being measured is usually under the pointer on the way somewhere else. Escape disarms.

**One boundary discovered rather than designed**: variant frames are sandboxed with an opaque origin, so a parent cannot reach into them **by construction** — the same property that makes them safe makes them unmeasurable from outside. Same-origin artefact frames go through the identical probe; sandboxed variants are measured by the shell's own path ([[TASK-0304]]) or not at all.
