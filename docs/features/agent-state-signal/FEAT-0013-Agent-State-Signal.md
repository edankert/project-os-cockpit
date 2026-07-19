---
type: "[[feature]]"
id: FEAT-0013
aliases: ["FEAT-0013"]
title: "Agent state signal — `cockpit signal <state>` + per-workspace state pipe"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
goal: "Give running agents (Claude Code, Codex, Aider, …) a tiny way to declare their state — `busy`, `waiting-for-input`, `done`, `error` — so the cockpit can surface 'this workspace needs you' at a glance, distinct from 'this workspace was active recently'."
related: ["[[FEAT-0010-Native-Nav-Right-Pane]]", "[[FEAT-0006-Cockpit-Layout]]", "[[PHASE-006-Native-Cockpit-UI]]"]
requirements: []
tasks: []
release: ""
tests: []
---

# Agent state signal

## Goal

A passive observer (file watcher, SSE) can tell you whether a workspace
*was* doing something recently. It cannot reliably tell you whether the
agent is **finished and waiting for you**. That distinction is the one
the user actually cares about — it's the difference between "I'll check
back later" and "the AI just stopped and needs me right now."

This feature adds the missing signal layer: a tiny CLI command agents
call at known transition points, plus the server-side state tracking
and SSE fan-out that lets every cockpit surface — desktop workspace
rail (FEAT-0010), browser cockpit, OS notifications, future automation
— consume it identically.

## Scope

### In scope

**CLI** (additive subcommands on the existing `cockpit` tool):

```
cockpit signal busy [--target <id>] [--agent <name>]
cockpit signal waiting [--message <text>]
cockpit signal done
cockpit signal error [--message <text>]
```

Discovery follows the existing `COCKPIT_URL` / `.cockpit/url` walk-up
chain — agents already know how to find the cockpit. In desktop mode
(`COCKPIT_DESKTOP=1`) the `.cockpit/url` file isn't written, so the
shell mounts `COCKPIT_URL` into the embedded terminal env (already
done for `cockpit focus` via TASK-0049 / TASK-0059).

**Server**:

- `POST /api/cockpit/agent-state` with body
  `{state, target?, agent?, message?}`. Stamps `ts` server-side.
- `CockpitState.record_agent_state(...)` tracks last-state + history,
  alongside the existing `agent_focus` / `tabs` / `history`.
- `GET /api/cockpit/state` returns a new `agent_state` block:
  `{state, target?, agent?, message?, ts}`.
- SSE event `cockpit:agent-state` emitted on every change so clients
  don't poll.
- **Auto-decay**: if `state == "busy"` and no update for 10 min, the
  server flips it to `idle` and emits a synthetic change event.
  Configurable later if it matters.

**Contract doc**: `docs/references/COCKPIT-API.md` updated with the
new endpoint + SSE event + state-transition rules.

**Schema bump**: this adds a new SSE event name, which counts as
breaking under the rule in `FEAT-0008`. Bump `cockpit.SCHEMA_VERSION`.

### Out of scope

- Auto-detection of state by snooping the PTY / stdin (would require
  intercepting the agent's terminal session — fragile, agent-specific,
  and the wrong layer). Explicit signals are the contract.
- Wrappers / hooks that auto-emit signals around `claude` / `codex` /
  etc. invocations. Those are a follow-up convenience layer; users
  who want it before then can call the CLI directly.
- Multi-agent per workspace (concurrent agents reporting state). v1
  is single-agent-per-workspace; last-writer-wins.
- OS notifications, dock badges. Surface choice lives in FEAT-0010 /
  FEAT-0012.
- Mode 1 (browser) consumption — the data pipe is available, but
  wiring the browser cockpit's UI to it is a separate task.

## Acceptance

- From a terminal inside any workspace's tree, `cockpit signal busy`
  succeeds (exit 0) and `cockpit state --json` shows
  `agent_state.state == "busy"` with a recent `ts`.
- A subsequent `cockpit signal waiting --message "review my PR"` shows
  the new state and the message; a connected SSE client receives a
  `cockpit:agent-state` event with the same payload between the two.
- A connection that stays idle past the decay window observes a
  synthetic `cockpit:agent-state` event flipping state to `idle`.
- `cockpit state` CLI's pretty-printed form gains a one-line summary:
  `agent state : waiting  (review my PR)  @ 2026-05-25T16:00:00Z`.
- `cockpit.SCHEMA_VERSION` bumped; TST-0006's header assertion still
  passes (every endpoint emits the new version); contract doc updated.

## Why this is its own feature

The data pipe is genuinely general-purpose — every cockpit surface
(desktop rail, browser tab title, future OS-notification daemon, future
dashboard) consumes the same signal. Keeping it separate from
FEAT-0010 means the renderer just *uses* the signal; the signal
itself is testable and documented independently.

## Links

- Visible consumer: [[FEAT-0010-Native-Nav-Right-Pane]] (workspace rail).
- Existing focus / state machinery this extends: `CockpitState` in
  `server.py` (TASK-0053), `cockpit` CLI (TASK-0049 / TASK-0054).
- Contract: `docs/references/COCKPIT-API.md` (FEAT-0008).
- Phase: [[PHASE-006-Native-Cockpit-UI]].
