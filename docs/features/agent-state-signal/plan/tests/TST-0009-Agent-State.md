---
type: "[[test]]"
id: TST-0009
aliases: ["TST-0009"]
title: "Agent-state pipe — storage, endpoint, SSE delivery, decay, CLI"
status: passing
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0076]]", "[[TASK-0077]]", "[[TASK-0078]]"]
verifies: ["[[TASK-0076]]", "[[TASK-0077]]", "[[TASK-0078]]", "[[FEAT-0013-Agent-State-Signal]]"]
path: "tests/test_cockpit_state.py + tests/test_agent_state.py + tests/test_cli_signal.py"
---

# TST-0009 — Agent-state pipe

## Intent
Locks the full FEAT-0013 contract: from `cockpit signal busy` typed
in a terminal, through the `POST /api/cockpit/agent-state` request
body, through `CockpitState` storage + lazy decay, to the
`cockpit:agent-state` SSE event the workspace rail (FEAT-0010) will
subscribe to.

## Coverage

**`test_cockpit_state.py` — CockpitState class (8 new cases):**
- Initial `agent_state` is `None`.
- `record_agent_state(...)` populates the snapshot field and returns
  the canonical payload.
- Optional fields (`target` / `agent` / `message`) elided cleanly
  when not supplied.
- History entry written with `source: "agent-state"`.
- Lazy decay: stored `busy` reports as `idle` (with `decayed_from`)
  in snapshot after the configurable window.
- `done` / `error` are explicit terminal states — they don't decay.
- `decay_tick` returns the synthetic payload exactly once per decay
  event (idempotent until the next `record_agent_state`).
- A fresh declaration unlatches the decay-observed flag.

**`test_agent_state.py` — HTTP + SSE (6 cases):**
- `POST /api/cockpit/agent-state` happy path, all valid states.
- 400 on missing `state`, 400 on unknown value.
- SSE: `cockpit:agent-state` event delivered after a successful POST
  with the correct JSON payload.
- SSE: synthetic event delivered when the decay timer flips a stale
  `busy` to `idle`.

**`test_cli_signal.py` — `cockpit signal` CLI (9 cases):**
- Each documented state produces the right POST body.
- `--target` / `--agent` / `--message` flags compose correctly.
- Argparse rejects unknown states with a clear error.
- Server error responses propagate (exit code + stderr).
- `--cockpit-url` override is honoured.

## Status
`passing` — 23 / 23 (8 storage + 6 HTTP + 9 CLI).
