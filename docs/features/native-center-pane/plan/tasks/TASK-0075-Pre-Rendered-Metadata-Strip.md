---
type: "[[task]]"
id: TASK-0075
aliases: ["TASK-0075"]
title: "Pre-rendered metadata_html field in /api/render"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0070]]"]
parent: "FEAT-0011"
effort: ""
due: ""
depends: ["[[TASK-0067]]"]
blocks: []
related: []
tests: []
---

# Pre-rendered metadata_html

## Definition of Done
- [ ] `GET /api/render` returns a new `metadata_html` field carrying
      the resolved metadata-strip HTML — produced by
      `templates._metadata_strip_html(frontmatter, resolver=index.resolve)`,
      identical to the strip mode 1 emits.
- [ ] Renderer drops the hand-built `renderFrontmatterCard`
      (+ `formatMetaValue`, `formatMetaScalar`, etc.); mounts
      `metadata_html + body_html + browse_html` instead.
- [ ] `<article id="doc-view">` gets a `cockpit-centre` class so the
      mode-1 `.metadata-strip` styling in cockpit.css applies.
- [ ] `tests/test_render_endpoint.py` extended: asserts
      `metadata_html` field present in the response; asserts that a
      `[[FEAT-XXXX]]` frontmatter reference resolves to an `<a>` tag
      with the right href; asserts a bare-ID reference (e.g.
      `parent: FEAT-XXXX`) also becomes an `<a>`.
- [ ] `docs/references/COCKPIT-API.md` adds the field to the
      `/api/render` response shape.

## Steps
- [ ] `server.py` — call `templates._metadata_strip_html(...)` inside
      `_serve_render`; pass `index.resolve` as the resolver. Add
      `metadata_html` to the response dict.
- [ ] `renderer.ts` — delete `renderFrontmatterCard`,
      `renderMetaRow`, `formatMetaValue`, `formatMetaScalar`, and
      `PRIMARY_META_KEYS`. Replace with
      `docView.innerHTML = data.metadata_html + data.html + browseHtml`.
      Add `cockpit-centre` class to the doc-view element in
      `index.html`.
- [ ] Update `test_render_endpoint.py` happy-path test to assert the
      new field; add a focused test for the
      `[[FEAT-XXXX]]` + bare-ID linking.
- [ ] Patch `docs/references/COCKPIT-API.md` `/api/render` section.

## Notes
Restores parity with mode 1: frontmatter wikilinks AND bare IDs
become clickable, status renders as a chip, lists comma-separated.
Same click-interception path as the body — the renderer's existing
`#doc-view` listener catches any `<a>` regardless of where it came
from in the mounted HTML.
