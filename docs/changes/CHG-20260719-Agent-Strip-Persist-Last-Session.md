---
type: "[[change]]"
id: CHG-20260719-Agent-Strip-Persist-Last-Session
aliases: ["CHG-20260719-Agent-Strip-Persist-Last-Session"]
title: "Agent strip persists the last session (files included) between runs"
status: merged
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
commit: ""
pr: ""
reviewed_by: "model:claude-opus"
review_date: 2026-07-19
review_verdict: approved
impacts: ["/api/cockpit/state snapshot (+last_session)", "agent strip visibility + files view"]
issues: ["[[ISS-0010-Agent-Strip-Files-Vanish-When-Idle]]"]
features: ["[[FEAT-0020-Agent-Activity-Surfaces]]"]
related: []
---

# Agent strip persistence (ISS-0010)

## Summary

Restores the "updated files" view in the agent strip that vanished when a session ended (regression from the ISS-0009 strip-hide). `AgentSessionTracker.snapshot()` now returns `last_session` — the most-recent session, slim, `live:false`, when none is live — additive to `/api/cockpit/state`. The renderer's `showAgentStrip()` renders `session ?? last_session`: live sessions are unchanged; an ended one shows muted (`.agent-strip.is-ended`, idle dot, "last session — <prompt>" label) with the files-touched detail still expandable. The strip hides only when a workspace has never run a session and nothing is queued, preserving the ISS-0009 goal (no permanent empty band).

## Verification

`tests/test_agent_hooks.py`: `last_session` populated only after a session ends, carries the touched files; full tracker suite green. Renderer driven over CDP through a real session lifecycle — strip shows live file activity, then persists as "last session" with the file still listed after SessionEnd. `tsc` clean.

Files: `src/project_os_cockpit/agent_hooks.py`, `desktop/src/renderer/{renderer.ts,renderer.css}`, `tests/test_agent_hooks.py`.
