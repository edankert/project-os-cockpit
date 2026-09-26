---
type: "[[task]]"
id: TASK-0009
aliases: ["TASK-0009"]
title: ".base JSON API endpoint"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-23
source: []
parent: "[[FEAT-0006]]"
fixes: []
effort: S
due: ""
depends: ["[[TASK-0008]]"]
blocks: ["[[TASK-0010]]"]
related: []
tests: []
---

# .base JSON API endpoint

> **Closed as superseded (2026-05-23).** [[ADR-0004]] moved the cockpit off `.base` files; FEAT-0006's JSON layer is `/api/cockpit/nav` and `/api/cockpit/context` (see [[TASK-0012]]). Status flipped from `backlog` → `done` to clear the queue. The scoping below stays as scaffolding for a future `.base`-rendering feature if one is ever pursued.

## Definition of Done
- [ ] `GET /api/base?path=<rel-path-to-.base>&this=<note-id-or-path>` returns 200 with JSON.
- [ ] `path` is required and must resolve under the configured docs root (path-traversal guard: 400 on `..`).
- [ ] `this` is optional. When supplied, the evaluator's `this.file` binds to the resolved note path; when absent, it's null.
- [ ] Response shape (v1):
  ```json
  {
    "schema_version": 1,
    "base": { "path": "docs/__bases__/CONTEXT.base", "name": "CONTEXT" },
    "views": [
      {
        "name": "All",
        "groupBy": { "property": "type", "direction": "ASC" },
        "order": ["id", "formula.display_title", "status", "..."],
        "sort": [{ "property": "priority", "direction": "DESC" }, ...],
        "columnSize": { "formula.display_title": 307 },
        "rowHeight": "medium",
        "rows": [
          {
            "id": "FEAT-0001",
            "path": "docs/features/render-server/FEAT-0001-Render-Server.md",
            "fields": {
              "id": "FEAT-0001",
              "formula.display_title": { "kind": "link", "target": "...", "display": "..." },
              "status": "active",
              "...": "..."
            }
          }
        ]
      }
    ],
    "properties": { "id": { "displayName": "ID" }, "...": "..." }
  }
  ```
- [ ] `Content-Type: application/json; charset=utf-8`. Header `X-Base-Schema: 1` for client-side compatibility checks.
- [ ] Unknown base path → 404. Base file fails to parse → 422 with `{error, file, line, message}`.
- [ ] Wraps `Index` + `bases.parse` + `bases.evaluate` only — no business logic in the handler.
- [ ] Unit tests hit the endpoint against the fixture index and assert the JSON shape for NAV.base (no `this`) and CONTEXT.base (with `this=FEAT-0001`).

## Steps
- [ ] Add a route to `docs_server.server` (the route table itself becomes real in TASK-0010 of FEAT-0001 / cockpit, whichever lands first — coordinate).
- [ ] Implement the JSON serialiser for `EvaluatedBase`: scalars pass through; typed-links become `{kind: "link", target, display}`; dates ISO-8601; missing fields omitted (not nulled).
- [ ] Add the path-traversal guard (reuse FEAT-0001's helper if it exists by then).
- [ ] Add the schema-version header.
- [ ] Write the unit tests.

## Notes
The schema version exists so the JS client (TASK-0010) can warn if the server is newer than it expects. v1 is a frozen contract; bump the version whenever the row/view shape changes.

Deliberately *not* HTML — keeping rendering responsibility client-side per the architecture decision noted in FEAT-0006's plan. Future tasks (column-sort toggles, filter-as-you-type) will be JS-only changes against this contract.
