---
type: "[[task]]"
id: TASK-0200
aliases: ["TASK-0200"]
title: "Overview stage rework — quiet-first focus band, mix-bar stat tiles (Requirements tile restored), Waiting-on-you list, full-width sparkbar + commits panel"
status: superseded
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
parent: "[[FEAT-0040-Overview-Rework]]"
effort: ""
due: ""
depends: ["[[TASK-0199]]"]
blocks: []
related: ["[[REQ-0022-Overview-State-Above-History]]", "[[TASK-0210]]"]
tests: []
---

# Overview stage rework

## Definition of Done

- [x] Focus band renders the SNAPSHOT focus chain quiet-first: the resting state reads last-completed with statuses, the focus note's age, and the last commit; a live session switches it to the pulsing in-flight variant (dossier plate C + exhibit).
- [x] `buildHero` becomes a six-tile stat strip with per-type status mix-bars and weekly deltas, absorbing the donuts; the Requirements tile renders (`hero.requirements` was computed but never rendered).
- [x] Waiting-on-you lists only the states audit's durable states — open issues (severity-ordered via the new `_slim` field), in-review stalls with age, ready-never-executed tests, parked/deferred tasks, open risks, done-but-unclosed phases — and renders "All clear" when empty.
- [x] Activity becomes a full-width ~34 px sparkbar with a plain-words summary line; a commits panel (from `/api/cockpit/commits`) replaces the note feed, with completions ticked, sync commits quiet, and no-doc-item commits flagged.
- [x] The donuts/histogram section and the old recent-note feed are removed; nothing above the fold at 900 px is a history surface (REQ-0022).

## Steps

- [x] Rework `buildHero` → stat strip + mix-bars (reusing `status_mix` buckets from `statuses.py` families).
- [x] Add the focus band component consuming the new `focus` payload block; wire the live/quiet switch to the existing agent-state signal.
- [x] Build the Waiting-on-you derivation over the scoped payload (durable-state filter, severity/age ordering) with typed-row markup extensible by TASK-0210.
- [x] Rework `buildBottomGrid` → Waiting-on-you + sparkbar + commits panel; delete the donut renderer.

## Notes

CSS stays inside existing tokens; the four mix-bar steps derive from them (REQ-0012). The Waiting-on-you row markup is the coupling point for FEAT-0041's announce rows (TASK-0210) — keep the row type extensible.

## Superseded 2026-07-30 — PHASE-012

The Waiting-on-you list this task delivered has been **deleted**, not emptied, and this status records that as a reversal rather than a cleanup.

It was right for the page it was built for: the phase squares had two visual states and could not say that anything needed a human, so a prose list was the only way to surface it. [[DES-0004]] gave the square six states, at which point the list was re-listing items already on screen — measured 2026-07-30: all 9 rows it showed had a square, 8 of them visible, every one rendering plain hollow.

Superseded by [[ISS-0068]]'s implementation. [[DES-0001]]'s plate 5 specified this section by name, so the reversal is a departure from an accepted design and is recorded there too.
