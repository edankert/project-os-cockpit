---
type: "[[test]]"
id: TST-0002
aliases: ["TST-0002"]
title: "Cockpit JSON API — nav + context payloads"
status: passing
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
source: []
scope: "system"
kind: "automated"
level: "unit"
entrypoint: "tests/test_cockpit.py"
validates: ["[[REQ-0013]]"]
artifacts: []
evidence: ["13 passed in 0.06s (2026-05-08)"]
last_run: "2026-05-08"
related: ["[[TASK-0012]]", "[[FEAT-0006]]"]
---

# TST-0002 — Cockpit JSON API

## Scope
Unit tests for `project_os_cockpit.cockpit.nav_payload` and `project_os_cockpit.cockpit.context_payload`. Validates the data contract the JS client (TASK-0013) consumes:

- `nav_payload` groups every non-template feature by its `phase` frontmatter, sorted by phase `order`, items sorted by `id`. Item shape: `{id, title, status, goal, url}`.
- `context_payload` resolves an active note (by id or by relative path), then returns:
  - `linked` — outbound links from the active note, grouped by type.
  - `backlinks` — inbound links MINUS outbound (the "inbound-only" set), grouped by type.
- Item shape on the context endpoint: `{id, title, status, priority, url}`.
- Unknown / missing `this` returns an empty payload (`active: null`, empty lists).
- Templates excluded from both endpoints' item lists.

## How to run
```bash
.venv/bin/python -m pytest tests/test_cockpit.py -v
```

13 test cases, runs in ~60 ms against the same `tests/fixtures/index_basic/` fixture used by TST-0001 (extended with a phase note and an inbound-only change).

## Coverage map
| Test | Validates |
|---|---|
| `test_nav_payload_schema_versioned` | `schema_version: 1` present |
| `test_nav_payload_groups_features_by_phase` | Phase grouping + phase metadata |
| `test_nav_payload_item_shape` | `{id, title, status, goal, url}` per row |
| `test_nav_payload_excludes_template_features` | Template `FEAT-0000` not present |
| `test_context_payload_unknown_note_is_empty` | Unknown `this` → empty payload |
| `test_context_payload_missing_this_is_empty` | `this=None` → empty payload |
| `test_context_payload_resolves_by_id` | `this=FEAT-0001` → resolved active block |
| `test_context_payload_linked_grouped_by_type` | Outbound type grouping |
| `test_context_payload_excludes_templates_from_linked` | Template excluded from outbound |
| `test_context_payload_backlinks_excludes_already_linked` | Inbound-only exclusion (the "minus outbound" rule) |
| `test_context_payload_inbound_only_change_appears` | Inbound-only items appear in `backlinks`, not `linked` |
| `test_context_payload_item_columns` | `{id, title, status, priority, url}` per item |
| `test_context_payload_resolves_by_path` | `this` accepts path-style + URL-prefixed forms |

## Last result
2026-05-08 — 13 passed in 0.06s.
