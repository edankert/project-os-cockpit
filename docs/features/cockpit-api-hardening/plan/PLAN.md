---
type: "[[plan]]"
id: PLAN-FEAT-0008
aliases: ["PLAN-FEAT-0008"]
title: "Plan: Cockpit API hardening (Python side) for the native renderer"
status: active
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
implements: ["[[FEAT-0008-Cockpit-API-Hardening]]"]
related: ["[[PHASE-006-Native-Cockpit-UI]]", "[[FEAT-0011-Native-Center-Pane]]"]
---

# Plan — FEAT-0008 Cockpit API hardening

## Delivery sequence

1. **[[TASK-0066]] — Document the existing API contract.**
   Write `docs/references/COCKPIT-API.md`. Inventory every endpoint
   the Python cockpit exposes, with request shape, response shape,
   headers (`X-Cockpit-Schema`), and which client(s) consume it
   (mode 1 cockpit.js / mode 3 TS renderer / `cockpit` CLI). This
   doc is the contract; PHASE-006 evolves the renderer against it.

2. **[[TASK-0067]] — Add `GET /api/render/<rel-path>`.**
   New JSON endpoint returning the rendered Markdown HTML fragment
   plus the metadata FEAT-0011's centre pane needs. Reuses
   `renderer.render_markdown_body()` for HTML and
   `cockpit.context_payload()` for outbound/inbound links. Adds
   the endpoint to the contract doc; ships with a regression test.

3. **[[TASK-0068]] — Codify schema-versioning rule + header
   assertion test.** Document in the contract doc that any
   non-additive change to a JSON endpoint bumps
   `cockpit.SCHEMA_VERSION` and that both clients refuse to
   render when their cached schema disagrees with the server's
   header. Land an HTTP-level test that asserts every JSON
   endpoint emits `X-Cockpit-Schema` matching the constant.

4. **[[TASK-0069]] — Fill regression test gaps.** Audit
   `tests/` against the contract doc; for any endpoint without a
   passing regression test, add one. Focus areas (gaps suspected):
   POST `/api/cockpit/focus` response shape + resolved-URL
   correctness; POST `/api/cockpit/tab-state` tab pruning
   semantics; `/_events` SSE event shape for `cockpit:focus` and
   `file-changed`. Each new test gets a TST-* note.

## Dependencies
- **Hard:** none beyond what already ships. The existing endpoints
  are the substrate; this feature freezes their shape and adds one
  endpoint.
- **Soft:** done before FEAT-0011 starts. The native centre pane
  builds against `/api/render`; build that endpoint first.

## Sequencing notes
- TASK-0066 is mostly inventory and can happen alongside TASK-0067
  (read the code once, write doc + endpoint).
- TASK-0068 builds on the contract doc (defines the rule the doc
  expresses) — sequential after TASK-0066.
- TASK-0069 is parallelisable with anything. Land last to keep the
  test suite green throughout.

## Open questions to pin during implementation

- **`/api/render/<rel-path>` URL shape.** Two options:
  (a) `/api/render/<rel-path>` with the path as a URL segment
      (escaped slashes; gets ugly for nested paths), or
  (b) `/api/render?path=<rel-path>` (cleaner; query-string).
  Recommend (b). Decided in TASK-0067.

- **Cache headers on `/api/render`.** The Python server emits
  `Cache-Control: no-cache` everywhere today. Keep that; the
  renderer never wants a stale doc anyway. Re-check if profiling
  shows a hot path.

- **Frontmatter shape.** Today the cockpit page emits structured
  frontmatter via the Python template; the JSON response will
  return raw frontmatter as a dict. Confirm the TS renderer can
  format it (FEAT-0011 problem, but worth noting here).

- **Schema header on POST endpoints.** Today only GET endpoints
  emit `X-Cockpit-Schema`. POST responses should too — the
  client may not have hit a GET first and still needs to know the
  server's schema version.

## Out of plan
- Authentication / authorisation — sidecar stays loopback-only.
- Pagination — current payloads are small.
- Streaming responses — N/A for v1.
- WebSocket replacement for SSE — out of scope.
- New endpoints beyond `/api/render`.
