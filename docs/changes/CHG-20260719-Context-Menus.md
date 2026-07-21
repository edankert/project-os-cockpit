---
type: "[[change]]"
id: CHG-20260719-Context-Menus
aliases: ["CHG-20260719-Context-Menus"]
title: "Context menus & clipboard — native edit menu, terminal menu, dispatch-selection"
status: merged
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
commit: ""
pr: ""
reviewed_by: "model:claude-opus"
review_date: 2026-07-19
review_verdict: approved
impacts: ["main webContents context-menu handler", "terminal context menu + clipboard keys", "menu:dispatch-selection IPC"]
issues: []
features: ["[[FEAT-0037-Context-Menus-And-Clipboard]]"]
related: ["[[TASK-0166]]", "[[TASK-0167]]", "[[TASK-0168]]"]
---

# Context menus & clipboard (FEAT-0037)

## Summary

**TASK-0166.** A single main-process `webContents "context-menu"` handler (`ipc/context-menu.ts`) provides the native text menu Electron omits: role-based Cut/Copy/Paste/Select All on editable targets (plus spellcheck suggestions), Copy on plain selections. Non-editable, no-selection right-clicks yield no items, so the renderer's own nav/card menus keep priority uncontested.

**TASK-0167.** The terminal gets its own menu (xterm's selection isn't a DOM selection, so the native menu can't see it): Copy (when selected), Paste (bracketed-paste wrapping for multi-line so a pasted block doesn't run line-by-line), Select All, Clear, and a persisted Copy-on-select toggle. ⌘C copies the xterm selection when one exists (else falls through to the shell), ⌘V pastes.

**TASK-0168.** The doc-pane selection menu adds "Copy as Markdown quote" and "Dispatch selection as prompt…" — the latter sends the selection over `menu:dispatch-selection` to the renderer, which dispatches it as an agent prompt for the current note via the FEAT-0025 runtime (confirm dialog, same delivery rules).

## Verification

CDP: the terminal menu renders all four actions + copy-on-select, the toggle persists, the menu closes on outside click, and the dispatch-selection IPC is exposed. The native edit menu uses standard Electron roles (OS menu, not DOM-inspectable). `tsc` clean; app loads without errors.

Files: `desktop/src/ipc/context-menu.ts`, `desktop/src/main.ts`, `desktop/src/preload.ts`, `desktop/src/renderer/{renderer.ts,renderer.css}`.
