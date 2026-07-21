---
type: "[[issue]]"
id: ISS-0013
aliases: ["ISS-0013"]
title: "Session history is undiscoverable after moving to the ~agents screen"
status: fixed
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-21
updated: 2026-07-21
source: [user_report_2026-07-21]
severity: low
component: renderer/overview+agents
parent: ""
related: ["[[TASK-0178]]", "[[FEAT-0032-Agents-Screen]]", "[[FEAT-0022-Session-Insight-And-Traceability]]"]
tests: []
---

# ISS-0013 — session history is undiscoverable

## Problem

TASK-0178 removed the "Agent sessions" feed from the overview and relocated session history to the `~agents` fleet screen (a "Recent sessions" section below the fleet rows). The `~agents` screen is only reachable via a small Agents rail icon, so the history is now hard to find — user (2026-07-21): "I don't understand how to make the recent sessions section appear?". The overview, where sessions used to live, no longer hints at them.

## Impact

Low: no data lost (the history renders on `~agents`), but the surface is effectively hidden. This is a side-effect of the declutter — the removal was intentional, the discoverability gap was not.

## Suggested handling (pick one/combination)

- **A (preferred): a small pointer on the overview.** A single "N recent sessions ›" line (project-focused, not the full feed we removed) linking to `~agents`. Keeps the overview clean while restoring the trail to the history.
- **B: make the `~agents` entry obvious.** A labelled button/menu item or keyboard shortcut, beyond the current rail icon (`#agents-toggle`, title "Agents — all sessions").
- **C: onboarding hint / empty-state.** First-run tip pointing at the Agents screen for session history.
