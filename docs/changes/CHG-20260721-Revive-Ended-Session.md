---
type: "[[change]]"
id: CHG-20260721-Revive-Ended-Session
title: "Agent session survives a sidecar soft-reload — fresh activity revives a seed-ended session"
date: 2026-07-21
author: user:edwin
status: merged
related: ["[[ISS-0014]]", "[[TASK-0183]]", "[[TASK-0014]]", "[[FEAT-0019]]"]
reviewed_by: "opus-independent-review"
review_date: 2026-07-21
review_verdict: CLOSE
---

# CHG-20260721 — revive an ended session on fresh activity

## What changed

`AgentSessionTracker.ingest` (`src/project_os_cockpit/agent_hooks.py`) now clears a stale `ended` marker when a session receives any event other than `SessionEnd`. Previously only `SessionStart` cleared `ended`.

## Why

The console's agent-state strip showed no current session and no `ctx %` / `$` for a project while an agent was actively working there (user report 2026-07-21, project-os-cockpit). Root cause: `_seed`, run when the sidecar loads `.cockpit/sessions.json` at startup, marks every persisted-live session (`ended is None`) as `ended` so a dead session can't ghost as live. That is correct for a crashed process — but the soft live-reload (TASK-0014, "file changes refresh panes, terminal survives") restarts the sidecar **while the embedded terminal and its Claude/Codex session keep running**. The still-alive session then keeps POSTing `Statusline`/`PreToolUse`/… hooks, but with only `SessionStart` clearing `ended` (and that already fired before the restart) the session stayed `ended=True` forever: `_live_session_locked` skips it, `has_live_session()` returns False, and the strip falls back to the most-recent ended session (often a stale Codex test session with no cost) — hence no current session and no ctx/$.

## Impact

- **Behaviour**: after a sidecar soft-reload, the live agent session is recognised again as soon as its next hook arrives, so the strip shows the current session with its live `ctx %` and `$`. `SessionEnd` remains the only event that ends a session; a genuinely dead session receives no further events and still ages out via `_live_ttl` (default 600s), so nothing can ghost as live — the `_seed` safety property is preserved.
- **Scope**: server-side only; no API-shape or renderer change; a sidecar reload picks it up. The handler already extracted `cost.total_cost_usd` and `context_window.used_percentage` correctly (verified against a real Claude statusline payload) — the data was captured all along; it just wasn't surfaced because the session was flagged ended.
- **Tests**: `tests/test_agent_hooks.py::test_seeded_session_revives_on_fresh_activity` — start → persist → reseed (ended) → fresh `Statusline` revives the session and surfaces the fresh cost/ctx; a following `SessionEnd` ends it again. Existing `test_session_persistence_and_seed` (a crashed session stays ended with no new activity) still passes. Full suite: 224 passed, 1 skipped.

## Files

- `src/project_os_cockpit/agent_hooks.py` — `ingest` revives a stale `ended` on any non-`SessionEnd` event.
- `tests/test_agent_hooks.py` — added `test_seeded_session_revives_on_fresh_activity`.
