---
type: "[[change]]"
id: CHG-20260719-Signal-Hygiene
aliases: ["CHG-20260719-Signal-Hygiene"]
title: "Agent signal hygiene — ingestion dedup, unified decay, surface rots"
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
impacts: ["/api/agent-hook ingestion (dedup)", "poller decay constant", "session-page transcript link", "undocumented wording", "queue tooltip"]
issues: []
features: ["[[FEAT-0033-Agent-Signal-Hygiene]]"]
related: ["[[TASK-0152]]", "[[TASK-0153]]", "[[TASK-0154]]", "[[TASK-0155]]"]
---

# Agent signal hygiene (FEAT-0033)

## Summary

**TASK-0152 — ingestion dedup.** `AgentSessionTracker.ingest()` drops a payload identical to one already seen for the same `(session_id, hook_event_name)` within `DEDUP_WINDOW_SECONDS` (2s) — the terminal + external double-capture that recorded every prompt twice (live evidence in your-sudoku's index). Returns `ignored/duplicate`, surfaced in the `/api/agent-hook` response; the recent-events map is pruned at 256 entries. Guarded by `test_double_capture_is_deduped`.

**TASK-0153 — notification semantics.** Completed as part of the severity remap (TASK-0156): the external-hook embedded script gates `Notification` by subtype exactly as the tracker does (idle_prompt → waiting, permission/elicitation → needs-input, others → no-op), so the file-fallback path no longer over-alarms.

**TASK-0154 — unified decay.** The desktop poller's stale-state decay now reads `COCKPIT_AGENT_STATE_DECAY_SECONDS` (default 600), the same env var the sidecar uses, so a single override can't leave the two agent-state decay clocks disagreeing.

**TASK-0155 — surface rots.** Session-page transcript path is now a Reveal-in-Finder button; the sessions-feed "undoc" chip reads "undocumented" like every other surface; the queue-chip static tooltip matches the JS ("click to manage").

## Verification

`tests/test_agent_hooks.py::test_double_capture_is_deduped` (dedup + non-duplicate still lands); full Python suite 211 passed / 1 skipped; `tsc` clean.

Files: `src/project_os_cockpit/{agent_hooks,server}.py`, `desktop/src/ipc/agent-state-poller.ts`, `desktop/src/renderer/{index.html,renderer.ts}`, `tests/test_agent_hooks.py`.
