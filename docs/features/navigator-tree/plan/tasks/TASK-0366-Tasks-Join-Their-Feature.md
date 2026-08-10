---
type: "[[task]]"
id: TASK-0366
aliases: ["TASK-0366"]
title: "Tasks join their feature's children in the nav payload, after the requirements and the plan"
status: done
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-10
source: ["[[FEAT-0085-The-Navigator-Shows-The-Structure-The-Record-Has]]"]
parent: "[[FEAT-0085-The-Navigator-Shows-The-Structure-The-Record-Has]]"
effort: M
due: ""
depends: []
blocks: ["[[TASK-0367-Task-Children-Sort-By-Status-And-Fold]]", "[[TASK-0368-The-Tasks-View-Retires-In-Both-Front-Doors]]"]
related: []
tests: []
---

# Tasks join their feature

## Definition of Done
- [x] `_features_groups` emits task children on each feature item, after the requirement children and the plan child — evidence: `test_nav_payload_features_attaches_tasks_after_requirements_and_plan`
- [x] Tasks are matched to features by their **declared edge**, resolved the way `_requirement_feature_ids` resolves its own — **amended, see below**: three fields, not one, and a documented path fallback for notes that declare nothing
- [x] An `Unattached tasks` group carries every task whose declared parent is not a feature — evidence: `test_nav_payload_features_orphan_tasks_group`
- [x] Existing children are byte-identical in content and order; the child-order test asserts requirements → plan → tasks
- [x] Both renderers receive the new depth without either restating the ordering — payload only; *rendering* the depth is [[TASK-0367]]
- [x] **Count identity**: nested + unattached == every task note — evidence: `test_nav_payload_features_every_task_appears_exactly_once`, and verified against three real corpora

## Measured 2026-08-10 — two amendments to the DoD above

**One field became three.** The DoD said match by `parent`. This repo agrees — 379 of 384 tasks use it and nothing else. **`your-trainer` does not**: 660 tasks on `parent`, **387 on `implements`**, 3 on `feature`. The cockpit renders twelve repos, so a `parent`-only resolver would have orphaned 387 tasks in a corpus this tool is expected to show. `parent` takes precedence where a note carries more than one.

**"Not by directory path" gained a fallback, for notes that declare nothing.** Of 384 task notes here, 3 carry no frontmatter at all (the ISS-0067 population, visible only because `_task_records` sweeps the path) and 2 carry frontmatter with no feature field. **All five sit under a `features/<slug>/plan/tasks/` directory** — resolving strictly by declaration would have sent 5 of 5 to an orphan group whose entire population had an obvious home.

The DoD's intent is preserved exactly: a declared edge is never overridden by the filesystem, which is the ISS-0062 hazard. A task that *declares nothing* is a different case, and it is the same rule `_task_records` already states for the type and `_feature_plan` applies to plans.

### Verified against real corpora, not only the fixture

| repo | nested | unattached | total | identity |
|---|---|---|---|---|
| project-os-cockpit | 384 | 0 | 384 | ✓ |
| your-trainer | 647 | 128 | 775 | ✓ |
| your-health | 263 | 13 | 276 | ✓ |

`your-trainer`'s 128 are honest: **102** declare nothing and live in `docs/tasks/` rather than under a feature; **14** name an `ISS-*` as their parent; **12** name a note that does not exist.

### Recorded for later, not fixed here

Those **14 tasks parented to an issue** are not *unattached* — they are attached to something that is not a feature. The DoD's rule places them correctly and the label understates them. Worth revisiting when the Issues view gains its own tree; deliberately not widened into this task.

## Steps
- [x] Build a `tasks_by_feature` map alongside the existing `reqs_by_feature`, tracking attached paths the same way
- [x] Append task children after `_plan_child_item`, preserving the stated reason for the plan sorting last
- [x] Add the orphan group, keyed `unattached-tasks`
- [x] Extend `tests/test_cockpit.py` (the suite that already owns `_features_groups`): child order, the three declaring fields, orphan capture, and the count identity

## Notes
Measured 2026-08-09: 355 of 358 tasks carry a `parent` feature; 80 of 83 features carry tasks; median 3, max 48. The three exceptions are `TASK-0000` (the template), `TASK-0065` and `TASK-0045`.

**The orphan group is not optional.** Without it those two real tasks become unreachable the moment the Tasks view retires — which is precisely the failure `Unattached requirements` was added to prevent, and the count identity in the DoD is what catches it.

Path-based matching would be wrong even though tasks live under `docs/features/<slug>/plan/tasks/`: [[ISS-0062]] is what happens when a lookup uses the directory instead of the declared edge.
