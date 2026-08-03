---
type: "[[feature]]"
id: FEAT-0068
aliases: ["FEAT-0068"]
title: "The measure view — two surfaces side by side with a computed-style table, so comparisons happen in numbers instead of eyes"
status: planned
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[DES-0007-The-Bench-Closes-The-Loop]]"]
goal: "Pick two panes — bench artefacts or the cockpit's own surfaces — pick an element in each, and read the differences as a table: box, font, colour, named and highlighted, copyable in the shape PHASE-022's issue notes used."
requirements: []
tasks: []
release: ""
related: ["[[DES-0002-Cockpit-Design-System]]"]
tests: []
---

# The measure view

## Goal

The tool whose absence cost PHASE-022 twelve rounds: every one began with hand-driven CDP measurement. Artefacts measure via same-origin `getComputedStyle`; the cockpit's own surfaces via the shell injecting the probe into its own webContents — the by-hand machinery made a feature.

## Out of Scope

- External apps. v1 is self and artefacts; pointing the probe elsewhere is its own phase with its own risk scan.
- Pixel diffing — rejected in [[DES-0007]]: pixels diff noisily and explain nothing.
