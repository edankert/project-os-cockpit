---
type: "[[issue]]"
id: ISS-0079
aliases: ["ISS-0079"]
title: "The note context menu keyed off `closest('a')`, so every button-shaped row — History, the uncommitted band — got the word menu and no way to copy anything about the note it names"
status: fixed
severity: medium
phase: "[[PHASE-020-Clipboard-That-Works]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["Edwin 2026-07-30, trying FEAT-0054: 'Still cannot copy a link tried a feature link in the history'"]
component: desktop-renderer
related: ["[[FEAT-0054-Clipboard-That-Works]]", "[[TASK-0262-Link-Aware-Context-Menu]]"]
fixed_by: ["[[TASK-0262-Link-Aware-Context-Menu]]"]
tests: []
---

# The menu only ever fired for anchors

## What

`docView`'s `contextmenu` handler began `target?.closest('a')` and returned when there was none. Rendered-markdown links are anchors, so [[TASK-0262]] tested against those and passed.

**The History rows are `<button>` elements.** So are the uncommitted band's. Measured:

```
tagName        : BUTTON
closest('a')   : null
text           : FEAT-0054 | One clipboard path, a link-aware conte…
inside #doc-view: true
```

Right-clicking a feature in History therefore fell through to the main-process selection menu and offered Copy / Dispatch on the word Chromium auto-selected — the exact symptom [[FEAT-0054]] was raised for, on a surface that feature never covered.

## Why it was missed

[[TASK-0262]] fixed the *anchor* path and I verified it on an anchor. The surfaces built earlier the same day — History, its uncommitted band, the fleet roll-up — are buttons because they carry structured columns rather than link text, and none of them was checked.

**"It works on the case I tested" is what the guard said too**: the test asserted `attachContextMenu` yields on a docs `linkURL`, which is true and does not cover a row that is not a link at all.

## Expected

Right-clicking any row that names a note offers that note's actions.

## Next Actions

- [x] Key the handler on note identity, not on element type
- [x] Carry `data-note-id` / `data-note-rel` on the rows that name a note
- [x] Guard it on a **button** row, since the anchor case is the one already covered

## Notes

The connected report — *"still cannot paste in the console using the context menu"* — is very likely the same bug wearing a different coat: a link that never reached the clipboard pastes as nothing. Menu paste writes to the PTY correctly under measurement, and Edwin confirms ⌘V works.

Two changes made alongside, so a paste is legible when it does happen: the menu hands focus back to the console afterwards, and the paste reports how many characters it wrote. A paste into a full-screen TUI is visually ambiguous — the app decides where the text lands — and silence read as failure.


## Fixed 2026-07-30

The handler now takes `closest('[data-note-rel]')` **or** `closest('a')`, and the History rows and the uncommitted band carry `data-note-id` / `data-note-rel`.

Verified on both paths — `defaultPrevented` is the honest signal, since the menu itself is native and invisible to a DOM assertion:

```
History row  FEAT-0054   handled: true
markdown <a> PHASE-020   handled: true
```

Guarded on the **button** case specifically. Asserting the anchor case would prove nothing: it is the one that already worked and still passed while this was broken.

### Two test mistakes on the way, both mine

**Stubbing `window.cockpit.app.showContextMenu` did nothing** — `contextBridge` objects are frozen, so the assignment failed silently and the probe reported "menu never asked" for code that was working. Switched to `event.defaultPrevented`.

**And the first guard for [[TASK-0262]] was true and useless.** It asserted `attachContextMenu` yields on a docs `linkURL` — correct, and completely blind to a row that is not a link at all. "It works on the case I tested" was what both the code and its test said.

### Alongside

The console menu now hands focus back to the terminal after an action, and a paste reports how many characters it wrote. Neither was broken; both were illegible. A paste into a full-screen TUI is visually ambiguous — the app decides where the text lands — and silence read as failure.
