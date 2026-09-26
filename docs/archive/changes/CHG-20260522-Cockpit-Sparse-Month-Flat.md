---
type: "[[change]]"
id: CHG-20260522-Cockpit-Sparse-Month-Flat
aliases: ["CHG-20260522-Cockpit-Sparse-Month-Flat"]
title: "Cockpit: skip weekly sub-buckets for sparse past months (<10 CHGs)"
status: merged
owner: user:edwin
created: 2026-05-22
updated: 2026-05-22
source: ["[[TASK-0041]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/cockpit.py"
  - "tests/test_cockpit.py"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[CHG-20260522-Cockpit-Changes-Hybrid-Buckets]]"]
---

# Cockpit: sparse past months render flat

## Summary
Past-month buckets with fewer than 10 CHGs no longer split into weekly sub-buckets — the items render directly under the month label. Months at or above the threshold (e.g. April 2026 with 56 items) keep the weekly date-range split from TASK-0040.

## Impact

### `cockpit.py`
- New constant `_CHG_PAST_MONTH_WEEK_SPLIT_MIN = 10`.
- `_changes_subgroups` past-month loop branches on item count: at or above the threshold → weekly sub-buckets; below → flat list inside the month.

### Tests
- `test_nav_payload_library_changes_sparse_past_month_is_flat` — synthesises CHG-20260105-One and CHG-20260112-Two and asserts the January 2026 bucket has empty `subgroups` and ≥2 items in `items`.
- 56 cockpit cases passing / 1 skipped (+1 net).

### Verified live (your-trainer/docs)
- April 2026 (56 items) — still 4 weekly sub-buckets.
- March / February / January 2026 (1 item each) — flat, no sub-buckets.

## Follow-ups
- [ ] Threshold is a single constant. If projects with very different change densities arrive, it could become per-project config or computed dynamically (e.g. `>= ceil(items_in_month / weeks_in_month * 2)`). Premature now.

## Documentation Coverage (All Types Considered)
- features: not-applicable
- requirements: not-applicable
- tasks: new ([[TASK-0041]])
- issues: not-applicable
- tests: updated (`tests/test_cockpit.py`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 40→41, focus.task → TASK-0041, metrics tasks_total 40→41 / tasks_done 34→35, items.changes addition)
