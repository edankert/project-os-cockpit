---
type: "[[task]]"
id: TASK-0669
aliases: ["TASK-0669"]
title: "The features navigator lists open unattached tasks with the work in flight, and open before finished"
status: done
phase: ""
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["Found 2026-10-14 when TASK-0668, an open task whose parent is an issue, made tests/test_completed_work_ordering.py fail on the live corpus"]
parent: "[[FEAT-0056]]"
effort: "S"
due: ""
depends: []
blocks: []
related: ["[[TASK-0268]]", "[[TASK-0668-A-Refused-Write-Closes-Its-Connection]]"]
tests: []
---

# Open unattached tasks sort with the work in flight

A task that belongs to no feature, such as one whose parent is an issue, appears in the features navigator's "Unattached tasks" group. That group is always placed last, after every finished phase, and its tasks are listed by ID. So an open task in it sits below forty finished phases, and below any finished task with a lower number. Every other group puts open work first ([[TASK-0268]]).

**How it was found.** [[TASK-0668-A-Refused-Write-Closes-Its-Connection]] is open with an issue as its parent. Two tests that read this repository's own notes failed as soon as it existed: `test_the_features_navigator_orders_its_items_open_first` (TASK-0668 follows a completed task) and `test_the_phase_in_flight_leads_the_features_navigator` (an in-flight group sorts after finished ones). No open unattached task had existed since those tests were written, so neither had run against the case.

**Cause.** `_features_groups` in `src/project_os_cockpit/cockpit.py` sorts the unattached tasks by ID only and appends their group after the sorted phase groups, without the open-first sort or the band rank the phase groups get.

## Definition of Done

- [x] The unattached tasks are sorted open-first, keeping ID order within each half.
- [x] The group is placed by the same band rank as a phase group: with open work, after the phases in flight; with none, last as before.
- [x] A test on a synthetic corpus fails without the fix, so the guard does not depend on this repository happening to have an open unattached task.
- [x] The two live-corpus tests pass.

## Built, 2026-10-14

`_features_groups` sorts the unattached tasks with `_open_first` and inserts their group after the phase groups whose band rank is the same or lower, using `_phase_group_rank(None, tasks)`: in flight when any is open, finished otherwise, where it stays last as before. `tests/test_completed_work_ordering.py::test_an_open_unattached_task_sorts_with_the_work_in_flight` builds a corpus where ID order and open-first disagree; it fails without the fix and passes with it. The two live-corpus tests pass with TASK-0668 open. The renderer reads the group by key only (`renderer.ts`, near line 15063), so moving it changes nothing else.
