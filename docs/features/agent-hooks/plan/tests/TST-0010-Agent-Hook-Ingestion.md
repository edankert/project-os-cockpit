---
type: "[[test]]"
id: TST-0010
aliases: ["TST-0010"]
title: "Agent-hook ingestion — endpoint, state mapping, sessions, provenance"
status: active
covers: ["[[FEAT-0019-Agent-Hook-Ingestion]]", "[[FEAT-0022-Session-Insight-And-Traceability]]"]
command: ".venv/bin/pytest tests/test_agent_hooks.py -q"
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-09-23
scope: feature
level: integration
entrypoint: ".venv/bin/python -m pytest tests/test_agent_hooks.py"
tasks: ["[[TASK-0114]]", "[[TASK-0123]]", "[[TASK-0125]]", "[[TASK-0126]]"]
last_verified: 2026-07-05

---

# TST-0010 — Agent-hook ingestion

## What it verifies

`tests/test_agent_hooks.py` (13 tests) covers the full `/api/agent-hook` pipeline: event → headline-state mapping (`UserPromptSubmit` → busy, `PermissionRequest`/`Notification` → needs-input, `Stop` → waiting, `SessionEnd` → idle), activity + session blocks in `/api/cockpit/state`, tool-event file recording, the undocumented-work rule (TASK-0125), Statusline cost ingestion, payload validation (malformed JSON, non-object, missing event name, oversized 413, unknown-event tolerance), query-param defaults for the shell forwarders (Codex `thread-id` fallback), manual-signal precedence while a hook session is live, `cockpit:agent-activity` SSE delivery, session persistence + crash-seed semantics (TASK-0123), and CHG provenance via `/api/render` (TASK-0126).

## Evidence

- 2026-07-05: `13 passed` in `tests/test_agent_hooks.py`; full suite `170 passed, 1 skipped`.
- 2026-07-05: live smoke against the running desktop sidecar (your-trainer, port 8765): busy → needs-input persisted to `.cockpit/agent-state.json` with `source: hook`; `/api/cockpit/sessions` recorded the session; SessionEnd → idle.

## September 23 regression coverage

`tests/test_agent_hooks.py` now checks parent state and child identity through SubagentStart/Stop, Interrupt holding needs-input through late PostToolUse and Stop, new-prompt recovery and SessionEnd. The combined agent/external tests pass 29 cases. Desktop generator and dispatch checks run with `cd desktop && npm run build && node --test tests/codex-shell-exit.test.mjs tests/codex-dispatch.test.mjs`; they cover native event registration, same-shell return and actual paste/Return submission ordering. Full-suite counts are recorded on FEAT-0019.
