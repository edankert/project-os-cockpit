---
type: "[[task]]"
id: TASK-0263
aliases: ["TASK-0263"]
title: "Terminal copy survives the right-click, and ⌘C/⌘V route to whichever pane is focused"
status: done
phase: "[[PHASE-020-Clipboard-That-Works]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0054-Clipboard-That-Works]]"]
parent: "[[FEAT-0054-Clipboard-That-Works]]"
effort: M
depends: ["[[TASK-0261-One-Clipboard-Path]]"]
blocks: []
related: ["[[TASK-0167-Terminal-Context-Menu]]"]
tests: []
---

# Terminal copy and paste

## Definition of Done
- [x] The terminal's `contextmenu` handler **captures the selection before it is cleared**, and the menu copies that captured text
- [x] `Copy` is enabled after a right-click on a selection
- [x] The app **Edit menu** routes Copy/Paste to the terminal when the terminal is focused, and to the document otherwise
- [x] ⌘V pastes **once** — not once from the menu accelerator and again from the renderer
- [x] Copy-on-select still works, and still reports a failure if one happens

## Steps
- [x] Capture `term.getSelection()` in the `contextmenu` listener, before `showTerminalMenu`
- [x] Replace the Edit menu's `role: 'copy'` / `role: 'paste'` with `click` handlers that ask the renderer what is focused
- [x] Remove the renderer's ⌘C/⌘V keydown branch, now that the menu owns the accelerator
- [x] Test: the capture, and a guard that the Edit menu no longer uses bare roles for copy/paste

## Notes

**Measured before the fix:**

```
selection before right-click : true
selection after right-click  : false
Copy menu item               : DISABLED
```

The right-click clears xterm's selection before `showTerminalMenu()` asks `term.hasSelection()`, so Copy is greyed out precisely when a user reaches for it. Copy-on-select works, which is why the asymmetry was the thing that got noticed.

**Why the Edit menu has to change.** `{ role: 'editMenu' }` binds ⌘C/⌘V to `webContents.copy()` / `paste()`, which only ever see the DOM. xterm's selection is not a DOM selection, so the role cannot serve the terminal — and on macOS the accelerator fires *before* the page's keydown, so the renderer's handler is racing something it cannot win. Context-aware `click` handlers are one path that is correct in both panes.

## Done 2026-07-30

**The capture.** `capturedTerminalSelection` is taken in the `contextmenu` listener, before `showTerminalMenu` runs, and both the enabled-state and the copy read it.

**Proven load-bearing, not merely plausible.** The clearing turned out to be non-deterministic — the second measurement showed the selection surviving where the first showed it cleared. So rather than rely on reproducing the race, the test forces the worst case: capture, then `term.clearSelection()`, then click Copy.

```
selection deliberately cleared : true
Copy still enabled             : true
copied despite cleared selection: true
```

Mutation-verified by removing the capture line.

**The Edit menu is context-aware.** `role: 'copy'` / `role: 'paste'` replaced with `click` handlers that send `menu:edit` to the renderer, which routes to the console when it has focus and to the document otherwise. The renderer's ⌘C/⌘V keydown branch is **deleted** — it was racing the accelerator, which on macOS fires first, and ⌘V could paste twice.

A paste with no focused target now says *"Nothing here accepts a paste"* rather than doing nothing.
