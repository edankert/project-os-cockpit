---
type: "[[task]]"
id: TASK-0012
aliases: ["TASK-0012"]
title: "Cockpit JSON API (features-by-phase + links/backlinks)"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
source: []
parent: "[[FEAT-0006]]"
fixes: []
effort: S
due: ""
depends: ["[[TASK-0007]]"]
blocks: ["[[TASK-0013]]"]
related: ["[[ADR-0004]]"]
tests: ["[[TST-0002]]"]
---

# Cockpit JSON API

## Definition of Done
- [x] `GET /api/cockpit/nav` returns features grouped by phase with `id` / `title` / `status` / `goal` per row + phase metadata (`phase_id`, `phase_title`, `phase_url`).
- [x] `GET /api/cockpit/context?this=<note-id-or-rel-path>` returns `linked` (outbound) + `backlinks` (inbound minus outbound), each grouped by `type`, with `id` / `title` / `status` / `priority` / `url` per item.
- [x] Missing or unresolvable `this` returns 200 with `active: null` + empty lists — no exception.
- [x] Both endpoints set `Content-Type: application/json; charset=utf-8` and `X-Cockpit-Schema: 1`.
- [x] 13 unit tests in `tests/test_cockpit.py` ([[TST-0002]]) cover both endpoints' shape, type-grouping, the inbound-only exclusion logic, template filtering, the `this`-by-id and `this`-by-path resolution paths, and the empty-payload contract. All passing in <100 ms.

## Steps
- [x] Built `src/docs_server/cockpit.py` with pure functions `nav_payload(index)` and `context_payload(index, this)`. Pure-function shape keeps the unit tests at the dict level, no HTTP plumbing.
- [x] Added route handlers `_serve_cockpit_nav` and `_serve_cockpit_context` in `server.py` next to the existing `/index/<plural>` and `/_events` routes.
- [x] Added `_respond_json(payload, status)` helper next to `_respond_html`. Sets `X-Cockpit-Schema` automatically; clients can detect schema bumps without parsing the body.
- [x] `_resolve_this` accepts both id/alias forms (`FEAT-0001`) and path forms (`FEAT-0001-Alpha.md`, `/docs/FEAT-0001-Alpha.md`) — the JS client can hand over either.
- [x] Phase grouping uses the `order` frontmatter field for predictable sequencing; phases without `order` land at the end. Items within a phase sort by `id`.
- [x] Right-pane type ordering uses the `TYPE_ORDER` tuple in `cockpit.py` (feature → task → requirement → … → plan → dashboard); types outside that list go alphabetically at the end.
- [x] Templates under `__templates__/` are filtered out of both endpoints' lists (so `FEAT-0000`, `TASK-0000`, etc. don't pollute the cockpit).

## Notes
**Verified against this repo's `docs/`:** `/api/cockpit/nav` returns 4 phase groups (PHASE-001 / 002 / 003 / 004) with the right features under each; `/api/cockpit/context?this=FEAT-0001` returns 6 outbound items (1 requirement, 4 changes, 1 phase) and 15 inbound-only items (5 tasks, 5 requirements, 2 risks, 2 ADRs, 1 change) with zero overlap.

**Schema (v1):**

```json
// GET /api/cockpit/nav
{
  "schema_version": 1,
  "groups": [
    {
      "phase_id": "PHASE-001",
      "phase_title": "MVP",
      "phase_url": "/docs/phases/PHASE-001-MVP.md",
      "items": [
        {
          "id": "FEAT-0001",
          "title": "Markdown render server (frontmatter + wikilinks + on-the-fly)",
          "status": "done",
          "goal": "Render any .md note ...",
          "url": "/docs/features/render-server/FEAT-0001-Render-Server.md"
        }
      ]
    }
  ]
}
```

```json
// GET /api/cockpit/context?this=FEAT-0001
{
  "schema_version": 1,
  "active": {
    "id": "FEAT-0001",
    "url": "/docs/features/render-server/FEAT-0001-Render-Server.md"
  },
  "linked": [
    { "type": "task", "items": [{ "id": "...", "title": "...", "status": "...", "priority": null, "url": "..." }] },
    { "type": "change", "items": [...] }
  ],
  "backlinks": [
    { "type": "requirement", "items": [...] }
  ]
}
```

`priority` is `null` for any note type that doesn't carry one (only requirements use it today). Status is the lowercase-normalised value the index already stores.

The schema-version + header convention mirrors what the deferred TASK-0009 (`.base` API) was going to do — same forward-compat story.

This task lands the data layer; TASK-0013 builds the UI; TASK-0014 wires SSE re-fetch.
