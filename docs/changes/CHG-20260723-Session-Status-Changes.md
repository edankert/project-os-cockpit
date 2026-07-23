---
type: "[[change]]"
id: CHG-20260723-Session-Status-Changes
title: "Console strip surfaces every task the session moved/completed — status changes recorded per-session from the watcher"
date: 2026-07-23
author: user:edwin
status: merged
related: ["[[ISS-0020]]", "[[TASK-0194]]", "[[FEAT-0038]]", "[[REQ-0021]]"]
reviewed_by: "opus-independent-review"
review_date: 2026-07-23
review_verdict: CLOSE
---

# CHG-20260723 — session status changes in the in-flight set

## What changed

`AgentSessionTracker.record_status_change` (new) stamps each note whose status changes onto the live session's `status_touched` map (`rel → {id, status, ts, title}`, bounded to 60, persisted). A bus subscriber in `DocsServer` feeds it every `cockpit:status-change` control event from the watcher. `work_items_for_session` now unions THREE sources, deduped by id: SNAPSHOT `focus`, session `status_touched`, and `work_notes` touched this prompt — focus and status-changed items are `current_prompt`.

## Why

The user hadn't seen the tasks implemented across a session (ISS-0020). The in-flight set was `focus ∪ notes-touched-this-prompt`, and the touch signal (`work_notes`) is populated only from `PostToolUse` file-path events (Edit/Write) — so notes changed by a shell tool (`sed`, a script) never registered, and cross-prompt completions dropped off the per-prompt filter, and the transition log didn't survive restarts. The watcher, by contrast, sees every status change regardless of the writing tool; correlating it to the session and persisting it captures the real "implemented this session" set durably — while created-but-unchanged notes (no transition) stay out, so the untouched backlog doesn't return (ISS-0018).

## Impact

- **Behaviour**: the strip now shows every task the session moved or completed — filled as they reach done — plus the declared focus and this-prompt edits. Captures shell-tool writes; survives a sidecar restart (persisted). Verified live on both project-os-cockpit and your-health.
- **Scope**: sidecar-only; additive. `record_status_change` no-ops without a live session; bounded map; the bus subscriber runs on the watcher thread and re-uses the tracker lock.
- **Tests**: `test_work_items_include_session_status_changes`, `test_record_status_change_stamps_live_session`. Full suite 232 passed / 1 skipped.

## Files

- `src/project_os_cockpit/agent_hooks.py` — `record_status_change`, `status_touched` in the slim session + new-session seed + `STATUS_TOUCHED_MAX`.
- `src/project_os_cockpit/server.py` — bus subscriber feeding `record_status_change`.
- `src/project_os_cockpit/cockpit.py` — three-source union in `work_items_for_session`.
- `tests/test_stats_scope.py` — status-change coverage.
