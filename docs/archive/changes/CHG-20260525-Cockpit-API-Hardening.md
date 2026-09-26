---
type: "[[change]]"
id: CHG-20260525-Cockpit-API-Hardening
aliases: ["CHG-20260525-Cockpit-API-Hardening"]
title: "Cockpit API hardening: contract doc, GET /api/render, schema-header coverage, wire-level focus/tab-state/SSE tests"
status: merged
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0066]]", "[[TASK-0067]]", "[[TASK-0068]]", "[[TASK-0069]]"]
commit: ""
pr: ""
impacts:
  - "docs/references/COCKPIT-API.md (new)"
  - "src/project_os_cockpit/server.py (+ /api/render route, _jsonable helper)"
  - "src/project_os_cockpit/index.py (FileEvent type guard in _on_event)"
  - "tests/test_render_endpoint.py (new — 7 tests)"
  - "tests/test_schema_header.py (new — 17 tests)"
  - "tests/test_focus_and_tab_state.py (new — 9 tests)"
  - "docs/features/cockpit-api-hardening/plan/tests/TST-0005-Render-Endpoint.md (new)"
  - "docs/features/cockpit-api-hardening/plan/tests/TST-0006-Schema-Header.md (new)"
  - "docs/features/cockpit-api-hardening/plan/tests/TST-0007-Focus-Tab-State-SSE.md (new)"
issues: []
features: ["[[FEAT-0008-Cockpit-API-Hardening]]"]
related: ["[[PHASE-006-Native-Cockpit-UI]]", "[[FEAT-0011-Native-Center-Pane]]"]
---

# Cockpit API hardening

## Summary

FEAT-0008 done. The Python cockpit's HTTP surface now has a written
contract (`docs/references/COCKPIT-API.md`), a new
`GET /api/render?path=<rel>` endpoint that returns the rendered
Markdown HTML fragment + metadata, a schema-versioning rule plus an
HTTP-level test that gates every JSON endpoint on its
`X-Cockpit-Schema` header, and wire-level tests for the
focus / tab-state POST endpoints and the SSE event envelopes.

Test count: **88 → 120** (+33 tests). Three new TST notes.

Mode 1 unaffected: no breaking changes; `/api/render` is purely
additive.

## What landed

### TASK-0066 — Contract doc
`docs/references/COCKPIT-API.md`. Inventories every JSON endpoint,
the SSE channel, the `/healthz` probe, the terminal endpoint
(mode-dependent), the mode-1-only HTML routes, the `.cockpit/url`
discovery file. Records the schema-versioning rule at the top.

### TASK-0067 — `GET /api/render?path=<rel-path>`
New endpoint returning `{schema_version, rel_path, title,
frontmatter, html, linked, backlinks}`. Reuses
`renderer.render_markdown_body()` so the HTML output matches the
mode-1 `<article>` body, and `cockpit.context_payload()` so the
linked/backlinks columns fill in the same fetch. Path traversal
guarded; `docs/` leading-segment tolerated. New `_jsonable` helper
coerces YAML-parsed dates in frontmatter to strings before
JSON-serialisation.

### TASK-0068 — Schema versioning rule + header coverage
The rule is documented in the contract doc: any non-additive change
bumps `cockpit.SCHEMA_VERSION` and clients refuse to render when
their cached schema disagrees with the `X-Cockpit-Schema` header.
`tests/test_schema_header.py` parametrises across every JSON
endpoint (including 4xx error responses — the renderer reads the
header before parsing the body) and asserts the header is present
and matches the constant.

### TASK-0069 — Wire-level regression tests
`tests/test_focus_and_tab_state.py`:
- `POST /api/cockpit/focus` happy path, missing target (400),
  unresolvable target (404), state-snapshot agreement.
- `POST /api/cockpit/tab-state` happy path, missing fields (400),
  snapshot-tabs agreement.
- `GET /_events` SSE: `cockpit:focus` event after a focus POST;
  `file-changed` event after publishing a `FileEvent` on the
  server bus.

### Pre-existing bug, fixed
While running the SSE focus test, the suite surfaced a
long-standing bug: `Index._on_event` (the watcher subscriber)
assumed every event had `abs_path`. `cockpit:focus` events
(`ControlEvent` type) triggered an `AttributeError` that was
caught and logged by the EventBus's per-subscriber try/except —
hiding it. Fix: added an `isinstance(event, FileEvent)` guard at
the top of `_on_event`. The SSE focus test now exercises this
path and would fail if the bug regressed.

## Documentation Coverage
- features: covered (FEAT-0008 status → `done`)
- requirements: not-applicable
- tasks: TASK-0066, 0067, 0068, 0069 status → `done`
- issues: not-applicable
- tests: TST-0005, TST-0006, TST-0007 added (status `passing`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (FEAT-0008 → done, TASK-0066..69 → done,
  TST counter 4 → 7, metrics bumped, focus cleared from
  TASK-0066, tasks_done 61 → 65, tests_total 4 → 7,
  test_cases_total 86 → 119)
