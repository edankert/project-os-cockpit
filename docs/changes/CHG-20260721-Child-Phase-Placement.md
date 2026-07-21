---
type: "[[change]]"
id: CHG-20260721-Child-Phase-Placement
title: "Phase drill-down nests a task under its parent feature only when they share a phase"
date: 2026-07-21
author: user:edwin
status: merged
related: ["[[TASK-0182]]", "[[TASK-0181]]", "[[FEAT-0023]]"]
reviewed_by: "opus-independent-review"
review_date: 2026-07-21
review_verdict: CLOSE
---

# CHG-20260721 — child phase placement agrees across views

## What changed

`stats_payload` (`src/project_os_cockpit/cockpit.py`) built `children_by_parent_id` by grouping every task/requirement/issue under its `parent:` feature, ignoring the child's own `phase:`. The project overview renders a feature's children inside that feature's phase section, so a task whose own phase differs from its parent's phase was rendered under the parent's phase — while a scoped phase page filters items by their own resolved phase (`_in_scope`) and therefore omitted the same task. Result: the item appeared on the project overview but was missing from that phase's page (and was duplicated — it also showed loose under its own phase on the overview).

The nesting now attaches a child to its parent feature only when `(_phase_id_of(child) or "unphased") == (_phase_id_of(parent) or "unphased")`. A child explicitly moved to a different phase is no longer nested under its parent's phase section; the existing `loose_by_phase` logic already surfaces it under its own phase. Both views now place the item identically.

## Why

User report (2026-07-21): deferred TASK-0045 was visible on the project page but not on the embedded-terminal phase page; same for TASK-0065 under desktop-shell. Both were deliberately parked in `PHASE-999-Future` (via an earlier "move uncompleted tasks to the future phase" sweep) while their parent features stayed in PHASE-004/PHASE-005. The overview kept nesting them under their parents' phases; the phase pages filtered them out by their own phase — an inconsistency.

## Impact

- **Behaviour**: a task whose `phase:` matches its parent feature's phase (the common case — tasks inherit the parent's phase when they set none) nests exactly as before. Only a child with an explicit, *different* phase changes: it now appears once, as loose under its own phase, in every view (project overview + each scoped phase page) instead of being duplicated under the parent's phase and absent from that phase page. For this repo, TASK-0045/TASK-0065 now live solely under PHASE-999 in all views.
- **API**: `/api/cockpit/stats` payload shape unchanged; server-side only, no renderer change, no rebuild — a sidecar reload picks it up.
- **Tests**: `tests/test_stats_scope.py::test_child_phase_placement_agrees_across_views` added — a parked task (parent in PHASE-001, task in PHASE-002) is loose under PHASE-002 and never nested under its parent in PHASE-001, on both the unscoped overview and the scoped pages; a phase-inheriting sibling still nests. Full suite: 223 passed, 1 skipped.

## Files

- `src/project_os_cockpit/cockpit.py` — `children_by_parent_id` now requires a shared phase between child and parent feature.
- `tests/test_stats_scope.py` — added `test_child_phase_placement_agrees_across_views`.
