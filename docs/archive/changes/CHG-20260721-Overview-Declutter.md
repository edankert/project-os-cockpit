---
type: "[[change]]"
id: CHG-20260721-Overview-Declutter
aliases: ["CHG-20260721-Overview-Declutter"]
title: "Overview is project-focused — agent surfaces dropped; session history moves to the ~agents screen"
status: merged
owner: user:edwin
created: 2026-07-21
updated: 2026-07-21
source: []
commit: ""
pr: ""
reviewed_by: "model:claude-opus"
review_date: 2026-07-21
review_verdict: approved
impacts: ["overview right pane", "overview feeds grid", "~agents screen (session history)"]
issues: []
features: ["[[FEAT-0022-Session-Insight-And-Traceability]]"]
related: ["[[TASK-0178]]", "[[FEAT-0032-Agents-Screen]]"]
---

# Overview declutter (session history → ~agents)

## Summary

The overview had accumulated agent-specific surfaces that now duplicate dedicated homes (rail dots, activity strip, attention inbox, the `~agents` fleet screen, session-detail pages). Per user request the overview is now purely project-focused: the right-pane "Agents" one-liner is gone (`buildNowSection` and its `updateOverviewNowCard` refresh removed; scope pane still shows Linked/Backlinks, project scope shows Pinned), and the feeds grid drops the "Agent sessions" column for a single full-width "Recent activity".

Session history was not lost — it relocated to the `~agents` fleet screen as a "Recent sessions" section below the fleet rows (the "fleet log" the screen's own code already anticipated). The agent-activity refresh that fed the sessions list now targets `~agents`. The live-session banner under the hero is unchanged.

## Verification

CDP: overview right pane has no agent line, the feeds area is single-column Recent activity; the `~agents` screen shows the fleet plus a populated "Recent sessions" list. tsc clean; full build OK.

Independent review (opus) approved; the one non-blocking finding — dead `.now-*`/`.ov-now` CSS orphaned by removing `buildNowSection` — was cleaned up.

Files: `desktop/src/renderer/{renderer.ts,renderer.css}`.
