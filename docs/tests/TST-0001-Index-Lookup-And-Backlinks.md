---
type: "[[test]]"
id: TST-0001
aliases: ["TST-0001"]
title: "Index — lookup tables, link graph, invalidation"
status: passing
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
source: []
scope: "system"
kind: "automated"
level: "unit"
entrypoint: "tests/test_index.py"
verifies: ["[[REQ-0002]]", "[[REQ-0008]]"]
artifacts: []
evidence: ["12 passed in 0.06s (2026-05-08)"]
last_run: "2026-05-08"
related: ["[[TASK-0007]]", "[[FEAT-0006]]"]
---

# TST-0001 — Index lookup + backlink graph + invalidation

## Scope
Unit tests for `project_os_cockpit.index.Index`. Validates the in-memory data layer that every other feature builds on:

- Wikilink resolution via the priority order (`id` → aliases → filename → title), implementing [[REQ-0002]].
- Outbound link extraction from BOTH frontmatter values and body markdown.
- Inbound (backlink) graph as the reverse of outbound — the data backing FEAT-0004's [[REQ-0008]] backlinks panel and FEAT-0006's CONTEXT pane.
- `Index.invalidate(path)` semantics for edit / delete / re-create, including the design decision that `_inbound[deleted_path]` is preserved (sources still claim to link there).

## How to run
```bash
.venv/bin/python -m pytest tests/test_index.py -v
```

12 test cases, runs in <100 ms against a static fixture under `tests/fixtures/index_basic/`.

## Coverage map
| Test | Validates |
|---|---|
| `test_build_indexes_real_notes_only` | `Index.build`, `type_counts` excludes templates |
| `test_get_returns_note_record` | `NoteRecord` shape (id, aliases, type, status, body) |
| `test_by_id_resolves_via_priority_order` | Lookup priority + fallthrough to None |
| `test_resolve_returns_url` | URL projection of `by_id` |
| `test_links_from_includes_body_and_frontmatter` | Outbound graph from both sources |
| `test_links_to_is_reverse_of_links_from` | Inbound is the mirror of outbound |
| `test_unresolved_wikilink_does_not_raise` | DoD: unresolved links are skipped, not raised |
| `test_self_links_excluded` | A note never links to itself |
| `test_invalidate_after_edit_updates_links` | Edit re-discovers outbound links |
| `test_invalidate_after_delete_removes_record` | Delete drops record + mirrors, preserves inbound from sources |
| `test_invalidate_after_recreate_re_indexes` | New file picked up; backlinks rebuilt |
| `test_paths_includes_template_notes_for_resolution` | Templates indexed for `[[feature]]` resolution |

## Last result
2026-05-08 — 12 passed in 0.06s.
