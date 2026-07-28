---
type: "[[issue]]"
id: ISS-0039
aliases: ["ISS-0039"]
title: "Scrollbars inside scrollbars on the design surface; the declared preset ignores an absent viewport"
status: fixed
severity: medium
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["user report 2026-07-28 while reviewing the design surface"]
related: ["[[FEAT-0042-Design-Bench]]", "[[ISS-0038-Unframed-Design-Stage-Renders-Narrow]]"]
fixed_by: []
---

# Scrollbars inside scrollbars

## What Edwin saw

"This is causing too many scroll-bars inside scroll-bars."

## What is actually stacked

```
.doc-view.design-page   overflow: auto          <- scrollbar 1 (the page)
  .design-view                                     (no styles at all)
    .design-body        display: flex
      .design-stage     display: flex
        iframe          height: 900px  <- forced  <- scrollbar 2 (the artifact)
```

Three in compare mode, where two stages each carry a frame.

## The defect underneath

The `declared` preset honours an absent `viewport:` for **width** and ignores it for **height**:

- `width = preset.key === 'declared' ? d.viewport : preset.w` — absent viewport, full width. Correct.
- `{ key: 'declared', h: 900 }` — 900px tall regardless.

`viewport:` absence means "this is a document, let it scroll" — the rule this whole feature was built on, contradicted one line below where it is implemented. DES-0001 declares no viewport, is the scrolling dossier, and is the **only design in the repo with an artifact** — so the single thing that can be opened is exactly the case that should never have been given a fixed window.

Found while measuring: the `Fill` preset sets `w: null, h: null`, so no height is applied and `.design-frame { min-height: 320px }` wins. **Fill renders a 320px box and fills nothing.**

## Why the obvious fix is unavailable

Auto-sizing an iframe to its content needs `contentDocument`. The sandbox denies it — `allow-scripts` without `allow-same-origin`, deliberately, and `test_frame_allows_scripts_but_nothing_else` asserts it. Granting both would let a sandboxed frame remove its own sandbox. So a document artifact either takes a fixed height, or the page hands it all the height there is.

## Decision (Edwin, 2026-07-28): app-shell

The page stops scrolling. Header and viewport bar pin to the top; the stage takes all remaining height; the iframe fills it. Revisions and rationale move to a right-hand column that scrolls independently. One scrollbar for the artifact, one for the sidebar, never nested.

Rejected alternatives, with reasons:

- **Honour absence and keep the page scrolling** — reduces nesting without removing it; a long dossier still gets an inner scrollbar inside a scrolling page.
- **Pop the artifact into its own window** — an escape from the embedded view rather than a fix to it. Worth having later as a complement; not the answer to this.
