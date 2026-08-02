---
type: "[[issue]]"
id: ISS-0084
aliases: ["ISS-0084"]
title: "A change note's id is its description, so a row renders the description twice and the CHG slug is the widest thing in the pane"
status: fixed
severity: low
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["Edwin 2026-08-02, on the new compact rows: 'Why are the change notes shown with the full file name and the others only show their ids and then the title?'"]
component: desktop-renderer
related: ["[[FEAT-0057-The-Record-Grammar]]"]
fixed_by: ["[[TASK-0271-One-Line-Rows-In-Both-Panes]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# Change ids print their description twice

## What

Every other note type carries a counter-allocated ID — `FEAT-0057`, `ISS-0084`, `TST-0023`. Changes do not. `LIFECYCLE.md` line 95 and `OBSIDIAN.md` line 28 both specify `CHG-YYYYMMDD-Short-Description`, so a change note's `id:` **is** a description:

```
id:    CHG-20260802-Completed-Work-Collapses
title: "Hide-completed became collapse-completed: nothing is removed by status any more…"
```

A row renders `id · title`. For a change that is the description twice, and the slug is three to five times the width of every other ID, so it dominates the column it shares.

## Why it only became visible now

The old two-line row put the ID on its own line with the title beneath, so a long ID cost width nobody was competing for. [[TASK-0271]] put them on one line, where the ID column's width is set by its widest member — and one `CHG-…` slug squeezes every title on the surface.

**A layout change made an existing inconsistency expensive.** The ID scheme was not wrong before and is not wrong now; it just stopped being free.

## Fix

Display-only: render the **date prefix** as the handle, `CHG-20260802`, and let the title carry the description — which is exactly the division of labour every other row already has. Nothing in the data changes; `id:` stays canonical, links and lookups are untouched.

Two changes on one day then share a display handle. That is acceptable and honest: the date *is* the identity granularity this scheme chose, and the title distinguishes them — which is the title's job.

## Not fixed here

Giving changes a counter. That is an upstream taxonomy decision affecting every project-os repo and a migration of 102 notes in this one; it is not worth doing to save a column's width.

## Evidence it is fixed

A change row shows `CHG-20260802` in the ID column, and its title reads as prose rather than a repeat.
