---
type: "[[feature]]"
id: FEAT-0017
aliases: ["FEAT-0017"]
title: "Overview dashboard — project stats in diagrams"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
goal: "A single 'Overview' view that gives a one-glance read of the project: hero counts (features / tasks / issues / tests / risks / last activity), progress per phase, status mix per type, weekly activity histogram, recent change feed."
related: ["[[FEAT-0015-Cockpit-IA-V2]]"]
tasks: ["[[TASK-0109]]", "[[TASK-0110]]"]
---

# Overview dashboard

## Goal
A 6th mode in the top bar (📊) that switches the centre pane to a
project-wide dashboard rather than a single note. Four tiles:

1. **Hero strip** — big-number cells for features, tasks, issues,
   tests, risks, last activity.
2. **Progress by phase** — stacked bar per phase (done /
   in-progress / backlog).
3. **Status donuts** — 4-up donuts for features / tasks / issues /
   requirements broken down by status.
4. **Activity** — weekly histogram of CHG counts (last 12 weeks) +
   a list of the 10 most recent CHGs (click → navigate).

## Scope
- New server endpoint `/api/cockpit/stats` (TASK-0109) returns one
  aggregated payload computed from the index. No new index passes;
  everything is already cached.
- New `overview` nav mode (TASK-0110) renders the dashboard into
  the centre pane (replacing the doc-view) when active. Clicking
  any item in the dashboard or switching to another mode restores
  normal doc viewing.

## Out of scope
- Time-series of state changes across history (we'd need a real
  event log; CHG-created dates are good-enough for the histogram).
- Drill-down filtering / interactive charts. v1 is a read-only
  glance.

## Acceptance
- Click 📊 in the top bar → centre pane mounts the dashboard.
- Hero numbers match what's in SNAPSHOT.yaml's `metrics`.
- Phase bars total the same task count visible in the Tasks mode.
- Activity histogram has 13 columns (12 weeks back + this week);
  CHG dates parsed from the `CHG-YYYYMMDD-…` ID.
- Recent CHG feed items navigate the centre pane to that CHG note
  on click; the mode flips back to whatever it was so the rest of
  the cockpit is usable.
