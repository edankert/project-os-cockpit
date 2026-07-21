---
type: "[[change]]"
id: CHG-20260721-Terminal-Refit-On-Visibility
title: "Embedded terminal re-fits on any container size change — no more off-screen prompt or dead scroll after a view switch"
date: 2026-07-21
author: user:edwin
status: merged
related: ["[[ISS-0016]]", "[[TASK-0185]]", "[[FEAT-0003]]"]
reviewed_by: "opus-independent-review"
review_date: 2026-07-21
review_verdict: CLOSE
---

# CHG-20260721 — re-fit the embedded terminal on visibility/size change

## What changed

`ensureXterm` in `desktop/src/renderer/renderer.ts` now attaches a `ResizeObserver` to `.terminal-mount` that calls `fitAddon.fit()` (rAF-debounced, skipped while the pane is hidden) on any container size change. The `window` resize handler additionally re-clamps a dragged pane height to `min(innerHeight - 120, max(80, h))` so it can't exceed a smaller window.

## Why

Two user-reported symptoms (ISS-0016), one root cause: xterm was re-fit only on an explicit `showTerminal` (a single `requestAnimationFrame`), a `window` resize, or a divider drag — there was no observer on the container. So when the pane went hidden→visible on a view switch (or the window moved to a differently-sized screen while the pane was hidden, where the `window` resize handler early-returns), xterm kept a stale geometry: a stale row count whose bottom rows clipped off-screen under the mount's `overflow: hidden` (the prompt and lines below it ran off the bottom), and a stale `.xterm-viewport` scroll area (mouse-wheel scrolling dead until a manual resize — which is why dragging the divider, whose mouseup calls `fit()`, fixed it).

## Impact

- **Behaviour**: switching to the console from another view now always shows a correctly-sized terminal — prompt visible, mouse-wheel scrolling live — with no manual resize. A tall terminal re-clamps when the window shrinks so the prompt stays on-screen.
- **Scope**: renderer-only; requires a desktop rebuild (`npm run build`) — done, `tsc` clean. No loop risk: `fit()` resizes xterm *within* the mount, so it doesn't change the mount's own box and can't re-trigger the observer.
- **Verification**: live CDP check — after a view-switch→reshow the mount/xterm/viewport dimensions are identical and correct (xterm screen 267px inside a 279px mount → no clip; viewport 267/267 → scroll area live; 18 rows). No renderer unit-test surface exists; rides FEAT-0003's manual-checklist waiver.

## Files

- `desktop/src/renderer/renderer.ts` — `ResizeObserver` on the terminal mount + window-resize height clamp.
