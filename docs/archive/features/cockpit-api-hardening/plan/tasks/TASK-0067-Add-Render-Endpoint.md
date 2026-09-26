---
type: "[[task]]"
id: TASK-0067
aliases: ["TASK-0067"]
title: "Add GET /api/render — rendered Markdown HTML fragment for the native centre pane"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0008"
effort: ""
due: ""
depends: []
blocks: ["[[FEAT-0011-Native-Center-Pane]]"]
related: []
tests: []
---

# Add `GET /api/render`

## Definition of Done
- [ ] `GET /api/render?path=<rel-path>` returns JSON:
      `{ok, rel_path, title, frontmatter, html, outbound, inbound}`.
- [ ] `rel_path` is docs-root-relative (e.g.
      `features/cockpit/FEAT-0006-Cockpit-Layout.md`); leading
      `docs/` is tolerated and stripped.
- [ ] Reuses `renderer.render_markdown_body()` so HTML output
      matches what mode-1 pages contain in their `<article>`.
- [ ] `outbound` + `inbound` populated from `cockpit.context_payload()`.
- [ ] Path traversal guarded (no `..`); resolved path must stay
      under the docs root.
- [ ] 404 when the path doesn't resolve to a `.md` file.
- [ ] 200 response carries `X-Cockpit-Schema` header.
- [ ] HTTP-level regression test covering: happy path, 404, traversal
      rejection.
- [ ] TST-* note documenting the test under
      `docs/features/cockpit-api-hardening/plan/tests/`.

## Steps
- [ ] Add the route in `server.py` next to the existing cockpit JSON
      handlers; helper `_serve_render(rel_path)` mirrors
      `_serve_cockpit_context` shape.
- [ ] Decode + normalise `rel_path`; strip leading `docs/`; reject
      traversal.
- [ ] Resolve the index record (for `frontmatter`); call
      `renderer.render_markdown_body()` for `html`; call
      `cockpit.context_payload()` for `outbound` + `inbound`.
- [ ] Add to `docs/references/COCKPIT-API.md` (depends on TASK-0066).
- [ ] Add `tests/test_render_endpoint.py` with the three cases.

## Notes
URL shape decision: `GET /api/render?path=…` over
`GET /api/render/<path>` — query-string keeps slash-heavy paths
clean and matches the convention of `/api/cockpit/context?this=…`.
