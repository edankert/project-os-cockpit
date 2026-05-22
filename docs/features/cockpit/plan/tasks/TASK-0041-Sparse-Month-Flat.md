---
type: "[[task]]"
id: TASK-0041
aliases: ["TASK-0041"]
title: "Cockpit: skip weekly sub-buckets for sparse past months (<10 CHGs)"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-22
updated: 2026-05-22
source: []
implements: ["[[FEAT-0006]]", "[[REQ-0016]]"]
fixes: []
effort: XS
due: ""
depends: ["[[TASK-0040]]"]
blocks: []
related: []
tests: ["[[TST-0002]]"]
---

# TASK-0041 — Sparse past months render flat

## Definition of Done
- [x] Past-month bucket renders items directly under the month label (no week sub-buckets) when item count is below `_CHG_PAST_MONTH_WEEK_SPLIT_MIN` (10).
- [x] Months at or above the threshold keep the weekly date-range split from TASK-0040.
- [x] Test asserts a sparse past month has empty `subgroups` and items in `items`.

## Steps
- [x] Added `_CHG_PAST_MONTH_WEEK_SPLIT_MIN = 10` constant in `cockpit.py`.
- [x] `_changes_subgroups` past-month loop branches on item count: `>=10` → weekly subs; `<10` → flat.
- [x] `test_nav_payload_library_changes_sparse_past_month_is_flat` — synthesises two CHGs in January 2026 and asserts the month bucket has no subgroups and >=2 items inline.

## Notes
Live (your-trainer): January / February / March 2026 each have 1 CHG and now render flat. April 2026 (56 items) keeps the weekly split. Threshold is a single constant — adjust if a project's typical month density differs.
