---
type: "[[change]]"
id: CHG-20260810-Features-Is-The-One-Structural-Tree
title: "Tasks hang under the feature they serve, the Tasks view retires from both front doors, and the quick palette stops listing every task twice"
status: merged
reviewed_by: ""
review_date: ""
review_verdict: ""
date: 2026-08-10
owner: user:edwin
component: [cockpit-payload, desktop-renderer, browser-cockpit]
related: ["[[FEAT-0085-The-Navigator-Shows-The-Structure-The-Record-Has]]", "[[PHASE-022-Completed-Work-Gets-Quieter]]", "[[REL-0001-The-Human-Has-Levers]]"]
---

# Features is the one structural tree

## What changed

`phase → feature → requirements · plan · tasks`. Tasks joined the child list they always belonged in, and the flat **Tasks** view — 356 rows, 282 of them `done`, none `doing`, phase appearing nowhere — is retired from both front doors.

```
Features  ▸ PHASE-030 · Obligations go home
             FEAT-0089  9 requirements · plan · 48 tasks   ← toggle
Tasks     (retired; a stored preference migrates to Features)
```

## Three things the plan did not predict

**The fleet writes three edge fields, not one.** The task template says `parent`, and 379 of this repo's 384 tasks use it. `your-trainer` carries **387 tasks on `implements`** and 3 on `feature`. The cockpit renders twelve repos, so a `parent`-only resolver would have orphaned 387 tasks in one of them. `parent` wins where a note carries several; the filesystem is consulted only for a note that declares nothing — 5 of 384 here, all of them sitting under the feature directory that names them.

**Both renderers labelled the toggle by subtraction.** "Everything that is not a plan is a requirement" read correctly for months, and became wrong the moment tasks joined the list: FEAT-0006 would have announced *"57 requirements · plan"*. Adding a member to a list that something else counts by subtraction is invisible at the call site.

**The quick palette would have doubled.** `flattenNavItems` descends into `children`, so `features` alone now carries all 384 tasks; `QUICK_CORPUS_MODES` listed `tasks` as well. Removing it deduplicated Cmd+P without losing reachability.

## Verified against real corpora

Nested + unattached == every task note, in three repos rather than the fixture alone:

| repo | nested | unattached | total |
|---|---|---|---|
| project-os-cockpit | 384 | 0 | 384 |
| your-trainer | 647 | 128 | 775 |
| your-health | 263 | 13 | 276 |

`your-trainer`'s 128 are honest: 102 declare nothing and live outside `features/`, 14 name an `ISS-*` as their parent, 12 name a note that does not exist.

## What stayed

`nav_payload(mode="tasks")` is **still served** — [[FEAT-0008]]'s API-stability commitment, and the same call TASK-0204 made for `active` and `recent`. A retired button is a UI decision; deleting an endpoint is a contract change.

The overview's Tasks stat tile was repointed to Features rather than left pointing at a mode with no button — [[ISS-0063]] is that exact bug.

## Paths

- `src/project_os_cockpit/cockpit.py` — `_task_feature_id`, `_task_child_item`, task children and the `unattached-tasks` group in `_features_groups`
- `desktop/src/renderer/renderer.ts` — `childrenSummary`, child folding, `RETIRED_NAV_MODES`, the stat tiles, `QUICK_CORPUS_MODES`
- `src/project_os_cockpit/static/cockpit.js` — the same summary and fold, `NAV_MODES`
- `desktop/src/renderer/index.html` — the Tasks button
- `tests/` — four new payload assertions, two renderer-parity guards, and two existing guards rewritten to assert the property rather than the mechanism

## Restart required

Mode 3 is a built bundle. Live after the desktop app restarts.
