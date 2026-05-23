---
type: "[[task]]"
id: TASK-0053
aliases: ["TASK-0053"]
title: "Cockpit: server-side state (agent_focus, per-tab state, history)"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-23
updated: 2026-05-23
source: []
implements: ["[[FEAT-0006]]"]
fixes: []
effort: S
due: ""
depends: ["[[TASK-0048]]"]
blocks: ["[[TASK-0054]]", "[[TASK-0055]]", "[[TASK-0057]]"]
related: ["[[TASK-0050]]", "[[TASK-0052]]"]
tests: []
---

# TASK-0053 — Cockpit state endpoint

## Goal
Foundation for bi-directional cockpit ↔ LLM awareness. The cockpit now exposes a single read-only snapshot of "where things are", so the agent can check the user's view (not just push its own).

## Definition of Done
- [ ] `GET /api/cockpit/state` returns `{agent_focus, user_view, tabs, history}` as JSON.
- [ ] `POST /api/cockpit/tab-state` accepts `{tab_id, url, following}` and updates the in-memory tab table.
- [ ] `POST /api/cockpit/focus` (existing) also records into `agent_focus` + `history`.
- [ ] Stale tabs (last_seen > 45s ago) are pruned on every state read.
- [ ] `history` is a bounded deque (max ~50) ordered newest-first, carrying `{url, ts, source, target?, tab_id?}`.
- [ ] Thread-safe (the server is multi-threaded).
- [ ] Unit test exercising tab add/expire/state-read.

## Notes
- v2 will layer dwell-time, pinned items, and a `cockpit refine` interactive flow on top.
- Per-tab state is keyed by a client-generated `tab_id` (TASK-0055), persisted in localStorage.
- `user_view` is derived: the URL of whichever live tab has the most recent `last_seen`.
