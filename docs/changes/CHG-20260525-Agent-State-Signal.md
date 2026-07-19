---
type: "[[change]]"
id: CHG-20260525-Agent-State-Signal
aliases: ["CHG-20260525-Agent-State-Signal"]
title: "Agent state signal: `cockpit signal` CLI + POST /api/cockpit/agent-state + SSE + decay timer + schema bump 2→3"
status: merged
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0076]]", "[[TASK-0077]]", "[[TASK-0078]]", "[[TASK-0079]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/cockpit.py (SCHEMA_VERSION 2→3)"
  - "src/project_os_cockpit/server.py (+CockpitState.record_agent_state / _effective_agent_state / decay_tick; +POST /api/cockpit/agent-state; +decay timer thread)"
  - "src/project_os_cockpit/cli.py (+`cockpit signal` subcommand; +agent_state row in `cockpit state` pretty-print)"
  - "docs/references/COCKPIT-API.md (new endpoint, new SSE event, schema rule + value update)"
  - "tests/test_cockpit_state.py (+8 cases — storage, decay semantics)"
  - "tests/test_agent_state.py (new — 6 cases — HTTP + SSE)"
  - "tests/test_cli_signal.py (new — 9 cases — CLI parser + body)"
  - "tests/test_render_endpoint.py (read SCHEMA_VERSION from constant, not hard-coded)"
  - "docs/features/agent-state-signal/plan/tests/TST-0009-Agent-State.md (new)"
issues: []
features: ["[[FEAT-0013-Agent-State-Signal]]"]
related: ["[[FEAT-0010-Native-Nav-Right-Pane]]", "[[FEAT-0008-Cockpit-API-Hardening]]"]
---

# Agent state signal

## Summary

Closes FEAT-0013. Agents (Claude Code, Codex, Aider, anything) can now
declare their state via a tiny CLI subcommand:

```sh
cockpit signal busy    --target FEAT-0010 --agent claude
cockpit signal waiting --message "review my PR"
cockpit signal done
cockpit signal error   --message "merge conflict in X"
cockpit signal idle
```

Each call POSTs to `POST /api/cockpit/agent-state`, the cockpit records
the transition on `CockpitState`, and a `cockpit:agent-state` SSE event
fans out to subscribers. The workspace rail in FEAT-0010 will consume
this directly to paint per-workspace status dots; OS notifications in
FEAT-0012 will hook the same stream.

Schema bumped to **3** (new SSE event name counts as breaking under the
rule in COCKPIT-API.md).

Test count: **145 → 154** (+9 visible; +23 actual — 8 added to existing
`test_cockpit_state.py`, 6 in new `test_agent_state.py`, 9 in new
`test_cli_signal.py`).

## What landed

### TASK-0076 — `CockpitState.agent_state` + lazy decay
- New `_agent_state` slot on `CockpitState`.
- `record_agent_state(state, target?, agent?, message?)` — populates
  the slot, pushes a `source: "agent-state"` history row, returns the
  canonical payload.
- `snapshot()` includes the new block.
- **Lazy decay**: `busy` / `waiting` older than
  `COCKPIT_AGENT_STATE_DECAY_SECONDS` (default 600) are reported as
  `{state: "idle", decayed_from: "<orig>", ts: <orig>}` without
  mutating the stored value.
- `decay_tick(now)` returns the synthetic payload **exactly once** per
  decay event — TASK-0077's timer publishes it as SSE, then a fresh
  `record_agent_state` re-arms.

### TASK-0077 — Endpoint + SSE + decay thread + schema bump
- `cockpit.SCHEMA_VERSION = 3` (was 2).
- `POST /api/cockpit/agent-state` route in `server.py`. Validates
  `state ∈ {busy, waiting, done, error, idle}`; 400 on missing /
  unknown / non-JSON; on success records state + publishes
  `cockpit:agent-state` ControlEvent.
- Background daemon thread in `DocsServer.run()` ticks every 60 s
  (configurable via `COCKPIT_AGENT_STATE_DECAY_TICK_SECONDS` for
  tests), calls `decay_tick`, fans the synthetic SSE out via the
  shared bus. Joined cleanly on shutdown via `threading.Event`.

### TASK-0078 — `cockpit signal` CLI
- New `signal {busy,waiting,done,error,idle}` subparser on the
  existing `cockpit` CLI.
- `--target`, `--agent`, `--message` flags.
- Discovery follows the existing `COCKPIT_URL` / `.cockpit/url`
  walk-up chain (no changes to that logic).
- Exit 0 on success with `cockpit signal -> <state>` ack; non-zero
  with server error on stderr otherwise.

### TASK-0079 — Pretty-print + contract doc
- `cockpit state` (CLI) now surfaces a one-line agent-state summary
  above agent-focus when present, including `decayed from: <prior>`
  when the state has been lazily flipped.
- `docs/references/COCKPIT-API.md` updated:
  - Schema value bumped (2 → 3); reason documented.
  - New `POST /api/cockpit/agent-state` section with full contract.
  - `GET /api/cockpit/state` response example carries the new block.
  - SSE event table gains the `cockpit:agent-state` row.
  - Auto-decay rule documented.

### Bonus fix
- `tests/test_render_endpoint.py` read `cockpit.SCHEMA_VERSION` from
  the constant instead of hard-coding `"2"`, so the next schema bump
  won't have to chase the same assertion across two files.

## Smoke-test status

- Full pytest suite: **154 passed, 1 skipped**.
- Sanity: `cockpit signal busy` against a running mode-1 cockpit (with
  `.cockpit/url` discovery) populates `/api/cockpit/state.agent_state`
  and fires the SSE on a `curl /_events` consumer.

## Known gap (follow-up)

In desktop mode the embedded terminal pane inherits `process.env` from
Electron and has **no `COCKPIT_URL` set**, so an agent running there
can't auto-discover the cockpit. A one-line fix lives in
`desktop/src/ipc/terminal.ts` (pass `COCKPIT_URL=<sidecar-url>` in the
spawn env when `cockpitApi.terminal.spawn` is called). Not blocking
FEAT-0013 — the pipe is complete — but it would make the demo
turnkey. Track as a small follow-up under FEAT-0010 or
FEAT-0012.

## Documentation Coverage
- features: covered (FEAT-0013 → `done`)
- requirements: not-applicable
- tasks: TASK-0076..0079 → `done`
- issues: not-applicable
- tests: TST-0009 added (status `passing`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (FEAT-0013 → done, TASK-0076..0079 → done,
  features_done 4 → 5, tasks_done 75 → 79, tests 8 → 9,
  test_cases 132 → 155 / 154 passing, focus cleared, TST counter
  8 → 9, schema bump documented)
