---
type: "[[issue]]"
id: ISS-0012
aliases: ["ISS-0012"]
title: "Workspace agent/framework label is poisoned by a stale last-session — shows codex while live agent is claude"
status: fixed
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-21
updated: 2026-07-21
source: [user_report_2026-07-21]
severity: medium
component: agent-hooks/session-tracker
parent: ""
related: ["[[FEAT-0019-Agent-Hook-Ingestion]]", "[[FEAT-0020-Agent-Activity-Surfaces]]"]
tests: []
---

# ISS-0012 — stale last-session poisons the displayed framework

## Problem

The workspace "seems stuck thinking it is using codex" (user, 2026-07-21). Two agent signals disagree:

- The **rail dot** reads `.cockpit/agent-state.json` — fresh, hook-fed: `{state: busy, agent: claude}`. Correct.
- The **agent strip / session detail / recent-sessions** read the snapshot's `session ?? last_session`. When no session is *live* in the tracker, `snapshot()` returns `last_session = self._sessions[self._order[-1]]` — the most-recently-**ordered** session — and shows *its* `agent`. If that record is a stale or one-off session, the whole project appears to be that agent's framework.

Concretely: `/api/cockpit/state` reported `session agent: codex` (from a leftover one-off codex session that was the most-recent record) while `agent-state.json` said `claude/busy`. The strip/label followed the stale record.

## Impact

Misleading, not data loss: a project can display the wrong LLM/CLI (codex vs claude) indefinitely until a newer session record supersedes the stale one. The rail dot and the strip contradict each other.

## Reproduce

1. Run (or inject) a one-off codex session in a workspace, then stop it.
2. With no live tracked session, load the workspace: the strip/session detail show `codex` even though the current/most-recent real work is claude (rail dot claude).

(In the reported case the stale record was a `codex-smoke` test session left by instrumentation verification; that specific record has been cleaned, but the underlying derivation is the bug.)

## Suggested handling (pick one/combination)

- **A (preferred): trust the live hook agent for the label.** When `activity`/`agent-state.json` reports an agent, use it for the strip/session agent; only fall back to `last_session.agent` when there is no live hook signal.
- **B: age out `last_session`.** Don't drive the current display from a session whose `ended` is beyond the decay window — show "no recent session" instead of a stale agent.
- **C: reconcile on disagreement.** If the live `activity.agent` differs from `last_session.agent`, prefer the live one (the rail and the strip should never contradict).
