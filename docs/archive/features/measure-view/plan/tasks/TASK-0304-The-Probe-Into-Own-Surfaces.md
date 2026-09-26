---
type: "[[task]]"
id: TASK-0304
aliases: ["TASK-0304"]
title: "The cockpit measures itself — the by-hand CDP loop made a feature"
status: done
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0068-The-Measure-View]]"]
parent: "[[FEAT-0068-The-Measure-View]]"
effort: M
depends: ["[[TASK-0303]]"]
blocks: []
related: []
tests: []
---

# The cockpit measures itself

## Definition of Done

- The shell injects the same probe into its own webContents; any visible cockpit surface can be a measure pane.
- Explicitly scoped to self: no external targets (the phase's out-of-scope, restated where the code would grow it).

## Done — 2026-08-11

The cockpit measures itself: the picker runs in the renderer's own document, so **any visible cockpit surface is a measure pane** — which is exactly the by-hand CDP loop PHASE-022 ran twelve times, made a feature.

**Explicitly scoped to self**, and asserted rather than asserted-in-prose: `test_the_scope_stayed_at_self_and_artefacts` reads the measure path and fails on `webview`, `BrowserView`, `loadURL(` or an outbound `fetch`. Pointing the probe at an external app is its own phase with its own risk scan, and this makes growing it there a visible change rather than a quiet parameter.
