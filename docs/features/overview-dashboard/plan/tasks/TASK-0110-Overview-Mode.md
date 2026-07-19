---
type: "[[task]]"
id: TASK-0110
aliases: ["TASK-0110"]
title: "Overview mode + dashboard renderer"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
parent: "FEAT-0017"
---

# Overview mode + dashboard renderer

## Definition of Done
- [ ] `overview` added to `NAV_MODES`; new top-bar button with a
      chart-bar SVG.
- [ ] Selecting overview hides the ws-nav-content + fetches
      `/api/cockpit/stats` + mounts the dashboard in `#doc-view`.
- [ ] 4 tiles rendered as pure SVG (hero strip, phase bars,
      4-donut status mix, activity histogram + recent feed).
- [ ] Clicking a recent-CHG item navigates the centre pane and
      switches mode back to whatever it was before overview.
- [ ] Re-renders when the user switches workspace (the dashboard
      is per-project).
