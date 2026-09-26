---
type: "[[change]]"
id: CHG-20260522-Cockpit-Changes-Hybrid-Buckets
aliases: ["CHG-20260522-Cockpit-Changes-Hybrid-Buckets"]
title: "Cockpit: hybrid Changes buckets (current week / last week / earlier this month + past months with weekly sub-buckets)"
status: merged
owner: user:edwin
created: 2026-05-22
updated: 2026-05-22
source: ["[[TASK-0040]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/cockpit.py"
  - "tests/test_cockpit.py"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[CHG-20260522-Cockpit-Changes-Month-Buckets]]"]
---

# Cockpit: hybrid Changes buckets

## Summary
Restructures the Changes group from a flat month-bucketed list into a hybrid that surfaces recent activity at the top with relative labels, and falls back to month + week date-range buckets for older content. No wrapper around the current month.

## Structure

Current month (no wrapper) — emit only the buckets that have content:
- **Current week** (Mon–Sun including today). Default open.
- **Last week** — only when items exist earlier than last week in the current month.
- **Earlier this month** — only when items older than current week exist; absorbs last week's items if no even-older content (so "Last week" never appears alone with redundant "Earlier this month").

Past months — one bucket per month with weekly sub-subgroups inside:
- **`Month Year`** label (e.g. `April 2026`). Collapsed by default.
- Each contains weekly sub-buckets with date-range labels (`Apr 1–5`, `Apr 6–12`, …, `Apr 27–30`) clipped to month boundaries. All collapsed by default.

## Impact

### `cockpit.py`
- `_CHG_DATE_RE` now captures the day (`CHG-(\d{4})(\d{2})(\d{2})`) so we can build a full date.
- New `_MONTH_ABBR` table for compact week labels.
- `_changes_month_subgroups` replaced by `_changes_subgroups` — implements the hybrid structure described above.
- New helpers `_past_month_week_subgroups`, `_format_week_range`, `_record_change_date`, `_record_sort_key`.
- Items lacking a usable date fall into "Earlier this month" so they remain reachable.

### Tests
- `test_nav_payload_library_changes_hybrid_buckets` — asserts no current-month wrapper, only "Current week" defaults open, all subgroups use stacked layout, all items carry type=`change`.
- Replaces the previous `test_nav_payload_library_changes_grouped_by_month`.
- 55 cockpit cases passing / 1 skipped.

### Verified live (your-trainer/docs, today 2026-05-22)
- No `Current week` bucket (no items this week).
- `Last week` (2 items) + `Earlier this month` (68) — both rendered because both qualify per the rule.
- `April 2026` (collapsed) splits into 4 week sub-buckets: `Apr 27–30` (13) / `Apr 20–26` (34) / `Apr 13–19` (8) / `Apr 6–12` (1).
- `March 2026`, `February 2026`, `January 2026` — 1 item each, single week sub-bucket per month.

## Follow-ups
- [ ] If a single weekly bucket within a past month exceeds ~50 items, layer in a "show recent N + expand" cap. Not a problem today (April 20–26 is the densest at 34).
- [ ] Past-month bucket counts could be surfaced in the label ("April 2026 · 56") as a navigation cue without expanding.

## Documentation Coverage (All Types Considered)
- features: not-applicable
- requirements: not-applicable
- tasks: new ([[TASK-0040]])
- issues: not-applicable
- tests: updated (`tests/test_cockpit.py`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 39→40, focus.task → TASK-0040, metrics tasks_total 39→40 / tasks_done 33→34, items.changes addition)
