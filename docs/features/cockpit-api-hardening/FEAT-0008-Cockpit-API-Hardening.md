---
type: "[[feature]]"
id: FEAT-0008
aliases: ["FEAT-0008"]
title: "Cockpit API hardening (Python side) for the native renderer"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
goal: "Freeze the Python cockpit's JSON API surface and add the one endpoint the native renderer needs (rendered Markdown fragment) — without breaking any existing mode-1 (browser) behaviour."
related: ["[[FEAT-0006-Cockpit-Layout]]", "[[FEAT-0007-Desktop-Shell]]", "[[PHASE-006-Native-Cockpit-UI]]"]
requirements: []
tasks: []
release: ""
tests: []
---

# Cockpit API hardening

## Goal
Get the Python sidecar's HTTP surface ready to be the **only** thing
the desktop renderer talks to. Audit each existing endpoint, document
its contract, add the one new endpoint the native center pane needs
(rendered Markdown HTML fragment), and gate every endpoint with a
regression test so PHASE-006 can evolve the renderer without breaking
mode 1.

## Scope

### In scope
- **Audit** each existing endpoint, write down its request shape,
  response shape, and headers (`X-Cockpit-Schema`). Endpoints:
  - `GET /api/cockpit/nav`
  - `GET /api/cockpit/context`
  - `GET /api/cockpit/state`
  - `POST /api/cockpit/focus`
  - `POST /api/cockpit/tab-state`
  - `GET /api/terminal` (mode-1 only; returns disabled in desktop mode)
  - `GET /_events` (SSE)
  - `GET /healthz`
- **Add `GET /api/render/<rel-path>`** — returns
  `{html: "<rendered body>", title, frontmatter, rel_path,
  outbound, inbound}` so the native center pane can mount the
  rendered Markdown without parsing the full HTML page. Renderer
  reuses the existing `renderer.render_markdown_body()` Python
  helper. URL prefix stripped for the desktop ("rel_path" is
  docs-root-relative; the renderer doesn't care about `/docs/`).
- **Schema versioning rule.** Document that any non-additive change
  bumps `X-Cockpit-Schema` and both clients (mode-1 cockpit JS, mode-3
  TS renderer) must check.
- **Regression tests** per endpoint. At least one HTTP-level test
  proving the response shape is stable. Where current coverage exists
  (cockpit nav / context / state, healthz, unknown-POST drain), tag
  the existing test as the contract gate; add tests where it's
  missing.

### Out of scope
- Rewriting any of the response generation logic. The endpoints stay
  what they are.
- Adding new fields beyond what the native renderer needs.
- Authentication / authorisation. The sidecar is loopback-only;
  threat model unchanged.
- Pagination / streaming optimisations. Current payloads are small
  enough.

## Acceptance
- A single doc (likely `docs/__reference__/COCKPIT-API.md` or similar)
  lists every endpoint with its contract.
- `GET /api/render/<rel-path>` works against any `.md` under `docs/`
  and returns rendered HTML matching the body content of the
  equivalent `/docs/...` page.
- Schema version constant is referenced from `cockpit.SCHEMA_VERSION`
  in every relevant response header; bumping it triggers test
  failures both sides until clients adapt.
- Every endpoint has at least one passing regression test in
  `tests/`.

## Links
- Native renderer that consumes this contract: [[FEAT-0011-Native-Center-Pane]],
  [[FEAT-0010-Native-Nav-Right-Pane]]
- Existing cockpit (mode 1) that this preserves: [[FEAT-0006-Cockpit-Layout]]
- Desktop shell that hosts the renderer: [[FEAT-0007-Desktop-Shell]]
- Phase: [[PHASE-006-Native-Cockpit-UI]]
