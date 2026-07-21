---
type: "[[requirement]]"
id: REQ-0019
aliases: ["REQ-0019"]
title: "Cross-workspace agent detail — state, session, cost, queue, rate limits — is available on one dedicated screen"
status: implemented
implements: []
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-20
source: []
priority: medium
scope: "FEAT-0032"
specifies: ["[[FEAT-0032-Agents-Screen]]"]
verifies: []
related: ["[[REQ-0018-Agent-Attention-Completeness]]"]
tests: []
---

# REQ-0019 — agent fleet visibility

## Requirement

One dedicated screen must show, for every workspace: live agent state with elapsed time, current session summary (prompt, last file, dispatch origin), queue depth, cost and context meters, and aggregate figures (total burn, active count, rate-limit budget with reset time). Rich agent detail must not require switching into each workspace. Ambient status (rail dots, agent strip) remains in chrome — this screen is the inspection surface, not a replacement for glanceability.

## Rationale

Only coarse state crosses workspaces today; sessions, cost, queues, and the already-collected-but-never-rendered rate-limit data are invisible for background workspaces (review 2026-07-19, same artifact as REQ-0018).

## Impact analysis (2026-07-19)

Additive virtual page reusing the ~overview machinery; needs a main-process state proxy for non-active sidecars. No conflicts with existing requirements; supersedes nothing.
