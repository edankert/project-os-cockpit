---
type: "[[feature]]"
id: FEAT-0031
aliases: ["FEAT-0031"]
title: "Ambient status consolidation — one agent-status surface per scope"
status: in-review
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
goal: "Coarse agent state appears exactly once per scope: rail dots for the fleet, the agent strip for the active workspace. The status-footer agent dot (a styling-incomplete duplicate of the strip) is removed — the footer keeps sidecar health only — and the Overview 'Now' card shrinks to a one-liner linking onward. The strip gains a rate-limit pip (5h budget %, amber above 80) from already-collected statusline data."
requirements: []
tests: []
tasks: ["[[TASK-0148]]", "[[TASK-0149]]"]
related: ["[[FEAT-0020-Agent-Activity-Surfaces]]", "[[FEAT-0030-Agent-Inbox]]"]
---

# Ambient status consolidation

## Why

One live session currently paints the same state in four chrome locations at once (rail, strip, footer, Now card); the footer copy even lacks a needs-input style, so two always-visible surfaces disagree about severity. Review 2026-07-19 (artifact §P1): keep ambient status glanceable but single-sourced per scope. This deliberately supersedes the footer-agent-dot part of FEAT-0020's surface set.

## Scope

Remove `#sf-agent` (footer keeps `#sf-sidecar` process health); demote the ~overview Now card to a compact line ("claude busy 12m — open agents") linking to `~agents` (or the strip until FEAT-0032 lands); add the rate-limit pip to the strip fed from the session `cost.rate_limits.five_hour` data the tracker already stores.
