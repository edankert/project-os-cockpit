---
type: "[[change]]"
id: CHG-20260724-Implemented-Status-Rank
title: "Cockpit ranks and colours `implemented` with the done family instead of falling through to the default rank"
status: merged
owner: user:edwin
created: 2026-07-24
updated: 2026-07-24
source: []
commit: ""
pr: ""
impacts: ["src/project_os_cockpit/templates.py", "src/project_os_cockpit/static/base.css", "tests/test_index.py"]
issues: []
features: []
reviewed_by: ""
review_date: ""
review_verdict: ""
related: []
---

# `implemented` joins the done band

## Summary

`implemented` is a delivered-work status in the project-os requirement taxonomy ("built, not yet formally verified"), but the cockpit had no entry for it in `STATUS_RANK`. It fell through to `STATUS_RANK_DEFAULT` (50), stranding it between the backlog and done bands in every sorted list, and it was absent from `COLLAPSED_BY_DEFAULT` so its group stayed open. It also had no status-chip colour rule, so it rendered in the default ink rather than the done colour.

It now ranks at 62 — after `done`/`fixed`/`merged`/`published` (60), before `verified`/`passing` (65) — collapses by default like the rest of the done family, and gets `--status-done` as its chip colour. A regression test pins the ordering invariant and the collapse membership.

## Impact

- Requirement notes at `implemented` now sort with delivered work rather than mid-list, and their groups collapse by default in the nav and overview surfaces.
- Purely presentational; no API, schema, or data change.

## Documentation Coverage (All Types Considered)

- features: not-applicable
- requirements: not-applicable
- tasks: not-applicable (small taxonomy-alignment fix; documented via this change note per LIFECYCLE "Mandatory Automated Documentation")
- issues: not-applicable
- tests: updated (`tests/test_index.py::test_implemented_status_sorts_and_collapses_with_the_done_family`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new
- snapshot: not-applicable (no tracked item state changed)

## Follow-ups

- [ ] The same fix exists in the upstream vendored copy (`tools/cockpit/` in project-os) — keep the two in step at the next template sync.
