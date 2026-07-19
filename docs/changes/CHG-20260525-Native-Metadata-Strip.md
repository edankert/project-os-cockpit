---
type: "[[change]]"
id: CHG-20260525-Native-Metadata-Strip
aliases: ["CHG-20260525-Native-Metadata-Strip"]
title: "Native centre: server-rendered metadata strip, base.css copied, grid-child sizing fix"
status: merged
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0075]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/server.py (+metadata_html field via templates._metadata_strip_html)"
  - "tests/test_render_endpoint.py (+wikilink/bare-ID resolution test)"
  - "desktop/scripts/copy-assets.mjs (also copies base.css)"
  - "desktop/src/renderer/index.html (loads base.css; cockpit-centre class on doc-view)"
  - "desktop/src/renderer/renderer.ts (drops hand-built frontmatter card; data-theme bridge)"
  - "desktop/src/renderer/renderer.css (body block override; min-height: 0 on grid children)"
  - "docs/references/COCKPIT-API.md (documents metadata_html field)"
issues: []
features: ["[[FEAT-0011-Native-Center-Pane]]"]
related: ["[[CHG-20260525-Native-Center-Pane]]", "[[FEAT-0008-Cockpit-API-Hardening]]"]
---

# Native metadata strip + base.css bridge

## Summary

Closes FEAT-0011. The native centre pane now renders the same metadata
strip mode 1 emits — wikilinks (`[[FEAT-XXXX]]`) **and** bare project-os
IDs in frontmatter become clickable anchors, status renders as a chip,
lists comma-separate. Server-side resolution stays the single source of
truth; the renderer just mounts the HTML.

Test count: **130 → 131** (+1 covering both link forms).

## What landed

### Server (`server.py`)
- `_serve_render` now calls `templates._metadata_strip_html(frontmatter,
  resolver=index.resolve)` and returns the resulting HTML as a new
  `metadata_html` response field. Passes the raw (un-`_jsonable`-ified)
  frontmatter so YAML date/list values reach the renderer with their
  original types, matching the contract `_metadata_strip_html` expects.
- New test `test_render_metadata_resolves_wikilinks_and_bare_ids`
  asserts that `[[FEAT-0042]]` AND a bare `TASK-0099` reference both
  end up as `<a href="/docs/...">` in the response.

### Renderer (`desktop/`)
- `copy-assets.mjs`: also copies `src/project_os_cockpit/static/base.css`
  → `dist/renderer/base.css`. Single source of truth; both modes use
  the same CSS file at runtime.
- `index.html`: loads `base.css` before `cockpit.css` before
  `renderer.css` (variables → cockpit chrome → native overrides). Adds
  `cockpit-centre` class to `<article id="doc-view">` so the
  metadata-strip styles in cockpit.css apply.
- `renderer.ts`: deleted `renderFrontmatterCard`,
  `formatMetaValue`, `formatMetaScalar`, `PRIMARY_META_KEYS` (~90 lines
  net delete). The mount is now
  `docView.innerHTML = metadata_html + body_html + browse_html`.
  New `applySystemTheme()` sets `<html data-theme="dark|light">` so
  base.css's dark palette activates with OS preference.

### Layout fix (regression from base.css)
- base.css's `body { display: flex; flex-direction: column; height:
  100dvh; overflow: hidden }` collided with the native shell's `.app`
  grid root. Overridden in `renderer.css` with `body { display: block;
  overflow: hidden }`.
- The classic CSS-grid trap: grid children default to `min-height:
  auto`, refusing to shrink below their content. With a long mounted
  doc this pushed the switcher footer (where the Terminal toggle
  lives) and the centre pane below the viewport, breaking inner scroll.
  Fix: `min-height: 0; overflow: hidden` on both `.switcher` and
  `.stage`.

## Documentation Coverage
- features: covered (FEAT-0011 → `done`)
- requirements: not-applicable
- tasks: TASK-0070..0075 status → `done` (all six verified live)
- issues: not-applicable
- tests: TST-0005 / TST-0006 / TST-0007 / TST-0008 all passing;
  test_render_endpoint.py extended (+1 case)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (FEAT-0011 → done, tasks_done 65 → 75,
  features_done 3 → 4, test_cases 130 → 131, focus cleared)
