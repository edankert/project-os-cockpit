---
type: "[[task]]"
id: TASK-0179
aliases: ["TASK-0179"]
title: "Displayed agent follows the live signal, not a stale last-session (ISS-0012)"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-21
updated: 2026-07-21
source: ["[[ISS-0012]]"]
parent: "FEAT-0033"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[ISS-0012]]"]
tests: ["[[TST-0012]]"]
---

# TASK-0179 — agent label follows the live signal

Fix ISS-0012 (option A): the displayed workspace agent must follow the live hook signal, not a stale `last_session`. Two spots override the live agent with the most-recent session's agent:

- `desktop/src/ipc/agents-fleet.ts` `buildRow`: the base row sets `agent: payload?.agent` (live poller/agent-state) but is then overwritten by `row.agent = sess.agent || row.agent` where `sess` is `session ?? last_session`. Change so `last_session`'s agent only applies when there is no live agent (a genuinely live session's agent still wins).
- `desktop/src/renderer/renderer.ts` `showAgentStrip`: `agentStripAgent.textContent = session.agent` → prefer the live `activity.agent` (`activity?.agent || session.agent`).

Net: the rail dot (live agent-state) and the strip/fleet-row agent no longer contradict; a one-off codex run can't relabel a claude workspace.

Verification: unit/CDP — a workspace whose live agent-state is claude but whose last_session is codex shows `claude` in the strip and fleet row.

## Verification

CDP: with a live claude workspace the agent strip shows `claude` (was following the stale last_session). Fleet proxy now sets the row agent from the live poller/agent-state (`payload.agent`) and only lets `last_session` override when a session is genuinely live — so a stale non-live codex record can't relabel a claude workspace, while a genuinely-live codex session still shows codex (verified: a freshly-posted live codex session correctly reads codex). tsc clean.
