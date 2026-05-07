---
type: "[[task]]"
id: TASK-0012
aliases: ["TASK-0012"]
title: "Cockpit JSON API (features-by-phase + links/backlinks)"
status: next
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
source: []
implements: ["[[FEAT-0006]]", "[[REQ-0013]]"]
fixes: []
effort: S
due: ""
depends: [TASK-0007]
blocks: [TASK-0013]
related: ["[[ADR-0004]]"]
tests: []
---

# Cockpit JSON API

## Definition of Done
- [ ] `GET /api/cockpit/nav` returns the left-pane payload — every feature note grouped by phase, with `id` / `title` / `status` / `goal` per row plus the phase note's URL for the group header link.
- [ ] `GET /api/cockpit/context?this=<note-id-or-rel-path>` returns the right-pane payload for the given active note: `linked` (outbound) + `backlinks` (inbound minus outbound), each section a list of `{type, items}` groups; every item carries `id` / `title` / `status` / `priority` / `url`.
- [ ] When `this` is missing or unresolvable, `/api/cockpit/context` returns 200 with empty `linked` and `backlinks` lists (no error).
- [ ] Both endpoints set `Content-Type: application/json; charset=utf-8` and an `X-Cockpit-Schema: 1` header so the JS client can detect schema bumps.
- [ ] Unit tests covering: the nav payload includes every non-template feature grouped by their `phase` value; the context payload's `backlinks` excludes any item already in `linked`; templates are excluded; an unknown `this` yields empty lists.

## Steps
- [ ] Add `Index.features_by_phase()` (or equivalent helper) that returns a stable-sorted `dict[phase_label, list[NoteRecord]]` for every non-template `type: feature` note.
- [ ] Add `/api/cockpit/nav` and `/api/cockpit/context` route handlers in `server.py` next to the existing `/index/<plural>` and SSE handlers.
- [ ] JSON serialiser: `{id, title, status, priority, url}` for items; phase headers carry the resolved phase note URL via `Index.by_id`.
- [ ] Plug into the existing path-traversal and case-folding helpers from `events.py` for any incoming path-shaped `this` parameter.
- [ ] Tests in `tests/test_cockpit_api.py` against an extended fixture (a feature with outbound + inbound + a unique-inbound case).

## Notes
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
