---
type: "[[issue]]"
id: ISS-0099
aliases: ["ISS-0099"]
title: "The activity feed renders a change note's full slug id, which wraps to four lines and breaks the row rhythm — ISS-0084's shortening never reached this surface"
status: fixed
severity: low
phase: "[[PHASE-016-The-Overview-Answers-Questions]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-05
source: ["Edwin 2026-08-05: 'activity in this phase (change notes are not displayed correctly)' — project-os-cockpit PHASE-006"]
component: desktop-renderer
related: ["[[ISS-0084-Change-Ids-Print-Their-Description-Twice]]"]
fixed_by: ["[[TASK-0271-One-Line-Rows-In-Both-Panes]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# Change ids unshortened in the activity feed

## What

PHASE-006's *Activity in this phase*, captured:

```
2026-05-25   CHANGE   CHG-20260525-      OS notification on agent `waiting` — first
                      Agent-             FEAT-0012 task; FEAT-0012 plan + 5 remaining
                      Waiting-           tasks drafted
                      Notification
```

Every other row's id column holds a short handle — `TASK-0174`, `ISS-0001`. A change note's id **is** a description (`CHG-YYYYMMDD-Short-Description`, LIFECYCLE.md line 95), so in a fixed narrow column it wraps to four lines and the row stands three times taller than its neighbours.

## Why

[[ISS-0084]] established the fix — render the date prefix as the handle, `CHG-20260525`, and let the title describe — and applied it to the nav rows, the context pane, the focus chip and, later, the review desk. **The activity feed was not among the ten call sites found**, because its rows are built from a different payload with their own id element.

That is the fourth surface this shortening has had to reach, which is the finding as much as the wrap is: the transform lives in a helper any renderer must remember to call.

## Fix

Call `shortNoteId` here too — and, since this is the fourth straggler, make the guard enumerate id-rendering sites rather than naming the ones known at the time, so a fifth surface fails the suite by existing.

## Evidence it is fixed

The activity feed's change rows are one line, and the guard fails when any surface renders a raw note id.


## Fixed 2026-08-05

Both feed builders now pass ids through `shortNoteId` with the full value in `title`, and `.ov-feed-id` never wraps. The activity rows measure 35px each, and the change row reads `CHG-20260525` beside its neighbours' `TASK-0174`.

## What the guard found that I had not

The issue asked for a guard that **enumerates** id-rendering sites rather than naming the known ones. Written that way, it immediately failed on two sites nobody had reported — the Now board's cards and the agent detail's work rows — making them the **fifth and sixth** surfaces this shortening had to reach.

Then mutation testing found the guard's own hole: the `title="…"` exemption was applied **per line** rather than per occurrence, so one `title="${escapeHtml(id)}"` exempted the visible `${escapeHtml(id)}` beside it, and reverting the visible one passed. Fixed to test each occurrence.

A guard written to enumerate finds what a guard written to remember cannot — and a guard's own exemptions need mutating too.