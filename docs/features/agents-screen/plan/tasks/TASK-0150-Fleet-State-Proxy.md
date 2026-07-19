---
type: "[[task]]"
id: TASK-0150
aliases: ["TASK-0150"]
title: "Fleet state proxy — main-process aggregation of per-workspace agent snapshots"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: ["[[REQ-0019-Agent-Fleet-Visibility]]"]
parent: "FEAT-0032"
effort: ""
due: ""
depends: []
blocks: []
related: []
tests: []
---

# TASK-0150 — fleet state proxy

New `agents:fleet` IPC in main: per workspace, the poller's coarse state + (when a sidecar is live, from the in-memory sidecar url map — never `.cockpit/url` files) the `/api/cockpit/state` snapshot (session, cost, activity) and the dispatch queue depth. 5s cache; tolerant of sidecar-less workspaces. Verification: two live sidecars + one dormant workspace → fleet payload carries rich rows for the live pair, file-level state for the dormant one.
