---
type: "[[change]]"
id: CHG-20260508-Cockpit-Json-Api
aliases: ["CHG-20260508-Cockpit-Json-Api"]
title: "Cockpit JSON API: /api/cockpit/{nav,context}"
status: merged
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
source: ["[[TASK-0012]]"]
commit: ""
pr: ""
impacts:
  - "src/docs_server/cockpit.py"
  - "src/docs_server/server.py"
  - "tests/test_cockpit.py"
  - "tests/fixtures/index_basic/"
  - "docs/tests/TST-0002-Cockpit-Json-Api.md"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[REQ-0013]]", "[[ADR-0004]]", "[[TST-0002]]", "[[TASK-0013]]"]
---

# Cockpit JSON API online

## Summary
Two new endpoints — `/api/cockpit/nav` and `/api/cockpit/context` — emit the data shape the JS client (landing in TASK-0013) will consume to render the cockpit's left and right panes. Pure-function payload builders in a new `cockpit.py` module; thin route handlers in `server.py`. Schema-versioned via an `X-Cockpit-Schema` response header so the client can detect bumps.

## Impact

### New URLs
- `GET /api/cockpit/nav` — features-by-phase. Returns `{ schema_version, groups: [{ phase_id, phase_title, phase_url, items: [{id, title, status, goal, url}] }] }`.
- `GET /api/cockpit/context?this=<note-id-or-path>` — relationships of an active note. Returns `{ schema_version, active, linked, backlinks }` where each of `linked` / `backlinks` is `[{type, items: [{id, title, status, priority, url}]}]`.

`this` accepts either an id/alias (`FEAT-0001`) or a docs-root-relative path (`FEAT-0001-Alpha.md` or `/docs/FEAT-0001-Alpha.md`) — both forms resolve. Missing or unresolvable `this` returns `{active: null, linked: [], backlinks: []}` with status 200.

### Architecture
- `src/docs_server/cockpit.py` — pure payload builders. `nav_payload(index)` and `context_payload(index, this)` take an `Index` and return dicts; HTTP plumbing lives in `server.py`. Lets unit tests assert at the dict level — no test-server spin-up needed.
- `src/docs_server/server.py` — `_serve_cockpit_nav` / `_serve_cockpit_context` handlers (thin) + a `_respond_json` helper that auto-sets `X-Cockpit-Schema`.

### Data shape decisions
- **Right-pane type order**: `TYPE_ORDER` tuple (feature → task → requirement → issue → risk → adr → change → release → workflow → test → phase → plan → dashboard). Types outside the list land alphabetically at the end. Stable order so the client doesn't need to sort.
- **Phase order**: phases sort by their `order` frontmatter (1, 2, 3...); phases without `order` go last.
- **Items within a group**: sorted by `id` (then `rel_path` as tiebreaker) for determinism.
- **Templates excluded**: notes under `__templates__/` are filtered out of both endpoints (placeholder IDs would pollute the cockpit). They remain indexed for wikilink resolution as before.
- **Inbound-only logic**: `backlinks = links_to(active) - links_from(active)` — the right pane never duplicates a note across its two sections. Verified by `test_context_payload_backlinks_excludes_already_linked`.

### Testing
- **TST-0002** — 13 unit tests in `tests/test_cockpit.py`, all passing in <100 ms.
- Fixture `tests/fixtures/index_basic/` extended with a phase note (`PHASE-001-Foundation.md`) and an inbound-only change (`CHG-20260508-Inbound.md`) that references FEAT-0001 without a back-reference. Existing TST-0001 tests still pass against the extended fixture.
- Verified against this repo's `docs/`: `/api/cockpit/nav` returns 4 phase groups; `/api/cockpit/context?this=FEAT-0001` returns 6 outbound items + 15 inbound-only items, zero overlap.

## Follow-ups
- [ ] [[TASK-0013]] — cockpit shell + `cockpit.js` consumes both endpoints to render the panes.
- [ ] [[TASK-0014]] — SSE-driven re-fetch; layered on top of TASK-0013.
- [ ] If a future use case emerges where the cockpit needs more right-pane columns (e.g. `phase`, `effort`), extend `_context_item` and bump `SCHEMA_VERSION` to v2; the `X-Cockpit-Schema` header lets the client refuse to render an unknown shape.
