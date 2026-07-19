---
type: "[[feature]]"
id: FEAT-0033
aliases: ["FEAT-0033"]
title: "Agent signal hygiene — dedup double ingestion, align semantics, unify decay, fix surface rots"
status: in-review
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
goal: "The pipeline records each event once and means the same thing on every path: hook ingestion dedups the terminal+external double-capture (live evidence: every prompt in your-sudoku's session index is stored twice); the external hook adopts the tracker's Notification subtype gate; the three independent 600s decay windows collapse to one shared constant; and the small surface rots (dead transcript link, stale queue tooltip, four wordings of 'undocumented', sessions-feed staleness) are cleaned up."
requirements: []
tests: []
tasks: ["[[TASK-0152]]", "[[TASK-0153]]", "[[TASK-0154]]", "[[TASK-0155]]"]
related: ["[[FEAT-0019-Agent-Hook-Ingestion]]", "[[FEAT-0027-External-Session-Signal]]", "[[FEAT-0020-Agent-Activity-Surfaces]]"]
---

# Agent signal hygiene

## Why

The 2026-07-19 review (artifact §P4) found real defects beneath the UX questions: a cockpit-terminal session with the external hook enabled is captured by both paths into the same tracker with no dedup key — prompts append twice, activity SSE fires twice; `Notification → needs-input` means different things on the two paths; decay is implemented three times at 600s (server state mirror, desktop poller, tracker live-TTL) and can drift if an env override touches one. These precede and outrank any redesign.

## Scope

See tasks. Dedup approach to decide in TASK-0152: drop events matching `(session_id, event, payload-hash)` within a short window at the tracker, or have the terminal-instrumented settings mark the session so the external hook stands down (one session, one capture path — cleaner if Claude Code's settings merge exposes enough to detect it).
