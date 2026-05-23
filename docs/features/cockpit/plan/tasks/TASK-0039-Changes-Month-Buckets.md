---
type: "[[task]]"
id: TASK-0039
aliases: ["TASK-0039"]
title: "Cockpit: bucket Changes group by calendar month (most-recent month open by default)"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-22
updated: 2026-05-23
source: []
implements: ["[[FEAT-0006]]", "[[REQ-0016]]"]
fixes: []
effort: S
due: ""
depends: ["[[TASK-0038]]"]
blocks: ["[[TASK-0040]]"]
related: []
tests: ["[[TST-0002]]"]
---

# TASK-0039 — Changes month buckets

## Definition of Done
- [x] The Changes rare-type group emits per-month subgroups (`YYYY-MM` keys, "May 2026" labels) sorted reverse-chronological.
- [x] Top-level Changes group has `items: []` (everything lives inside the month subgroups).
- [x] Most-recent month carries `default_open: true`; older months `default_open: false`.
- [x] JS `collapsibleGroup` honours `defaultOpen` — single localStorage map, semantics flip per group (bit set ≡ user diverged from default).
- [x] Tests cover the subgroup shape + default-open flags.

## Steps
- [x] Added `_CHG_DATE_RE` + `_MONTH_NAMES` constants and the helpers `_changes_month_subgroups`, `_extract_year_month`, `_format_month_label` in `cockpit.py`.
- [x] `_library_groups` special-cases `type_name == "change"` — clears `items` and emits `subgroups` from the helper.
- [x] `collapsibleGroup(opts)` accepts `opts.defaultOpen` (default `true`). When `false`, storage-bit-set means "user opened a default-closed group"; toggle handler computes the diverged-from-default state.
- [x] `renderSubgroup` passes `defaultOpen: group.default_open !== false` so non-Changes subgroups keep their existing always-open default.
- [x] Tests: `test_nav_payload_library_changes_grouped_by_month` asserts top-level items empty, subgroups sorted reverse-chronological, first subgroup `default_open=True`, others `False`, item type=change, key prefix correct.

## Notes
- Date extraction prefers the `CHG-YYYYMMDD-…` id, falling back to frontmatter `updated`/`created`. Unparsable records land in a `"unknown"` bucket.
- Live: your-trainer's 129 CHG notes split across 5 months (May 2026 = 70 items, April = 56, March/February/January = 1 each). Future tasks may add a per-month cap if any single month grows too large.
