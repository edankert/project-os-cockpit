---
type: "[[plan]]"
title: "Plan — clipboard that works"
status: done
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
implements: ["[[FEAT-0054-Clipboard-That-Works]]"]
related: ["[[PHASE-020-Clipboard-That-Works]]"]
---

# Plan

1. **[[TASK-0261]]** first — everything else sits on it, and it is what makes the failures visible enough to test.
2. **[[TASK-0262]]** — independent of the other two.
3. **[[TASK-0263]]** — depends on 0261 for the paste path.

## The decision this rests on

**Main-process clipboard, not `navigator.clipboard`.** The renderer API needs document focus for `writeText` and a granted permission for `readText`; Electron's `clipboard` module needs neither. Every failure reported in the review traces to one of those two constraints or to a bare `catch`.

## Three things to watch

**⌘C must not be one thing.** The terminal's selection is not a DOM selection, so a single handler cannot serve both panes. The Edit menu items become context-aware — they check what is focused — rather than being roles that only ever mean one thing.

**A right-click on a link is about the link.** Chromium auto-selects the word under the cursor, and the existing menu treats that as user intent. When `linkURL` is present it wins; selection actions stay available below it.

**Do not lose `Copy as Markdown quote` or `Dispatch selection as prompt`.** They are the reason this menu exists ([[FEAT-0037]] / TASK-0168) and they work today. This adds to them.
