---
type: "[[issue]]"
id: ISS-0045
aliases: ["ISS-0045"]
title: "The viewport chooser appears on documents, which have no device width"
status: fixed
severity: low
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["user report 2026-07-28"]
related: ["[[TASK-0215-Design-Render-Surface]]", "[[DES-0002-Cockpit-Design-System]]"]
fixed_by: []
---

# Chrome for a case the corpus does not have

Edwin: *"why do we have these options on top if all we show is just a page with artefacts ... the page should always just show the page"*

## He is right, and it goes further than the buttons

`viewport:` **absence already means "this is a document, let it flow"** — that rule shapes the width, the height, and the framing. The *chrome* was never told. So a document rendered with a five-button viewport bar of which four were disabled, offering device widths for a page that has none.

Both designs in this corpus are documents. The bar was dead chrome on every design that exists.

## The deeper problem it exposed

[[DES-0002]] declared `viewport: 900` — and that was simply **wrong**. It was written before the page existed, recording the height [[REQ-0022]] asserts rather than a width the artifact is drawn at. That single wrong field is what put a scrolling reference page inside a 900px window, made the stage a second scroller ([[ISS-0044]]), and turned on the viewport chooser.

A declaration that means "I am a surface" was carrying a number that meant something else entirely.

## Fix

- The viewport chooser renders **only** when the design declares a viewport — the same rule the frame already follows, applied to the chrome.
- DES-0002 declares no viewport. It is a document and now renders as one: full width, its own scrolling, no framing, no chooser. The page simply shown.

A genuine surface mock — a 420px phone screen — still frames and still gets its chooser. That case is worth keeping; it just is not the case anything in this repo actually has yet.
