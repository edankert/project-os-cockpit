---
type: "[[task]]"
id: TASK-0076
aliases: ["TASK-0076"]
title: "CockpitState.agent_state storage + lazy decay in snapshot()"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0013"
effort: ""
due: ""
depends: []
blocks: ["[[TASK-0077]]"]
related: []
tests: []
---

# CockpitState.agent_state storage

## Definition of Done
- [ ] `CockpitState` gains an `_agent_state: dict | None` slot,
      written by a new public method `record_agent_state(state,
      target, agent, message)`.
- [ ] Each call also pushes a row onto the existing `_history`
      deque with `source: "agent-state"` so cross-source ordering
      is preserved.
- [ ] `snapshot()` returns the block under key `agent_state`. The
      block is lazily decayed: if the stored state is `busy` /
      `waiting` and `now - ts > DECAY_SECONDS`, the snapshot
      reports `{state: "idle", decayed_from: "...", ts: <orig>}`
      instead of the stored value. Stored value is NOT mutated —
      the decay is observation-only at this stage.
- [ ] Decay window read from `COCKPIT_AGENT_STATE_DECAY_SECONDS`
      env var (default 600). Module-level constant for easy patching
      in tests.
- [ ] Unit-level tests in `tests/test_cockpit_state.py` (or new
      file) covering: initial empty state, record → snapshot
      round-trip, history entry, lazy decay activation.

## Steps
- [ ] Edit `CockpitState.__init__` to add the field.
- [ ] Add `record_agent_state` mirroring `record_agent_focus` shape.
- [ ] Extend `snapshot()` to include the new block; apply lazy decay.
- [ ] Add tests.

## Notes
Storage only — no HTTP / SSE in this task. TASK-0077 layers those on.
Keep the schema number unchanged at this point (still 2); TASK-0077
bumps it when the new SSE event lands.
