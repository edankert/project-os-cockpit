---
type: "[[task]]"
id: TASK-0055
aliases: ["TASK-0055"]
title: "Cockpit: JS tab-state pings + heartbeat"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-23
updated: 2026-05-23
source: []
parent: "[[FEAT-0006]]"
fixes: []
effort: XS
due: ""
depends: ["[[TASK-0053]]"]
blocks: []
related: ["[[TASK-0050]]"]
tests: []
---

# TASK-0055 — Tab-state pings

## Goal
The cockpit JS reports each tab's current view + follow state to the server, so `/api/cockpit/state` reflects reality.

## Definition of Done
- [ ] Each tab generates a `tab_id` on first load and persists it in `localStorage` (key `cockpit-tab-id`).
- [ ] POST `/api/cockpit/tab-state` fires on:
  - initial page load
  - `navigateTo` (in-pane swap)
  - `popstate` (back/forward)
  - follow-toggle change
  - periodic heartbeat (every 15s)
- [ ] Payload: `{tab_id, url, following}`.
- [ ] Failures are silent (no console spam); the cockpit must keep working when the server is down.
