---
type: "[[issue]]"
id: ISS-0048
aliases: ["ISS-0048"]
title: "Token values were interpolated into markup, and every token was assumed to be a colour"
status: fixed
severity: medium
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["user report 2026-07-28: 'icon-folder and icon-file do not render correctly, could be a xml/html format issue?'"]
related: ["[[TASK-0228-Living-Style-Guide]]", "[[DES-0002-Cockpit-Design-System]]"]
fixed_by: []
---

# A stylesheet value is data, not markup

Edwin: *"in the palette section, the icon-folder and icon-file do not render correctly, could be a xml/html format issue?"* — exactly right.

## Two defects, one symptom

**1. Values were concatenated into `innerHTML`.**

```js
'<div class="sw"><i style="background:' + v + '">…'
```

`--icon-folder` holds `url("data:image/svg+xml;utf8,<svg …>")`. The `"` closed the `style` attribute and the `<svg>` was parsed as markup. Measured in the app: **16 stray elements** inside the palette, and the row's own text reading `")">--icon-folderurl("data:image/svg+xml;utf8,")`.

The page reads values out of a stylesheet — that is the point of it — and **a value read from a stylesheet is data.** Interpolating it into markup was the mistake, and it would have been a script-injection bug in any page whose stylesheets were less trustworthy than its own.

**2. Every non-status token was assumed to be a colour.**

`--icon-folder` and `--icon-file` are `url()` assets used as `mask-image`; `--shadow-soft` is a shadow triple. Painting them as `background` and printing the raw value said nothing and dumped hundreds of characters of data URI into a value column.

## Fix

- **Built with DOM APIs.** `createElement`, `textContent`, `style.setProperty` — no value ever reaches an HTML parser.
- **Classified by value.** `url(…)` is an asset, previewed the way the app uses it (`mask-image` in the current ink colour); a shadow triple is previewed as a `box-shadow`; everything else is a colour. The value column shows `url(data:image/svg+xml …)` with the full text on hover.

Verified in the Electron app: **0 stray elements** (was 16), both icons rendering as glyphs, both shadow tokens previewing as shadows, 106 swatches intact.
