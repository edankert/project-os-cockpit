---
type: "[[test]]"
id: TST-0005
aliases: ["TST-0005"]
title: "GET /api/render — HTML fragment + metadata, error shapes, path-traversal guard"
status: passing
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0067]]"]
verifies: ["[[TASK-0067]]", "[[FEAT-0008-Cockpit-API-Hardening]]"]
path: "tests/test_render_endpoint.py"
---

# TST-0005 — `GET /api/render` contract

## Intent
Locks the wire shape of `GET /api/render?path=<rel>` documented in
`docs/references/COCKPIT-API.md` so PHASE-006 / FEAT-0011 can build
the native centre pane against a stable contract.

Coverage:

1. **Happy path.** Renders a docs-rel `.md` file; response carries
   `schema_version`, `rel_path`, `title`, `frontmatter` (with date
   sanitised to a string), `html` (body content present, YAML block
   stripped), and `linked` / `backlinks` as arrays.
2. **`docs/` prefix tolerated.** `docs/foo/bar.md` and `foo/bar.md`
   both resolve; `rel_path` in the response is the normalised form.
3. **README without frontmatter.** Returns empty `frontmatter` dict,
   non-empty `title` derived from filename / H1.
4. **Missing `path` parameter → 400** with `{ok: false, error: ...}`.
5. **`..` segment → 403** with `{ok: false, error: "...traversal..."}`.
6. **Path resolves outside docs root → 403.** Covered by the same
   guard.
7. **Path doesn't resolve to a file → 404.**
8. **Path resolves to a non-`.md` file → 404** with reason
   mentioning "markdown".

## Location
`tests/test_render_endpoint.py` — 7 tests, all passing as of
2026-05-25. Uses the same `_NoDNSThreadingHTTPServer` ephemeral-port
pattern as `test_cockpit_state.py` / `test_sidecar_contract.py`.

## Status
`passing` — 7/7 (`pytest tests/test_render_endpoint.py -v`).
