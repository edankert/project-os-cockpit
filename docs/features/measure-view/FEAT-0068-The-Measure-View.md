---
type: "[[feature]]"
id: FEAT-0068
aliases: ["FEAT-0068"]
title: "The measure view — two surfaces side by side with a computed-style table, so comparisons happen in numbers instead of eyes"
status: done
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[DES-0007-The-Bench-Closes-The-Loop]]"]
goal: "Pick two panes — bench artefacts or the cockpit's own surfaces — pick an element in each, and read the differences as a table: box, font, colour, named and highlighted, copyable in the shape PHASE-022's issue notes used."
requirements: []
tasks:
  - "[[TASK-0303-The-Probe-Over-Artefacts]]"
  - "[[TASK-0304-The-Probe-Into-Own-Surfaces]]"
  - "[[TASK-0305-The-Diff-Table]]"
release: "[[REL-0001-The-Human-Has-Levers]]"
related: ["[[DES-0002-Cockpit-Design-System]]"]

---

# The measure view

## Goal

The tool whose absence cost PHASE-022 twelve rounds: every one began with hand-driven CDP measurement. Artefacts measure via same-origin `getComputedStyle`; the cockpit's own surfaces via the shell injecting the probe into its own webContents — the by-hand machinery made a feature.

## Out of Scope

- External apps. v1 is self and artefacts; pointing the probe elsewhere is its own phase with its own risk scan.
- Pixel diffing — rejected in [[DES-0007]]: pixels diff noisily and explain nothing.

## Acceptance

- [x] Two elements can be picked and their computed metrics read — box, type, colour, space ([[TASK-0303]])
- [x] The cockpit measures **itself**: any visible surface is a pane, which is the by-hand CDP loop made a feature ([[TASK-0304]])
- [x] Scope stayed at self and artefacts — asserted by a test that fails on `webview`, `BrowserView`, `loadURL(` or an outbound fetch
- [x] Differences are shown as a table with every property present and the differing ones marked ([[TASK-0305]])
- [x] Copy produces the markdown shape PHASE-022's issues used as evidence, differences only
- [x] Not pixel diffing — [[DES-0007]]'s rejection holds: no canvas, no image compare

## Verification

`tests/test_measure_view.py` — 8 tests over the module's shape and boundaries.

**A boundary found rather than designed:** sandboxed variant frames carry an opaque origin, so a parent cannot reach into them by construction. The property that makes a mockup safe to render is the same one that makes it unmeasurable from outside — so those are measured through the shell's own path or not at all.
