---
type: "[[task]]"
id: TASK-0112
aliases: ["TASK-0112"]
title: "Health badge + drift panel UI — chrome badge, error list deep-linked to offending notes"
status: backlog
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
parent: "FEAT-0018"
depends: ["[[TASK-0111]]"]
---

# Health badge + drift panel

## Definition of Done
- [ ] Top-bar badge with three states: healthy (green), drifting (red, with error count), unavailable (grey). Uses the existing status palette; no new colour semantics.
- [ ] Clicking the badge opens a drift panel listing each violation: `[CODE]`, message, and — when an ID is present — a link that navigates the centre pane to the offending note via the existing resolver.
- [ ] Badge updates live from the SSE validation event (no reload, no polling).
- [ ] Panel state (open/closed) survives soft live-reload.

## Notes
- Follow the pattern of the existing agent-state/tab-state chrome elements for placement and SSE wiring.
