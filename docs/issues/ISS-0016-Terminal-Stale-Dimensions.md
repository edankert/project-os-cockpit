---
type: "[[issue]]"
id: ISS-0016
aliases: ["ISS-0016"]
title: "Embedded terminal: content runs off-screen below the prompt and mouse-scroll stops working after switching to the console"
status: fixed
severity: medium
owner: user:edwin
created: 2026-07-21
updated: 2026-07-21
source: ["user-report"]
related: ["[[FEAT-0003]]", "[[TASK-0185]]"]
---

# ISS-0016 — embedded terminal keeps stale dimensions after a view switch

## Symptom

1. The console information shown below the prompt sometimes runs off the bottom of the screen.
2. Mouse-wheel scrolling sometimes does not work after switching to a console from another screen/view; dragging the divider at the top of the console to resize it fixes the scrolling.

Reported 2026-07-21.

## Root cause

Both symptoms are one root cause: xterm's dimensions are recomputed (`fitAddon.fit()`) only on an explicit `showTerminal` (a single `requestAnimationFrame`), a `window` resize, or a divider drag. There is no `ResizeObserver` on the terminal container. So when the pane transitions hidden→visible on a view switch (or the window is moved to a differently-sized screen while the pane is hidden — the `window` resize handler early-returns while `terminalPane.hidden`), xterm keeps a stale geometry:

- a stale row count larger than the now-smaller mount, whose `overflow: hidden` clips the bottom rows — the prompt and the lines below it fall off-screen; and
- a stale `.xterm-viewport` scroll area, so mouse-wheel scrolling is dead until a `fit()` recomputes it — which is exactly why dragging the divider (whose mouseup calls `fit()`) restores scrolling.

## Fix

See [[TASK-0185]]: observe the terminal mount with a `ResizeObserver` that re-fits (debounced) on any size change — including the hidden→visible transition — and re-clamp a dragged pane height on window resize so it can't exceed a smaller window.
