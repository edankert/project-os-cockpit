---
type: "[[task]]"
id: TASK-0093
aliases: ["TASK-0093"]
title: "hiddenInset title bar (integrated macOS traffic lights)"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0009"
effort: ""
due: ""
depends: []
blocks: []
related: []
tests: []
---

# hiddenInset title bar

## Definition of Done
- [ ] `BrowserWindow` constructor opts add `titleBarStyle:
      'hiddenInset'` on macOS (no-op on other platforms — Electron
      falls through to the platform default).
- [ ] CSS reserves the top ~28 px of the rail for the traffic
      lights so they don't overlap rail content.
- [ ] No regressions: window drag still works (the title bar area
      remains a drag region by default).

## Steps
- [ ] `main.ts` — extend `createWindow` opts.
- [ ] `renderer.css` — increase `.rail` top padding when on macOS
      (or unconditionally for now, since this is a macOS-first app).
