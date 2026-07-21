---
type: "[[task]]"
id: TASK-0185
aliases: ["TASK-0185"]
title: "Fix: embedded terminal keeps stale dimensions after a view switch — content clipped below the prompt and mouse-scroll dead until a manual resize"
status: done
phase: "[[PHASE-004-Embedded-Terminal]]"
owner: user:edwin
created: 2026-07-21
updated: 2026-07-21
source: ["[[ISS-0016]]"]
parent: "FEAT-0003"
effort: ""
due: ""
depends: []
blocks: []
related: []
tests: []
verification_waiver: "Renderer-only fit/observer wiring; xterm layout/scroll behaviour has no automated renderer unit-test surface. Verified by tsc build, code trace, and a live CDP smoke check that the terminal re-fits on show (dimensions identical and un-clipped after a view-switch reshow); independent review CLOSE on the code."
---

# TASK-0185 — re-fit the terminal on any container size change

Fixes [[ISS-0016]]. Add a `ResizeObserver` on `.terminal-mount` that calls `fitAddon.fit()` (rAF-debounced) whenever the container's size changes — most importantly the hidden→visible transition when the user switches to the console, which the single `requestAnimationFrame` fit in `showTerminal` handles unreliably and which nothing handles when the layout changed while the pane was hidden. This keeps xterm's row count and scroll viewport in sync, fixing both the content-clipped-below-the-prompt overflow and the dead mouse-wheel scrolling.

Also re-clamp a dragged pane height on `window` resize (`min(innerHeight - 120, max(80, h))`) so moving to a smaller screen can't leave the pane taller than the window.

Verification: build the renderer; switch to the console from another view and confirm the prompt is visible and mouse-wheel scrolling works without a manual resize; shrink the window with a tall terminal and confirm the prompt stays on-screen.
