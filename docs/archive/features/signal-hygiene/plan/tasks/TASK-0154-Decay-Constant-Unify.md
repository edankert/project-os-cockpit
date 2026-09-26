---
type: "[[task]]"
id: TASK-0154
aliases: ["TASK-0154"]
title: "One decay window — collapse the three independent 600s constants"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
parent: "FEAT-0033"
effort: ""
due: ""
depends: []
blocks: []
related: []
tests: []
---

# TASK-0154 — decay unification

Agent-state decay exists three times at 600s: the sidecar state mirror (`_AGENT_STATE_DECAY_SECONDS`), the desktop poller (`DECAY_MS`), and the tracker's live-session TTL (`COCKPIT_AGENT_SESSION_TTL_SECONDS`) — an env override touching one silently desynchronises the others. Establish one source (env var honoured by all three; sidecar can advertise its value via `/api/cockpit/identity` for the poller), document the contract in HOOKS.md, and add a test pinning the three to a shared constant.
