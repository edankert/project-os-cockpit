---
type: "[[issue]]"
id: ISS-0157
aliases: ["ISS-0157"]
title: "The usage block scrolls away with the cards it is meant to sit under — the attention panel scrolls as one piece"
status: "fixed"
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
source: ["Edwin 2026-08-13: 'the Needs you section, the project cards and the usage section seem to scroll together when getting too big, I think the usage section should be anchored to the bottom and should be visible, the other Needs you items can scroll'"]
severity: medium
component: desktop-renderer
parent: ""
related: ["[[FEAT-0030]]", "[[FEAT-0081]]", "[[DES-0008-The-Returning-Human]]"]
tests: []
---

# The usage block scrolls out of the attention panel

## Problem

`#ws-attention` is a single scroll container — `max-height: 45%; overflow-y: auto` — holding four things stacked in one flow: the **Needs you** heading, the per-workspace cards, the *"N finished today"* footer, and the **usage** block (`.ws-budget`).

With enough cards the usage block leaves the viewport. It is the one part of the panel that is not a list of things to work through: it is a standing readout, and a standing readout that has to be scrolled to is one nobody reads.

## Expected

The usage block is anchored to the bottom of the panel and always visible. The cards above it scroll.

## Actual

Everything scrolls together, so the readout is the first thing to disappear precisely when there is most going on — the moment its number is most worth seeing.

## Evidence

- `desktop/src/renderer/renderer.css:3223` — `.ws-attention { max-height: 45%; overflow-y: auto; }`, one container for all four regions.
- `desktop/src/renderer/renderer.ts` `paintAttention()` — appends head, rows, the finished-today button and `buildBudgetBlock()` as siblings into that same scrolling element.
- `renderer.css:3345` — `.ws-budget` has no `flex` of its own, so it is simply the last child in the scroll flow.

## Fix shape

Split the panel: an inner region that scrolls (`flex: 1 1 auto; min-height: 0; overflow-y: auto`) for the heading, the cards and the footer, with `.ws-budget` as a sibling outside it at `flex: none`. The outer panel stops scrolling and becomes the frame.

`min-height: 0` is the part that is easy to omit and silently breaks it: a flex child defaults to `min-height: auto`, which refuses to shrink below its content, and the inner region would grow instead of scrolling.

## Fixed — 2026-08-13

The panel is a frame; a `.ws-attention-scroll` region inside it holds the heading, the cards and the finished-today footer, and `.ws-budget` sits outside that region at `flex: none`.

`min-height: 0` on the scroll region is the load-bearing line, and it is written down in the CSS rather than left as folklore: a flex child defaults to `min-height: auto` and refuses to shrink below its content, so without it the region grows the panel instead of scrolling inside it.

Verified in the running app: the scroll region exists and `.ws-budget` is a direct child of the panel rather than of the scroller.
