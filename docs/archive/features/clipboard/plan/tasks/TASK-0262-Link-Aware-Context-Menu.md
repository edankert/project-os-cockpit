---
type: "[[task]]"
id: TASK-0262
aliases: ["TASK-0262"]
title: "The context menu acts on the link that was right-clicked, not the word Chromium selected"
status: done
phase: "[[PHASE-020-Clipboard-That-Works]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0054-Clipboard-That-Works]]"]
parent: "[[FEAT-0054-Clipboard-That-Works]]"
effort: S
depends: []
blocks: []
related: ["[[FEAT-0037-Native-Text-Menus]]"]
tests: []
---

# A link-aware context menu

## Definition of Done
- [x] When `params.linkURL` is set, the menu leads with **link** actions: Copy link · Copy `<ID>` · Dispatch `<ID>` as prompt · Open
- [x] The note ID is extracted from the link when it has one, so the label reads `Dispatch FEAT-0028 as prompt…` rather than a path
- [x] Selection actions remain available **below** the link actions
- [x] Non-link right-clicks are unchanged — `Copy as Markdown quote` and `Dispatch selection as prompt…` keep working
- [x] An external `http(s)` link offers Open and Copy link, and no dispatch — there is no note to dispatch

## Steps
- [x] Read `params.linkURL` / `linkText` in `attachContextMenu`
- [x] Resolve `/docs/<rel>` to an ID with the same pattern the index uses
- [x] Test: the menu template built for a note link, an external link, and a plain selection

## Notes

**A right-click on a link is about the link.** Chromium auto-selects the word under the cursor on macOS, and the current menu reads that as intent — so right-clicking `FEAT-0028-Fleet-Health-Surface` offers to dispatch a word fragment and says nothing about the feature. The information was in `params.linkURL` all along; nothing read it.

Ordering matters more than the extra items: the first thing in the menu is what the menu is *about*.

## Done 2026-07-30 — and the diagnosis changed while doing it

**A rich link menu already existed.** `main.ts`'s `doc-link` template offers Open · Copy ID · Copy path · Copy link plus the agent verbs, and `renderer.ts` wires `docView`'s `contextmenu` to it for any `/docs/*.md` anchor.

So the report was not "there is no link menu" — it was **"the wrong menu wins"**. Both handlers fire for one right-click, and `preventDefault()` on the DOM event does **not** suppress the main-process `context-menu` event. The selection menu, built from the word Chromium auto-selected, popped over the link menu.

**Fix: `attachContextMenu` yields.** When `params.linkURL` names a `/docs/…md` path it returns immediately and lets the renderer's menu own the click.

**Non-docs links gained actions**, because nothing offered any: Open link · Copy link · Copy `<ID>` · Dispatch `<ID>` as prompt · Copy link text.

The original plan — add link items to this menu — would have produced *three* menus for one click. Reading the code before writing it was the whole difference.
