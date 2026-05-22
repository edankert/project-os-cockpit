---
type: "[[task]]"
id: TASK-0040
aliases: ["TASK-0040"]
title: "Cockpit: hybrid Changes buckets (current week / last week / earlier this month + past months with weekly sub-buckets)"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-22
updated: 2026-05-22
source: []
implements: ["[[FEAT-0006]]", "[[REQ-0016]]"]
fixes: []
effort: M
due: ""
depends: ["[[TASK-0039]]"]
blocks: []
related: []
tests: ["[[TST-0002]]"]
---

# TASK-0040 — Hybrid Changes buckets

## Definition of Done
- [x] Current-month section is FLAT (no "May 2026" wrapper) with up to three top-level subgroups:
  - **Current week** (Mon–Sun including today). Default open.
  - **Last week** — rendered only when items exist earlier than last week in the current month.
  - **Earlier this month** — rendered only when items exist older than current week; absorbs last week's items when no even-older content (so "Last week" never appears alone).
- [x] Past months emit one bucket per month, label `"Month Year"` (e.g. `"April 2026"`), all collapsed by default.
- [x] Past-month buckets nest **weekly sub-buckets** with date-range labels, clipped to month boundaries (`Apr 1–5` / `Apr 6–12` / … / `Apr 27–30`). All collapsed by default.
- [x] ISO Mon–Sun week boundaries.
- [x] Tests cover the conditional bucket rendering + nested past-month structure.

## Steps
- [x] Replaced `_changes_month_subgroups` with `_changes_subgroups` — emits the hybrid structure.
- [x] New helpers: `_past_month_week_subgroups`, `_format_week_range`, `_record_change_date`, `_record_sort_key`.
- [x] `_MONTH_ABBR` table for week-range labels (`Apr`, `May`, …).
- [x] CHG date regex extended to capture the day (`CHG-(\d{4})(\d{2})(\d{2})`) so we can build `_dt.date` from the id.
- [x] Tests: `test_nav_payload_library_changes_hybrid_buckets` asserts no current-month wrapper, only Current week defaults open, every subgroup carries the stacked layout.

## Notes
- "Current week" is suppressed entirely when there are no items dated this week. The first visible bucket on your-trainer today is "Last week" (2 items) followed by "Earlier this month" (68).
- Past-month week labels handle clipping: `Apr 1–5` (partial start week), `Apr 27–30` (partial end week), `Apr 6–12` (full ISO week).
- Same `defaultOpen` storage semantics from TASK-0039 — bit set ≡ user diverged from default.
- No bucketing applied to items lacking a usable date; they fall into "Earlier this month" so they remain reachable.
