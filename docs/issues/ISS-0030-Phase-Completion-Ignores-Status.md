---
type: "[[issue]]"
id: ISS-0030
aliases: ["ISS-0030"]
title: "Phase completion is inferred from task counts and ignores the phase's own status, so a superseded phase reads live; live phases also sort by `order:` rather than active-first"
status: fixed
severity: medium
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
component: ui
source: ["user-report:2026-07-26"]
design: "[[DES-0001-Overview-Redesign]]"
related: [ISS-0029, ADR-0005, ADR-0008]
tests: []
---

# Phase completion ignores the authored status

## Problem

Two defects, reported together because they show up in the same list.

**1. `superseded` phases read as live.** `phaseIsComplete()` derived completion purely from task arithmetic:

```ts
const total = t.done + t.in_progress + t.backlog;
return total > 0 && t.done === total;
```

In `your-trainer`, PHASE-012 (iOS Launch) was **superseded by PHASE-019 (iOS Parity)** — the phase note carries `superseded_by:`, and ADR-0008 added `superseded` to the phase taxonomy precisely to record work absorbed into a successor. The predicate never looked at `p.status`, so the authored decision "this phase was replaced" had no effect on how the phase rendered.

**2. Live phases sorted by `order:` only.** `PHASE-019` (`active`) rendered *below* four `planned` phases because its order number is higher. The one phase where work is actually happening was the fifth row.

## What was already correct

Worth recording, because the report also named tasks. Superseded **tasks** were already handled end to end — `DONE_TASK` contains `superseded`, `is_done_status('task','superseded')` is `True`, and all **72** of them fold into the `done` bucket (655) rather than `backlog`. The task symptom was a *consequence* of defect 1: with PHASE-012 in the live band, its 104 completed tasks read as outstanding work.

## Fix

- `phaseIsComplete()` now returns true when the phase's own status is terminal, falling back to the count heuristic otherwise. It reuses **`isCompletedStatus()`** — the shared `statuses.py → cockpit.js → renderer.ts` vocabulary that already contains `done`, `superseded` and `cancelled` — rather than keeping a local list, which is the mistake ISS-0023 was filed about. `deferred` is deliberately absent from that set: parked work is still wanted (ADR-0005).
- New `sortLivePhases()` ranks `active`/`in-progress`/`doing` above `planned`/`backlog`/`draft`, keeping `order:` as the tiebreak via a stable index.
- Both are applied to the **centre-pane accordion and the left Scope pane**, which share the predicate — so the two panes cannot disagree.

## Verified against `your-trainer`

```
IN FLIGHT (new order)          COMPLETED
  PHASE-019  iOS Parity  active   … PHASE-012 (superseded) now here
  PHASE-015  planned
  PHASE-016  planned
  PHASE-018  planned
  PHASE-999  planned
```
