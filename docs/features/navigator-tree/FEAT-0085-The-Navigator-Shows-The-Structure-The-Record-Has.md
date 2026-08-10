---
type: "[[feature]]"
id: FEAT-0085
aliases: ["FEAT-0085"]
title: "The navigator shows the structure the record has — tasks join their feature beside its requirements and plan, and the Tasks view retires"
status: done
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-10
source: ["Edwin 2026-08-09: 'how about we group tasks directly under features (sorted by status) and make the phases in features selectable'"]
goal: "Make Features the one structural tree — phase → feature → requirements · plan · tasks — so a task is read where it belongs instead of in a flat status list, and retire the Tasks view whose 356 rows were 79% finished work with no phase anywhere in them."
requirements: []
tasks:
  - "[[TASK-0366-Tasks-Join-Their-Feature]]"
  - "[[TASK-0367-Task-Children-Sort-By-Status-And-Fold]]"
  - "[[TASK-0368-The-Tasks-View-Retires-In-Both-Front-Doors]]"
release: ""
related: ["[[FEAT-0058-One-Shape-Per-Navigator]]", "[[FEAT-0056-Completed-Work-Ordering]]", "[[FEAT-0084-One-View-Vocabulary]]", "[[PHASE-029-One-Tool-Two-Front-Doors]]"]
tests: []
---

# The navigator shows the structure the record has

## Goal

Two views describe one hierarchy and neither shows it. **Features** groups by phase and nests requirements and the plan, but stops before the work. **Tasks** lists 356 tasks in six status groups — `Done · 282`, `Backlog · 65`, `Deferred · 2`, nothing at `doing` — with phase appearing nowhere and no way to see which feature a task serves.

The record already has the edge: **355 of 358 tasks carry a `parent` feature**, and 80 of 83 features carry tasks. Median 3 tasks per feature, maximum 48. The navigator simply never drew it.

## Scope

**In:**

- Task children on the feature item in `_features_groups`, **after** the requirements and the plan
- Task children sorted by status, with finished ones folded by this phase's existing rules
- An `Unattached tasks` group for tasks whose `parent` is not a feature, by exact analogy with the `Unattached requirements` group that already exists
- Retiring the Tasks view **in both front doors**, with the stored-preference migration that `RETIRED_NAV_MODES` already provides

**Out — and preserved exactly as they are:**

- The phase grouping, the `Unphased` group, the `Unattached requirements` group, open-features-first ordering, and the requirements-before-plan child order with its stated reason. Nothing currently surfaced in Features is displaced by this; tasks are added to the child list, not substituted into it.
- **The phase scope.** Asked for in the same breath and deliberately deferred — see the phase note. Folding finished phases already leaves 1 active and 7 planned visible, so this change may remove the need.
- Any change to what a task *is*, or to `parent` semantics.

## Why the payload does most of the work

`_features_groups` is server-side and **both** renderers consume `/api/cockpit/nav?mode=features`. So the tree lands in the browser cockpit and the shell from one change, and only the extra render depth is done twice. That is also what makes retiring the Tasks view safe in both at once: mode 1 does not lose task visibility, it gains a better version of it — which is the difference between this and the `recent` divergence [[FEAT-0084]] exists to clean up.

## Acceptance

- [x] A feature's children are its requirements, then its plan, then its tasks — the existing two kinds unchanged in content and order
- [x] Task children sort by status with finished ones folded; a 48-task feature stays readable
- [x] Tasks whose `parent` is not a feature appear in an `Unattached tasks` group; no task is reachable only through the retired view
- [x] The `Unphased` and `Unattached requirements` groups still behave exactly as before
- [x] The Tasks view is gone from both front doors, and a stored preference pointing at it migrates rather than stranding the user
- [x] Both renderers draw the new depth; neither restates the ordering or the completed-status set locally (the [[ISS-0023]] rule)

## Links

- Phase: [[PHASE-022-Completed-Work-Gets-Quieter]] — reopened for this leg; the goal there is this rule one level deeper
- Paths: `src/project_os_cockpit/cockpit.py` (`_features_groups`, `_task_records`, `_tasks_groups`), `desktop/src/renderer/renderer.ts`, `src/project_os_cockpit/static/cockpit.js`, both stylesheets

## Closed 2026-08-10

Three tasks, three findings the notes did not predict:

1. **The fleet writes three edge fields, not one.** `parent` here — but **387 tasks in `your-trainer` use `implements`**, and a `parent`-only resolver would have orphaned them in a corpus this tool renders.
2. **Both renderers labelled the child toggle by subtraction** — everything not a plan was a requirement. FEAT-0006 would have read *"57 requirements · plan"*. Guarded in both front doors now.
3. **The quick palette would have listed every task twice**, because `flattenNavItems` descends into `children`. Removing `tasks` from its corpus deduplicated it, and its guard was rewritten to assert reachability rather than mode names.

Verified against three real corpora rather than the fixture alone: nested + unattached equals every task note in `project-os-cockpit` (384), `your-trainer` (775) and `your-health` (276).
