---
type: "[[task]]"
id: TASK-0112
aliases: ["TASK-0112"]
title: "Health badge + drift panel UI — chrome badge, error list deep-linked to offending notes"
status: done
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-17
parent: "FEAT-0018"
depends: ["[[TASK-0111]]"]
---

# Health badge + drift panel

## Definition of Done
- [x] Top-bar badge with three states: healthy (green), drifting (red, with error count), unavailable (grey). Uses the existing status palette; no new colour semantics.
- [x] Clicking the badge opens a drift panel listing each violation: `[CODE]`, message, and — when an ID is present — a link that navigates the centre pane to the offending note via the existing resolver.
- [x] Badge updates live from the SSE validation event (no reload, no polling).
- [x] Panel state (open/closed) survives soft live-reload.

## Notes
- Follow the pattern of the existing agent-state/tab-state chrome elements for placement and SSE wiring.

## Verification (2026-07-17)
- Implemented in the mode-1 cockpit chrome: `cockpit-health-slot` in the header (templates.py, next to the follow-agent slot), `mountHealthBadge` / `renderHealthPanel` / `cockpit:validation` SSE listener in `static/cockpit.js`, badge + panel styles in `static/cockpit.css` reusing `--status-active` / `--status-blocked` / `--status-default` tokens. Deep links are plain `<a href>` rows using the server-resolved `url` (index resolver), so the existing click interceptor swaps the centre pane in place; panel open state persists in localStorage and the panel element is untouched by the soft-reload path (which only re-renders the panes).
- Server payload/SSE behaviour behind the badge is covered by [[TST-0016]]; the served HTML carrying the health slot was verified by manual curl. Visual interaction pass (badge flip on live drift, row navigation) pending human review — parent feature held at `in-review`.
