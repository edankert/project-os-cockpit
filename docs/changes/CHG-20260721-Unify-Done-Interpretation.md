---
type: "[[change]]"
id: CHG-20260721-Unify-Done-Interpretation
title: "Phase progress boxes and hero counts now share one per-type done definition"
date: 2026-07-21
author: user:edwin
status: merged
related: ["[[TASK-0181]]", "[[TASK-0176]]", "[[FEAT-0023]]"]
reviewed_by: "opus-independent-review"
review_date: 2026-07-21
review_verdict: CLOSE
---

# CHG-20260721 — unify done interpretation across boxes and counts

## What changed

`stats_payload` (`src/project_os_cockpit/cockpit.py`) previously classified the phase progress boxes (the little squares and the per-phase progress bars) with a single, type-agnostic union set `DONE_PHASE_BUCKET`, while the hero/summary tiles counted "done" with per-type sets (`DONE_FEAT` / `DONE_TASK` / `DONE_REQ`). Those two definitions contained different statuses, so a filled box and the summary count could disagree for the same item — e.g. a status that is terminal for one type but not another (`accepted` is done for a requirement but not for a task) rendered a filled box while the matching count read it as not-done.

The bucketing now consults a single per-type map `DONE_BY_TYPE` (feature→`DONE_FEAT`, task→`DONE_TASK`, requirement→`DONE_REQ`, issue/test/risk/change/phase → their terminal vocabularies, union fallback for anything else) via a new `_is_done(record)` helper keyed on `note_type`. Both `phase_buckets` (progress bars) and `_status_bucket` (drill-down squares) call `_is_done`, and the summary tiles use the same per-type sets — so a box is filled **iff** the item also counts done. The old `DONE_PHASE_BUCKET` union was removed.

## Why

User report (2026-07-21): "docs completion is interpreted differently … the issue is in the rendering of the little boxes … the deferred option seems to be treated differently." Investigation confirmed project-os-cockpit's own boxes were already consistent (deferred renders as an empty/backlog box in both the project overview and phase views), but it surfaced a genuine latent divergence: any project using a status that the union treated as done but the per-type hero did not would see boxes and counts disagree. Unifying to one per-type source of truth removes that class of inconsistency entirely.

## Impact

- **Behaviour**: boxes and hero counts now agree by construction. For project-os-cockpit's actual statuses (feature: done/superseded/in-review/backlog; task: done/cancelled/deferred/backlog; requirement: verified/retired/implemented/draft; issue: fixed/closed/triage) the rendered boxes are **unchanged** — those statuses don't hit the old mismatch. Only projects that used a divergent status (e.g. `accepted`/`passing`/`complete`/`released` on a task) see a corrected (now-consistent) box.
- **API**: `/api/cockpit/stats` payload shape unchanged (`bucket` field values still `done`/`in_progress`/`backlog`); server-side only, no renderer change, no rebuild required — a sidecar reload picks it up.
- **Tests**: `tests/test_stats_scope.py::test_boxes_agree_with_hero_per_type` added — an `accepted` requirement buckets done while an `accepted` task buckets backlog, each matching its hero tile (would fail under the old union). Full suite: 222 passed, 1 skipped.

## Files

- `src/project_os_cockpit/cockpit.py` — added `DONE_ISS`, `DONE_BY_TYPE`, `_DONE_ANY`, `_is_done`; routed `phase_buckets` and `_status_bucket` through `_is_done`; removed `DONE_PHASE_BUCKET`.
- `tests/test_stats_scope.py` — added `test_boxes_agree_with_hero_per_type`.
