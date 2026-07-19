---
type: "[[task]]"
id: TASK-0114
aliases: ["TASK-0114"]
title: "Agent-hook ingestion endpoint — /api/agent-hook + state mapping + SSE fan-out"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
parent: "[[FEAT-0019-Agent-Hook-Ingestion]]"
effort: "M"
depends: []
blocks: ["[[TASK-0115]]", "[[TASK-0116]]", "[[TASK-0118]]"]
related: ["[[RISK-0004-Hook-Injection-Surface]]"]
tests: ["[[TST-0010]]"]
---

# Agent-hook ingestion endpoint

## Definition of Done
- [x] `POST /api/agent-hook` accepts Claude Code / Codex hook payloads: validates shape, caps size, rejects malformed input with 400 without disturbing state.
- [x] Event mapping into `CockpitState`: `UserPromptSubmit` → busy (prompt recorded), `PermissionRequest`/`Notification(permission_prompt|idle_prompt)` → needs-input, `Stop` → waiting, `SessionEnd` → idle, `PreToolUse`/`PostToolUse(Edit|Write)` → touched file recorded.
- [x] Activity fan-out over SSE: extended `cockpit:agent-state` plus new `cockpit:agent-activity` control events.
- [x] `needs-input` added to the allowed agent-state vocabulary end to end (endpoint, decay, persistence).
- [x] Hook-fed state takes precedence over manual `cockpit signal` while an instrumented session is live; manual signal still works otherwise.
- [x] Unit tests green (TST-0010).

## Steps
- [x] Add `AGENT_HOOK_MAX_BYTES` cap + payload validation helper.
- [x] Extend `CockpitState` with per-workspace session tracking (session_id, agent, prompt, current file, source=hook|manual).
- [x] Route `POST /api/agent-hook` in `_route_post`; map events; publish `ControlEvent`s.
- [x] Extend statusline ingestion field set (cost/context) — shared payload with TASK-0117.
- [x] Tests: fixture payloads for each event type, malformed/oversized cases, precedence.

## Notes
Payloads are untrusted local input (RISK-0004): never render as HTML, log-and-drop unknown events so CLI schema drift cannot 500 the endpoint.
