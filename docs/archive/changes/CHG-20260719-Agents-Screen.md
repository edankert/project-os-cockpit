---
type: "[[change]]"
id: CHG-20260719-Agents-Screen
aliases: ["CHG-20260719-Agents-Screen"]
title: "Agents screen (~agents) — cross-workspace fleet view + main-process fleet proxy"
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
impacts: ["new agents:fleet IPC", "new ~agents virtual page", "rail agents button", "poller payload accessor", "dispatch queue-depth accessor"]
issues: []
features: ["[[FEAT-0032-Agents-Screen]]"]
related: ["[[REQ-0019-Agent-Fleet-Visibility]]", "[[TASK-0150]]", "[[TASK-0151]]"]
---

# Agents screen (FEAT-0032)

## Summary

A dedicated `~agents` virtual page gives cross-workspace mission control — the "LLM detail on its own screen" half of the 2026-07-19 review.

**TASK-0150 — fleet proxy (main).** New `desktop/src/ipc/agents-fleet.ts` (`registerAgentsFleetIpc`) assembles one `FleetRow` per workspace in the main process, where the cross-workspace data lives: coarse state from the poller's new `getLastAgentPayloads()`, plus — when a sidecar is live (`sidecarUrlFor`) — its `/api/cockpit/state` session/cost/activity, and queue depth from the dispatch queue's new `queueDepthFor()`. 3s cache. Exposed via `agents:fleet` IPC / `cockpitApi.agents.fleet()`.

**TASK-0151 — ~agents page (renderer).** `renderAgentsPage()` renders into the centre pane (joins the `~overview`/`~session` virtual-page family with real history): a header aggregating active count, total queued, total burn, and the 5h rate-limit budget (amber ≥80%); one row per workspace sorted needs-input → waiting → busy → error → done → idle, each with state dot, current session summary (prompt, last file, dispatch origin, queue depth), ctx/$ meters, and jump actions (respond/review/terminal + session). Reachable from a new rail button (`#agents-toggle`), the attention panel's "N finished today" line, and the Overview Now one-liner.

## Verification

Driven end-to-end over CDP: opened a workspace, drove a live session on it plus coarse needs-input/waiting states on two others; `~agents` rendered 9 rows with correct ordering, the live row rich (prompt, `renderer.ts`, ctx 42% · $3.41, undocumented, session jump), coarse rows for background workspaces, aggregate header `3 active · $3.41 today`; rail button and Now one-liner both navigate to it. `tsc` clean.

Files: `desktop/src/ipc/agents-fleet.ts`, `desktop/src/ipc/{agent-state-poller,dispatch-queue,sidecar}.ts`, `desktop/src/{main,preload}.ts`, `desktop/src/renderer/{index.html,renderer.ts,renderer.css}`.
