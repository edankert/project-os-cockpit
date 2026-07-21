---
type: "[[task]]"
id: TASK-0171
aliases: ["TASK-0171"]
title: "Usage source — expose the freshest rate-limit reading across ALL sessions, not just the last"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-20
updated: 2026-07-20
source: []
parent: "FEAT-0035"
effort: ""
due: ""
depends: ["[[TASK-0169]]"]
blocks: []
related: []
tests: []
---

# TASK-0171 — usage source: freshest across all sessions

Usage showed wrong numbers even though the correct reading was in the tracker (user report 2026-07-20: displayed 48%/19%, real 17%/58%). Two causes: (1) rate limits are account-global but the snapshot/fleet only ever surfaced the *last* session's `cost.rate_limits` — so a more recent session that lacked a statusline reading masked an earlier session that had the real one; (2) test-seeded readings had polluted the persisted value.

Fix: the tracker gains `latest_rate_limits()` — scans every session and returns the reading with the newest `captured_at` (account-global, freshest-wins). It's exposed as top-level `rate_limits` + `rate_limits_at` on `/api/cockpit/state`, and the fleet proxy uses it per workspace. The renderer adopts the snapshot's top-level reading (and the fleet's) through the existing adopt-if-newer gate, so the freshest real reading across all sessions/workspaces is what shows. (The polluted persisted value is cleared as a one-off.)

Verification: pytest — `latest_rate_limits` returns the max-captured_at reading, ignores readings without one; CDP — with a real 17%/58% (captured earlier) and a 71%/55% (no captured_at) in the tracker, the block shows 17%/58%.
