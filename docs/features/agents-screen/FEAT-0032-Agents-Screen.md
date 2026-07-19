---
type: "[[feature]]"
id: FEAT-0032
aliases: ["FEAT-0032"]
title: "Agents screen (~agents) — cross-workspace fleet view: sessions, cost, queues, rate limits"
status: in-review
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
goal: "A dedicated virtual page (~agents, reachable from the rail and the inbox header) with one row per workspace: live state + elapsed, current prompt, last file, dispatch origin, queue depth, ctx/$ meters, and jump actions (terminal / session / queue); a header aggregating total burn, active count, and the rate-limit budget. Session history and ~session pages become children of this screen instead of hiding inside ~overview."
requirements: ["[[REQ-0019-Agent-Fleet-Visibility]]"]
tests: []
tasks: ["[[TASK-0150]]", "[[TASK-0151]]"]
related: ["[[FEAT-0030-Agent-Inbox]]", "[[FEAT-0031-Ambient-Status-Consolidation]]", "[[FEAT-0021-Task-Dispatch]]"]
---

# Agents screen

## Why

There is no cross-workspace agent surface beyond coarse dots and the needs-input bell; sessions, cost, queue depth and the never-rendered rate-limit data are invisible for background workspaces. This is the "LLM info on its own screen" half of the 2026-07-19 review verdict (artifact §P3): detail gets a screen, ambient status stays in chrome, provenance stays in the docs.

## Design decisions

- **Data path:** desktop main proxies `GET /api/cockpit/state` for every workspace with a live sidecar (new IPC `agents:fleet`); workspaces without a sidecar show file-level state only (the rail-dot data). Chosen over sidecar-side mirroring for simplicity.
- **Navigation:** `~agents` joins the `~overview`/`~session` virtual-page family; entry points: rail button + inbox popover header + Now-card one-liner (FEAT-0031).

## Open decision (tracked here)

Browser-cockpit (mode-1) agent parity: the web UI currently has zero agent surfaces. Either add rail-dot-equivalent + inbox for the tablet monitoring use case, or document desktop-only as intended. Decide when this feature is groomed.
