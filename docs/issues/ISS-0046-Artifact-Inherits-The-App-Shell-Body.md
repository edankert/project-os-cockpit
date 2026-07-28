---
type: "[[issue]]"
id: ISS-0046
aliases: ["ISS-0046"]
title: "An artifact that links the app's stylesheets inherits an app-shell body and cannot scroll"
status: fixed
severity: high
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["user report 2026-07-28: 'Still no scroll and the margins are still wrong'"]
related: ["[[TASK-0227-Expose-Shell-Stylesheet]]", "[[TASK-0228-Living-Style-Guide]]", "[[TASK-0221-Design-Authoring-Contract]]", "[[ISS-0044-Framed-Design-Scroll-Theme-Margins]]"]
fixed_by: []
---

# The artifact inherited an application shell

## What it was

```
body { overflow: hidden }   →  4792px of content clipped to a 963px viewport
```

`base.css` declares `body { height: 100dvh; display: flex; flex-direction: column; overflow: hidden }` and `renderer.css` adds `body { display: block; overflow: hidden }`. Both are correct for a window that owns the viewport. Both are fatal for a document.

The style guide links those stylesheets — that is the whole point of [[TASK-0227]], so it can show real tokens and real widgets — and inherited the shell's body with them. The page rendered completely and **could not be scrolled a single pixel**, and its padding did nothing because the body was a clipped flex column rather than a document.

That is both of Edwin's complaints, from one rule.

## Why the previous two attempts missed it

[[ISS-0044]] treated "no scroll" as a *chrome* problem — the stage swallowing the wheel — and scaled the frame to fit. That reasoning was sound and the measurement supported it, but it was measuring the wrong layer: the artifact could not scroll **anywhere**, including opened directly in a browser tab. A bare frame test had scrolled fine, and I read that as proof the artifact was fine, when what it proved was only that *that* artifact was fine — it was a synthetic fixture that linked nothing.

The tell was available the whole time and I did not look for it: `getComputedStyle(document.body).overflow` on the real artifact.

## Fix

The artifact resets what it borrows:

```css
html { height: auto; overflow: visible; }
body { height: auto; min-height: 100%; display: block; overflow: visible; }
```

Verified: `overflow: visible`, height 4871px in a 963px viewport, `window.scrollY` 0 → 900 on a scroll, padding applied.

## The general rule

**An artifact that links the application's stylesheets inherits the application's shell.** This is not a quirk of one file — it is the standing cost of [[TASK-0227]], and every future artifact that wants real widgets pays it. Recorded in the authoring contract ([[TASK-0221]]) rather than left as a patch in one page.
