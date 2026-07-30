---
type: "[[plan]]"
title: "Plan — History"
status: done
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
implements: ["[[FEAT-0052-History-Timeline]]"]
related: ["[[PHASE-017-History-As-Document-Events]]"]
---

# Plan

1. **[[TASK-0255]]** — the payload. Everything else waits on it, and it is where the accuracy questions live.
2. **[[TASK-0256]]** — the overview tile, replacing three. Depends on 0255.
3. **[[TASK-0257]]** — the full view. Depends on 0255, independent of 0256.

## The decision this rests on

**A row is a status transition, not a note touch.** Measured: the phase-hygiene commit touched 20 notes and changed 4 statuses; the other 16 had a `phase:` field corrected. A touch-based list makes bookkeeping the largest event of the day, which is the opposite of the stated goal.

## Three things to watch

**A commit with no rows must not vanish.** Today `commits_payload` flags commits that touched no notes — [[FEAT-0022]]'s guardrail. Under a transition-based list such a commit produces nothing, so it has to survive as a flagged divider. This is the single most likely way to build this wrong.

**Deleting three tiles is the point, not a side effect.** If History lands beside Activity, Changes and Commits, the overview has four history surfaces and we have done the thing [[PHASE-010]] and [[PHASE-012]] each closed by undoing.

**A transition is only as good as its parse.** `+status:` in a diff is a *line added*, which for a new file means "created at this status" rather than "moved to it". Those are different events and the payload should distinguish them, not blur them into one arrow.
