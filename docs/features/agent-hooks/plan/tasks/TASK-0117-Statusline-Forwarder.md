---
type: "[[task]]"
id: TASK-0117
aliases: ["TASK-0117"]
title: "Statusline forwarder — cost/context/rate-limit feed"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
parent: "[[FEAT-0019-Agent-Hook-Ingestion]]"
effort: "S"
depends: ["[[TASK-0114]]", "[[TASK-0115]]"]
blocks: []
related: []
tests: []
---

# Statusline forwarder

## Definition of Done
- [ ] A statusline command shipped with the app forwards Claude Code's statusline JSON (cost.total_cost_usd, lines added/removed, context_window.used_percentage, rate-limit windows) to the sidecar (`/api/agent-hook` with `hook_event_name: Statusline`).
- [ ] Registered via the same per-spawn settings injection as TASK-0115; user statusline config outside the cockpit unaffected.
- [ ] Sidecar stores the latest snapshot per workspace session; exposed in `/api/cockpit/state` for FEAT-0020 meters.

## Steps
- [ ] Small POSIX-sh/python forwarder script under the app resources; must echo a short status string so the in-terminal statusline stays useful.
- [ ] Include in generated settings; debounce forwarding (statusline fires frequently).
- [ ] Extend state payload + tests.

## Notes
Statusline is the richest cost/context surface (includes Pro/Max rate-limit windows) and needs no OTel infrastructure.
