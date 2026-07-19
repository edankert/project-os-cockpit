---
type: "[[task]]"
id: TASK-0099
aliases: ["TASK-0099"]
title: "Port item-render conventions from cockpit.js to renderer.ts (full)"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0014"
related: ["[[TASK-0083]]", "[[TASK-0085]]"]
tests: []
---

# Item-render port

## Definition of Done
- [x] Four layout variants in TS: `stacked`, `compact`, `nested`,
      `nested-children`. Picked per-group via `group.item_layout`.
- [x] Type icons on items: `.type-icon[data-type="feature"|...]`
      with the same colour tokens used in the Python cockpit.
- [x] Group icons in section headers.
- [x] Status chips: same colour tokens as the Python cockpit
      (driven by cockpit.css already loaded in the renderer).
- [x] Subtitle row when applicable.
- [x] Right pane uses the same `navItem` so linked + backlinks
      rows match nav rows.
- [x] Local one-off renderers in `renderer.ts` removed.

## Implementation
Key realisation: cockpit.css is already loaded into the renderer
(copy-assets.mjs ships `base.css` + `cockpit.css` to dist/renderer).
So no CSS lift was needed — only the TS side. The renderer emits
the same DOM cockpit.js does (`.nav-item`, `.nav-item-stacked`,
`.nav-item-compact`, `.nav-item-nested`, `.nav-item-children`,
`.type-icon[data-type]`, `.group-icon[data-status|data-severity]`,
`.status-chip[data-status]`), and the existing cockpit.css selectors
style it. Saved ~150 lines of CSS that would have drifted.

## Notes
CSS port is selector-targeted, not a whole-file copy: only the
classes the new TS renderer emits. Tokens come from `base.css`
(already shared between Python and Electron). Selectors to lift:

- `.nav-item`, `.nav-item-stacked`, `.nav-item-compact`,
  `.nav-item-nested`, `.nav-item-children*`
- `.type-icon[data-type=...]`
- `.group-icon[data-type=...]`
- `.status-chip[data-status=...]`
- `.nav-title-*`, `.nav-meta`, `.nav-subtitle`

`pickItemRenderer` reads `group.item_layout`; the server already
emits this field, so no Python-side change is needed.
