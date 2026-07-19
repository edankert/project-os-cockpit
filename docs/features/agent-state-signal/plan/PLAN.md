---
type: "[[plan]]"
id: PLAN-FEAT-0013
aliases: ["PLAN-FEAT-0013"]
title: "Plan: Agent state signal"
status: active
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
implements: ["[[FEAT-0013-Agent-State-Signal]]"]
related: ["[[FEAT-0010-Native-Nav-Right-Pane]]", "[[FEAT-0008-Cockpit-API-Hardening]]", "[[PHASE-006-Native-Cockpit-UI]]"]
---

# Plan — FEAT-0013 Agent state signal

## Delivery sequence

1. **[[TASK-0076]] — `CockpitState.agent_state` storage + lazy decay.**
   Add an `agent_state` block to the in-memory `CockpitState` (sibling
   of `agent_focus` / `tabs` / `history`). New method
   `record_agent_state(state, target?, agent?, message?)`. The
   `snapshot()` method walks the stored block and returns either the
   raw state or `{state: "idle"}` if the timestamp is older than the
   decay window — lazy decay, no thread yet.

2. **[[TASK-0077]] — `POST /api/cockpit/agent-state` + SSE event +
   decay timer.** New endpoint validating `{state, target?, agent?,
   message?}`. On success records to state, publishes a
   `cockpit:agent-state` ControlEvent, returns `{ok: true}`. Bumps
   `cockpit.SCHEMA_VERSION` to 3 (new SSE event name = breaking
   change). Background decay thread runs every 60 s; if the stored
   state should now appear as `idle` (per the decay rule) and hasn't
   already been observed as such, publishes a synthetic SSE so
   subscribed clients update without polling. HTTP-level tests cover
   happy path, 400 cases, SSE shape, decay.

3. **[[TASK-0078]] — `cockpit signal <state>` CLI subcommands.**
   Adds `signal busy | waiting | done | error` to `cli.py`, each
   accepting `--target`, `--agent`, `--message` as appropriate. Each
   subcommand POSTs to `/api/cockpit/agent-state`. Subprocess-level
   tests confirm the right body is sent for each shape.

4. **[[TASK-0079]] — Pretty-print `agent state` in `cockpit state` +
   COCKPIT-API.md update.** Extends `_print_state_pretty` to surface
   the new block. Documents the endpoint, SSE event, decay rule, and
   schema bump in `docs/references/COCKPIT-API.md`. Schema-header
   test (TST-0006) re-run to confirm every endpoint still emits the
   bumped version.

## Dependencies

- **Hard:** none beyond what already ships. This is purely additive
  on the existing `CockpitState` + SSE + CLI machinery.
- **Soft:** FEAT-0010 will be the first consumer. Build the pipe
  first; rail wiring happens against a working endpoint.

## Sequencing notes

- TASK-0076 ships the data shape; TASK-0077 wires HTTP + SSE on top.
  Don't merge 0076 → main before 0077, else `record_agent_state` is
  dead code briefly.
- TASK-0078 (CLI) is independent of 0077's decay thread; can land in
  parallel with 0077 once the endpoint exists.
- TASK-0079 (pretty-print + docs) gates the close-out.

## Open questions to pin during implementation

- **Decay window** — 10 min default. Configurable via env var
  (`COCKPIT_AGENT_STATE_DECAY_SECONDS`) for testability;
  documented in TASK-0077. Production value stays 600 s.
- **`done` vs `idle`** — both mean "agent not busy." Semantic split:
  - `done` is **explicit** — agent shipped its work cleanly.
  - `idle` is **implicit** — decayed from a stale `busy` / `waiting`.
  Clients show different glyphs (green-check vs grey). v1 may collapse
  them visually; the data distinction stays.
- **History entry shape** — agent-state transitions get history rows
  alongside agent-focus + user-nav. Useful for "show me what the
  agent did and how long it sat waiting." Decided in TASK-0076.
- **Per-workspace identity** — each cockpit sidecar is one workspace,
  so `agent_state` is implicitly per-workspace; no extra ID needed.
  Multi-agent-per-workspace is out of scope (last-writer-wins).

## Out of plan
- Auto-detecting state from PTY observation. Explicit signals only.
- Wrappers / hooks (e.g. `claude` wrapped to auto-signal) — separate
  effort under FEAT-0012 or a future convenience-tooling feature.
- Mode 1 (browser) UI surfacing the signal. The data pipe is
  available; wiring is a follow-up.
- OS notifications when state flips to `waiting`. That's FEAT-0012.
