---
type: "[[feature]]"
id: FEAT-0054
aliases: ["FEAT-0054"]
title: "One clipboard path, a link-aware context menu, and no silent failures"
status: done
phase: "[[PHASE-020-Clipboard-That-Works]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["Edwin 2026-07-30: 'The copy and paste functionality is not great yet, can you do a full review'"]
goal: "Copy and paste behave identically in the doc pane and the console, right-click acts on what was clicked rather than on what Chromium selected, and a clipboard operation that fails says so."
requirements: []
tasks:
  - "[[TASK-0261-One-Clipboard-Path]]"
  - "[[TASK-0262-Link-Aware-Context-Menu]]"
  - "[[TASK-0263-Terminal-Copy-And-Paste]]"
release: ""
related: ["[[FEAT-0037-Native-Text-Menus]]"]

---

# A clipboard that works

## Brief plan

1. **[[TASK-0261]]** — move every clipboard read and write to the main process behind IPC, and surface failures. The foundation: Electron's `clipboard` module has no focus or permission constraints, which deletes the whole "worked when focused, failed otherwise" class.
2. **[[TASK-0262]]** — the context menu reads `params.linkURL` and leads with link actions.
3. **[[TASK-0263]]** — terminal copy captures the selection before the right-click clears it, and ⌘C/⌘V route correctly in both panes.

## Acceptance

- Right-clicking a note link offers Copy link, Copy the ID, Dispatch the ID, Open — and the auto-selected word does not masquerade as intent.
- Right-clicking a terminal selection offers an **enabled** Copy that copies that selection.
- ⌘C copies the terminal's selection when the terminal is focused, and the document's selection otherwise. ⌘V pastes into whichever is focused, once.
- A clipboard failure shows a status line rather than nothing.
- `navigator.clipboard` no longer appears in the renderer.

## Scope

- In: `context-menu.ts`, the terminal menu and key handling, the app Edit menu, and the five renderer clipboard call sites.
- Out: rich-text formats; the browser client, which uses the OS's own menus.


## Done 2026-07-30

All five items, verified live.

| reported | cause | fix |
|---|---|---|
| right-click a link offers the *word* | two menus fire for one click; the selection menu wins | `attachContextMenu` yields when `linkURL` is a docs path |
| console Copy does nothing | the right-click clears xterm's selection before the menu reads it | capture the selection in the `contextmenu` listener |
| console paste does nothing | ⌘V raced the Edit-menu accelerator; failures were bare-caught | context-aware Edit menu; every failure surfaces |

**The diagnosis changed twice while doing it**, and both corrections are worth keeping:

1. My first measurement said `navigator.clipboard` was blocked outright. It was the test harness not focusing the window. A clipboard test that does not control focus measures itself.
2. My first plan was to add link items to the selection menu. Reading the code showed a rich link menu **already existed and was already wired** — the bug was that a second menu overrode it. Adding items would have made three menus for one click.

## Owed

- **`Copy as Markdown quote` and `Dispatch selection as prompt…` still only appear for a real text selection**, which is right — but Chromium's auto word-select still makes them available on a plain right-click in prose. Distinguishing a deliberate selection from an auto one needs `params.selectionText` compared against the word at the click point, and is not worth it until someone is bitten.
- **Mode 1 untouched.** The browser client uses the OS's own menus and has none of these problems.
