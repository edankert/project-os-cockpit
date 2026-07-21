---
type: "[[issue]]"
id: ISS-0014
aliases: ["ISS-0014"]
title: "Agent session strip shows no current session / ctx / $ after a sidecar soft-reload (session stuck ended)"
status: fixed
severity: medium
owner: user:edwin
created: 2026-07-21
updated: 2026-07-21
source: ["user-report"]
related: ["[[FEAT-0019]]", "[[TASK-0183]]", "[[TASK-0014]]"]
---

# ISS-0014 — session stuck "ended" after a sidecar soft-reload

## Symptom

In the desktop shell, the agent-state strip at the top of the console for a project shows no current session and no `ctx %` / `$` — even while an agent is actively working in that project's embedded terminal. Reported for project-os-cockpit on 2026-07-21.

## Root cause

`AgentSessionTracker._seed` (startup load of `.cockpit/sessions.json`) deliberately marks any persisted session that was live (`ended is None`) as **ended**, "so they can't ghost as live forever." That is correct for a session whose process actually died. But the soft live-reload (TASK-0014, "file changes refresh panes, terminal survives") restarts the sidecar **while the embedded terminal — and its Claude/Codex session — keeps running**. After the restart the still-alive session keeps POSTing `Statusline`/`PreToolUse`/… hooks, but only `SessionStart` clears `ended`, and that fired once before the restart. So the session is stuck `ended=True`: its cost/context are still captured on the record, but `_live_session_locked` skips it (requires `ended is None`), `has_live_session()` returns False, and the strip falls back to the most-recent *ended* session — often a stale Codex test session with no cost — showing no current session and no ctx/$.

Reproduced deterministically: start → statusline (live) → reseed (ended) → fresh statusline → still `has_live_session()==False`.

## Fix

See [[TASK-0183]]: any non-`SessionEnd` lifecycle event revives a stale `ended` marker — a session receiving fresh activity is alive again. A genuinely dead session receives no further events and still ages out via the TTL, so it cannot ghost as live.
