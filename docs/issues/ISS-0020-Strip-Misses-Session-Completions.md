---
type: "[[issue]]"
id: ISS-0020
aliases: ["ISS-0020"]
title: "Strip misses the session's implemented tasks — status changes (esp. via non-Edit-tool writes) and cross-prompt completions never surface"
status: fixed
severity: medium
owner: user:edwin
created: 2026-07-23
updated: 2026-07-23
source: ["user-report"]
related: ["[[FEAT-0038]]", "[[REQ-0021]]", "[[TASK-0194]]", "[[TASK-0193]]"]
---

# ISS-0020 — strip misses the session's implemented tasks

## Symptom (user, project-os-cockpit)

"I haven't seen all the tasks which were implemented this session on the strip." Many tasks completed across the session never appeared.

## Root cause

Three compounding gaps in the FEAT-0038 in-flight set (focus ∪ notes-touched-this-prompt):

1. **Touch tracking misses non-Edit-tool writes.** `work_notes`/`work_ts` are populated only from `PostToolUse` events that carry a `file_path` (Edit/Write/MultiEdit). Notes changed via a shell tool (`sed`, `python -c`, a script) fire no file-path event, so they never enter `work_notes` — even though the file watcher sees them. On project-os-cockpit the session showed 11 work_notes though far more notes were edited.
2. **Per-prompt scope.** `current_prompt` only flags notes edited at/after the latest prompt boundary, so a task completed two prompts ago drops off.
3. **Non-durable transition log.** The status-diff transition log is in-memory and wiped on a sidecar restart.

The watcher (status-diff) sees every status change regardless of how the file was written, but that signal was never correlated to the session or persisted.

## Fix

See [[TASK-0194]]: the tracker records each `cockpit:status-change` onto the live session (`status_touched`, persisted), and `work_items_for_session` includes those items — union of focus ∪ session-status-changes ∪ notes-touched-this-prompt. This surfaces every task moved/completed this session, durably, whatever tool wrote it, without re-introducing the untouched project backlog (a created-but-unchanged note emits no transition).
