---
type: "[[change]]"
id: CHG-20260522-Cockpit-Changes-Month-Buckets
aliases: ["CHG-20260522-Cockpit-Changes-Month-Buckets"]
title: "Cockpit: bucket Changes group by calendar month"
status: merged
owner: user:edwin
created: 2026-05-22
updated: 2026-05-22
source: ["[[TASK-0039]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/cockpit.py"
  - "src/project_os_cockpit/static/cockpit.js"
  - "tests/test_cockpit.py"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[CHG-20260522-Cockpit-Library-Changes-Group]]"]
---

# Cockpit: Changes month buckets

## Summary
Tames the Changes rare-type group: CHG notes are now bucketed into per-month subgroups ("May 2026", "April 2026", …) sorted reverse-chronological. The most-recent month opens by default; older months stay collapsed unless the user opens them. Persisted across reloads.

## Impact

### `cockpit.py`
- New constants `_CHG_DATE_RE` (`^CHG-(\d{4})(\d{2})\d{2}`) and `_MONTH_NAMES`.
- New helpers `_changes_month_subgroups(index, records)`, `_extract_year_month(record)`, `_format_month_label(ym)`.
- `_library_groups` special-cases `type_name == "change"`: clears the top-level `items` list and replaces it with `subgroups` from the helper. Other rare-types unchanged.

### `cockpit.js`
- `collapsibleGroup(opts)` accepts `opts.defaultOpen` (defaults to `true`). When `false`, storage semantics flip: a set bit means the user opened a default-closed group rather than collapsing a default-open one. Toggle handler computes `nowDiverged = defaultOpen ? !isOpen : isOpen` so a single localStorage map serves both modes.
- `renderSubgroup` forwards `group.default_open !== false` so non-Changes subgroups continue to default open and the topmost month opens by default.

### Tests
- `test_nav_payload_library_changes_grouped_by_month` — asserts `items: []`, subgroup keys sorted reverse-chronological, `default_open` true on the first subgroup and false on the rest, items carry `type: "change"` and CHG ids.
- 55 cockpit cases passing / 1 skipped (replaces the previous `test_nav_payload_library_includes_changes_group`).

### Verified live (your-trainer/docs)
- Changes group splits into 5 buckets: May 2026 (70 items, open) / April 2026 (56, closed) / March / February / January 2026.

## Follow-ups
- [ ] If a month exceeds ~50 entries, the bucket itself becomes hard to scan. Could layer in a per-bucket "show recent N + expand" cap as a follow-up.
- [ ] Unparsable change records land in a `"unknown"` bucket — labelled as `"unknown"` raw. Rare in practice; if it shows up regularly, format the label more nicely.

## Documentation Coverage (All Types Considered)
- features: not-applicable
- requirements: not-applicable
- tasks: new ([[TASK-0039]])
- issues: not-applicable
- tests: updated (`tests/test_cockpit.py`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 38→39, focus.task → TASK-0039, metrics tasks_total 38→39 / tasks_done 32→33, items.changes addition)
