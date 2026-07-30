---
type: "[[phase]]"
id: PHASE-020
aliases: ["PHASE-020"]
title: "A clipboard that works the same way everywhere, and says so when it does not"
status: done
order: 20
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
goal: "One clipboard path for the whole app, right-click menus that act on what was actually clicked, and a copy that never fails in silence."
features:
  - "[[FEAT-0054-Clipboard-That-Works]]"
requirements: []
issues:
  - "[[ISS-0079-Context-Menu-Only-Ever-Fired-For-Anchors]]"
  - "[[ISS-0080-Console-Context-Menu-Replaced-By-Terminal-Convention]]"
depends: ["[[PHASE-016-The-Overview-Answers-Questions]]"]
related: ["[[FEAT-0037-Native-Text-Menus]]", "[[TASK-0167-Terminal-Context-Menu]]"]
tags: [desktop, clipboard]
---

# A clipboard that works everywhere

## Where this came from

Edwin, 2026-07-30: *"The copy and paste functionality is not great yet"* — with two specific reports, both of which reproduced.

## What the review found

**The app has two clipboard stacks.** The doc pane uses Electron menu *roles*, which run in the main process and have no restrictions. The terminal uses `navigator.clipboard` in the renderer, which needs document focus and a permission. Different failure modes, no shared behaviour — which is exactly why one works and the other does not.

**The context menu never looks at what was clicked.** `context-menu.ts` reads `params.isEditable` and `params.selectionText` and nothing else. Electron also hands it `params.linkURL` and `params.linkText` on every event, and those are ignored — so right-clicking a note link offers actions on the word Chromium auto-selected under the cursor, and nothing about the link.

**Terminal Copy is disabled exactly when you need it.** Measured:

```
selection before right-click : true
selection after right-click  : false
Copy menu item               : DISABLED
```

The right-click clears xterm's selection before the menu asks whether one exists.

**Every failure is silent.** Five `navigator.clipboard` call sites, all `void`-ed or bare-caught. A copy that does not happen says nothing.

## Scope

- **[[FEAT-0054]]** — one clipboard path through the main process, a link-aware context menu, terminal copy/paste that works from every route, and failures that surface.

## Out of Scope

- **Rich-text or HTML clipboard formats.** Everything here is plain text and Markdown, and the one existing non-plain path (`Copy as Markdown quote`) stays as it is.
- **The browser client (mode 1).** It has the OS's own menus and none of these problems.

## Exit Criteria

- [x] Right-clicking a note link offers actions on the **link** — evidence: `attachContextMenu` yields on a docs `linkURL`, so the existing `doc-link` menu (Open · Copy ID · Copy path · Copy link · agent verbs) is no longer overridden
- [x] Terminal Copy is enabled after a right-click on a selection — evidence: with the selection *deliberately cleared*, Copy stayed enabled and still copied
- [x] ⌘C / ⌘V do the right thing in both panes — evidence: the Edit menu asks the renderer which pane has focus; the racing keydown branch is deleted
- [x] No clipboard call can fail silently — evidence: writes are read back and every failure shows a status
- [x] One clipboard path — evidence: no `navigator.clipboard` call left in the built renderer

## Notes

**The measurement mattered more than the reasoning here.** My first diagnosis was that `navigator.clipboard` was blocked outright — the test said `writeText` did nothing and `readText` was denied. Both were artefacts of the test harness not focusing the window. Re-run with focus, both worked, and the real bug turned out to be the selection being cleared by the right-click. Worth recording: a clipboard test that does not control window focus measures its own harness.


## Closed 2026-07-30

[[FEAT-0054]] done, three tasks, five guards, all mutation-verified.

**Both reports reproduced before anything was written**, and both diagnoses were wrong on the first pass:

- `navigator.clipboard` looked blocked outright — it was my test not focusing the window.
- The link menu looked missing — it existed, was wired, and was being overridden by a second menu firing for the same click.

Reading the code and re-running with focus cost twenty minutes and prevented building the wrong thing twice: the second plan would have added a **third** menu to a click that already had two.


## Reopened and re-closed 2026-07-30

Two follow-ups from Edwin trying it, both fixed:

- **[[ISS-0079]]** — the note context menu keyed off `closest('a')`, so History's `<button>` rows got the word menu. My [[TASK-0262]] fix covered anchors and I verified it on an anchor.
- **[[ISS-0080]]** — the console's context menu never worked for him across three attempts. Replaced with the terminal convention: **select copies, right-click pastes**, no menu.

**The pattern in both is the same and worth naming.** Each time I verified the case I had built, on the surface I had built it for, and each time the user found the surface I had not. Right-clicking an anchor worked; right-clicking a History row did not. A dispatched `contextmenu` event worked; a real right-click did not.
