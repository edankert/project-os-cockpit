---
type: "[[feature]]"
id: FEAT-0053
aliases: ["FEAT-0053"]
title: "A contribution grid you can click into, and a permanent way to reach History"
status: done
phase: "[[PHASE-016-The-Overview-Answers-Questions]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["Edwin 2026-07-30, on FEAT-0052: 'is there a way to get to the history page without having to press that hidden button at the bottom of the page?'"]
goal: "Replace the History tile's 13-week sparkline with a year-long contribution grid whose days are destinations, and give History a permanent entry point in the workspace rail."
requirements: []
tasks:
  - "[[TASK-0258-Activity-Grid-Payload]]"
  - "[[TASK-0259-Contribution-Grid]]"
  - "[[TASK-0260-History-In-The-Rail]]"
release: ""
related: ["[[FEAT-0052-History-Timeline]]"]

---

# History navigation

## Goal

Two complaints from the same place: History exists and there is no way in, and the tile's sparkline shows thirteen weeks you cannot interact with.

One answer to both — a **contribution grid** where a day is a destination. Clicking it goes to History at that day, which makes the surface discoverable by construction rather than by finding a link. Plus a rail button so History is reachable from anywhere.

## Brief plan

1. **[[TASK-0258]]** — `activity_payload`: per-day transition and commit counts across the whole history, cached on HEAD.
2. **[[TASK-0259]]** — the grid, replacing the sparkline, with the three corrections that make it honest on a young repo.
3. **[[TASK-0260]]** — the rail button.

## Acceptance

- The grid shows a rolling year; days before the first commit are visibly *absent*, not empty.
- Intensity is relative to this repo's own active days: its 199-transition day and its 6-transition day differ visibly.
- Clicking a day lands on that day in History.
- Year controls appear only when history spans more than a year — on this repo, none.
- History is reachable from the rail from any page.
- The sparkline is gone.

## Scope

- In: the payload, the grid, the rail button.
- Out: a History nav mode in the top bar (those are left-pane modes and History has no listing); a per-day page (the grid scrolls the timeline instead).


## Done 2026-07-30

Every acceptance criterion verified in the running app.

- **Rolling year, pre-history absent** — 371 cells: **286 absent, 69 empty**, 16 lit. The two are visibly different, which is the correction that stops a young repo's graph reading as neglect.
- **Relative intensity** — the 16 active days spread **5 / 4 / 3 / 4** across the four steps. Under GitHub's fixed buckets all sixteen would be step 4.
- **Clicking a day lands on it** — the 2026-05-07 cell lands on the 2026-05-07 divider.
- **No year controls** — one year of history, nothing to navigate to.
- **History reachable from the rail** — from `~overview`, one click to `~history`.
- **Sparkline gone.**

## The bug the live pass caught

[[TASK-0259]]'s note warned that *"a cell that does not navigate is the sparkline again"*. The first cut navigated to `~history` and scrolled — which only works for dates inside the loaded window. The grid spans all history; the page loads 60 commits. **Clicking 2026-05-07 landed on 2026-07-28** and said nothing.

Anchoring the window at the date rather than scrolling into it makes the day loaded by construction. Guarded, and mutation-verified.

Worth recording that the task note named the failure mode and the first implementation walked into it anyway. Naming a trap makes it cheap to *diagnose*, not impossible to *commit*.

## Owed

- **The grid is mode 3 only**, like the History tile it sits in. Mode 1 still has the old three tiles — the same debt [[FEAT-0052]] recorded, unchanged.
- **`~history/<date>` has no back-to-now control** other than the rail button. Sufficient, and worth watching if anyone uses date navigation heavily.
