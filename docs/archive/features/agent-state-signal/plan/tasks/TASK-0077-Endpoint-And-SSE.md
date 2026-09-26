---
type: "[[task]]"
id: TASK-0077
aliases: ["TASK-0077"]
title: "POST /api/cockpit/agent-state + cockpit:agent-state SSE + decay thread"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0013"
effort: ""
due: ""
depends: ["[[TASK-0076]]"]
blocks: ["[[TASK-0078]]", "[[TASK-0079]]"]
related: []
tests: []
---

# Agent-state endpoint + SSE + decay

## Definition of Done
- [ ] `POST /api/cockpit/agent-state` route in `server.py`. Body
      `{state, target?, agent?, message?}`. `state` must be one of
      `busy`, `waiting`, `done`, `error`, `idle` — anything else →
      400 with `{ok: false, error: "..."}`.
- [ ] Successful POST: calls `state.record_agent_state(...)`,
      publishes `ControlEvent("cockpit:agent-state", {...})`,
      responds `{ok: true}`.
- [ ] `cockpit.SCHEMA_VERSION` bumped to **3** (new SSE event name
      counts as breaking under the rule in COCKPIT-API.md).
- [ ] Background decay timer: a daemon thread in `DocsServer.run`
      that wakes every 60 s, calls a new
      `CockpitState.decay_tick(now)` helper. If `decay_tick` returns
      a synthetic event payload (state flipped from busy/waiting →
      idle just now), publish a `cockpit:agent-state` SSE so
      subscribers update without polling.
- [ ] Tests in `tests/test_agent_state.py`: happy path (POST + state
      returned by GET /state), 400 on missing/invalid state, 400 on
      unknown state value, SSE event delivered on POST, SSE event
      delivered on decay (with patched short decay window).

## Steps
- [ ] Bump `SCHEMA_VERSION = 3` in `cockpit.py`.
- [ ] Add the POST route; mirror `_serve_cockpit_focus` shape.
- [ ] Add `CockpitState.decay_tick(now) -> dict | None` returning
      the synthetic payload when a state flip is observed for the
      first time (mark the state as decay-observed so we don't fire
      repeatedly).
- [ ] Spin a decay thread in `DocsServer.run` (or `_make_handler`'s
      closure scope) that calls `decay_tick` every 60 s and
      publishes via the shared bus.
- [ ] Write the new test file. Reuse `_NoDNSThreadingHTTPServer`
      pattern.

## Notes
The SSE name change (`cockpit:agent-state`) is the breaking-change
trigger for the schema bump. TST-0006 (every endpoint emits the new
header value) is re-run in TASK-0079 as the close-out gate.

The decay thread must be cleanly shut down on `DocsServer` exit so
pytest doesn't leak daemon threads between tests. Easiest pattern:
`threading.Event` flag the thread loops on.
