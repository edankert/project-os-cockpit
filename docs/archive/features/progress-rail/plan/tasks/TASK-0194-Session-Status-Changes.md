---
type: "[[task]]"
id: TASK-0194
aliases: ["TASK-0194"]
title: "Record per-session status changes from the watcher and include them (durably) in the in-flight work set"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-23
updated: 2026-07-23
source: ["[[ISS-0020]]"]
parent: "FEAT-0038"
effort: ""
due: ""
depends: ["[[TASK-0193]]"]
blocks: []
related: ["[[TASK-0162]]", "[[TASK-0191]]"]
tests: ["[[TST-0012]]"]
---

# TASK-0194 — session-scoped status changes in the in-flight set

Fixes [[ISS-0020]]. `AgentSessionTracker` gains `record_status_change(payload)` — invoked for every `cockpit:status-change` control event (wired via a bus subscriber in the server) — which stamps the changed note onto the live session's `status_touched` map (`rel → {id, status, ts, title}`, bounded, persisted). `work_items_for_session` now unions three sources into the in-flight set, deduped by id: (1) SNAPSHOT `focus` (declared active), (2) `status_touched` (every note whose status changed this session — captures shell-tool writes the touch-tracker misses, and survives a sidecar restart via persistence), (3) `work_notes` touched at/after the prompt boundary. Focus and status-changed items are `current_prompt`; touched notes keep the prompt gate. Enrichment (title/status/type/done) still resolves from the live index. Created-but-unchanged notes emit no transition, so the untouched backlog stays out (no regression of [[ISS-0018]]).

Verification: pytest — a `record_status_change` on the live session appears in `_slim`/`work_items` as current; a note changed via the watcher (no work_note touch) still surfaces; a created note (seed, no transition) does not; `status_touched` persists across a reseed; union dedupes with focus/touched. Live: project-os-cockpit strip shows the tasks completed across the session.

## Verification

pytest: `test_work_items_include_session_status_changes` (a status-changed note with no work_note touch surfaces as current + done + index-enriched; a created-but-unchanged note stays out) + `test_record_status_change_stamps_live_session` (stamps the live session, no-ops without one). Full suite 232 passed / 1 skipped. Live: on project-os-cockpit a `sed` status change (no Edit-tool touch) registered in `status_touched` and surfaced in `work_items`; on your-health the strip now shows the agent's status-changed items (PHASE-0007 done, a CHG note, ISS-0024) — the completions the touch/prompt model had missed.
