---
type: "[[task]]"
id: TASK-0366
aliases: ["TASK-0366"]
title: "Tasks join their feature's children in the nav payload, after the requirements and the plan"
status: backlog
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-09
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
- [ ] `_features_groups` emits task children on each feature item, after the requirement children and the plan child
- [ ] Tasks are matched to features by `parent`, resolved the same way `_requirement_feature_ids` resolves its edge — not by directory path
- [ ] An `Unattached tasks` group carries every task whose `parent` is not a feature, mirroring `Unattached requirements`
- [ ] Existing children are byte-identical in content and order; a test asserts requirements-then-plan is unchanged
- [ ] Both renderers receive the new depth without either restating the ordering

## Steps
- [ ] Build a `tasks_by_feature` map alongside the existing `reqs_by_feature`, tracking attached paths the same way
- [ ] Append task children after `_plan_child_item`, preserving the stated reason for the plan sorting last
- [ ] Add the orphan group after `unattached-reqs`, keyed `unattached-tasks`
- [ ] Extend `tests/test_cockpit_payloads.py` (or the nearest suite): child order, orphan capture, and the count identity — every task appears exactly once across the whole payload

## Notes
Measured 2026-08-09: 355 of 358 tasks carry a `parent` feature; 80 of 83 features carry tasks; median 3, max 48. The three exceptions are `TASK-0000` (the template), `TASK-0065` and `TASK-0045`.

**The orphan group is not optional.** Without it those two real tasks become unreachable the moment the Tasks view retires — which is precisely the failure `Unattached requirements` was added to prevent, and the count identity in the DoD is what catches it.

Path-based matching would be wrong even though tasks live under `docs/features/<slug>/plan/tasks/`: [[ISS-0062]] is what happens when a lookup uses the directory instead of the declared edge.
