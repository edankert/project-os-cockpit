---
type: "[[test]]"
id: TST-0007
aliases: ["TST-0007"]
title: "Wire-level coverage for focus POST, tab-state POST, and SSE event shapes"
status: passing
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0069]]"]
verifies: ["[[TASK-0069]]", "[[FEAT-0008-Cockpit-API-Hardening]]"]
path: "tests/test_focus_and_tab_state.py"
---

# TST-0007 — focus / tab-state / SSE wire shapes

## Intent
Closes the wire-level gap left by `test_cockpit_state.py`, which
exercises the `CockpitState` Python class but never goes through
HTTP. PHASE-006 will rebuild the cockpit UI in TypeScript; the
TS client only ever sees the wire shape, so the contract must be
gated at that level.

## Coverage

**`POST /api/cockpit/focus`** (4 tests):
- Happy path with `{"target": "README"}` → 200 + `{ok, url}`;
  url resolves to the indexed docs path (`id: README` in
  frontmatter beats top-level support-file lookup).
- 400 when `target` is missing.
- 404 when target is unresolvable.
- A successful focus updates `/api/cockpit/state.agent_focus` and
  appends a history entry with `source: "agent"`.

**`POST /api/cockpit/tab-state`** (3 tests):
- Happy path with `{tab_id, url, following}` → 200 + `{ok: true}`.
- 400 when `tab_id` OR `url` is missing.
- After a heartbeat, `GET /api/cockpit/state.tabs` shows the tab
  with the correct flag.

**`GET /_events` SSE** (2 tests):
- After `POST /api/cockpit/focus`, the SSE channel emits an
  `event: cockpit:focus` envelope with the same
  `{url, target}` JSON payload as the focus response. Verified
  by reading raw bytes from the SSE socket and matching the
  `event:` marker.
- Publishing a `FileEvent` directly on the server's bus (the same
  path the watcher uses) surfaces an `event: file-changed`
  envelope with the rel-path as plain-text data.

## Bonus bug fix

While writing this test, the suite surfaced a long-standing bug:
`Index._on_event` (the watcher subscriber) accessed `event.abs_path`
without checking type, so every `cockpit:focus` ControlEvent
triggered an `AttributeError` that was buried by the EventBus's
per-subscriber try/except + `log.exception`. Fixed in `index.py`:
added `isinstance(event, FileEvent)` guard. No new test needed —
the SSE focus test now exercises this path and would fail if the
exception re-surfaced.

## Location
`tests/test_focus_and_tab_state.py` — 9 tests, all passing as of
2026-05-25.

## Status
`passing` — 9/9.
