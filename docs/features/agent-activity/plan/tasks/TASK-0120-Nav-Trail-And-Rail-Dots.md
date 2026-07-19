---
type: "[[task]]"
id: TASK-0120
aliases: ["TASK-0120"]
title: "Live nav attribution trail + needs-input rail-dot vocabulary"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
parent: "[[FEAT-0020-Agent-Activity-Surfaces]]"
effort: "S"
depends: ["[[TASK-0114]]", "[[TASK-0118]]"]
blocks: []
related: []
tests: []
---

# Live nav trail + rail dots

## Definition of Done
- [ ] When the agent edits a note under `docs/`, the matching nav/right-pane row flashes an attribution badge ("agent, just now") within SSE latency; badge decays after a short interval.
- [ ] needs-input is visually distinct from busy and waiting on rail dots, dock badge, and OS notification copy.

## Steps
- [ ] Key attribution by rel-path from tool events; badge + decay timer in nav renderers.
- [ ] Extend rail dot classes + CSS; update notification copy in the poller.

## Notes
Distinct from SSE soft-reload (which refreshes content but attributes nothing).
