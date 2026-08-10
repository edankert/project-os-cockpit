---
type: "[[task]]"
id: TASK-0367
aliases: ["TASK-0367"]
title: "Task children sort by status and fold when finished, so a 48-task feature stays readable"
status: done
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-10
source: ["[[FEAT-0085-The-Navigator-Shows-The-Structure-The-Record-Has]]"]
parent: "[[FEAT-0085-The-Navigator-Shows-The-Structure-The-Record-Has]]"
effort: M
due: ""
depends: ["[[TASK-0366-Tasks-Join-Their-Feature]]"]
blocks: []
related: ["[[FEAT-0056-Completed-Work-Ordering]]", "[[FEAT-0058-One-Shape-Per-Navigator]]"]
tests: []
---

# Task children sort by status and fold

## Definition of Done
- [x] Task children sort open-first by the comparator this phase already established — `openFirst` was **already applied** to the child list; tasks inherited it by joining, and no second comparator was written
- [x] Finished children fold behind the established affordance — `foldGroup(kids, NAV_GROUP_FOLD_LIMIT, hideCompleted)` and the `nav-more-btn` row, in both front doors
- [x] The 48-task feature and the median both read well — measured below, against the real corpus
- [x] Neither renderer declares its own completed-status set — both call the shared `foldGroup`/`completionRank`, unchanged

## Measured 2026-08-10 — the extremes, in this corpus

| | feature | children | toggle reads | folded to |
|---|---|---|---|---|
| largest | FEAT-0006 | 58 (all done) | `9 requirements · plan · 48 tasks` | 12 rows + `… 46 more` |
| median | FEAT-0075 | 6 | `2 requirements · plan · 3 tasks` | whole |
| smallest | FEAT-0005 | 2 | `1 requirement · 1 task` | whole |

## A defect this task introduced and fixed

[[TASK-0366]] put tasks in `children`, and **both renderers labelled the toggle by counting "everything that is not a plan" as a requirement.** FEAT-0006 would have read **"57 requirements · plan"**.

It was hand-written twice, so it is now guarded twice: `test_feature_children_summary_counts_tasks_separately` asserts both front doors count tasks, requirements and plans separately, and `test_feature_children_fold_on_volume_in_both_front_doors` asserts neither grew a second fold.

Worth recording as the shape rather than the instance: adding a member to a list that something else counts by *subtraction* is invisible at the call site. The count read correctly for months because the assumption held.

## Steps
- [x] Reuse the established comparator — found already applied to the child list; nothing to add
- [x] Apply the existing fold at child level, in both renderers
- [x] Render the depth in both `renderer.ts` and `cockpit.js` — both already rendered `children`; what changed is the label and the fold
- [x] Look at the real tree at both extremes before calling it done

## Notes
Two traps this phase has already fallen into, both applicable here:

**One comparator.** [[TASK-0267]] collapsed open-before-done to a single comparator precisely because a second one drifts. Task children must use it rather than sorting by a local status list.

**Compounding indents.** [[ISS-0093]]: no single indent value was wrong, but the band's 6, the group's 2 and the head's 8 compounded until a phase id sat 2px right of its own children. This adds a level, so it is the change most likely to reproduce that. The fix that held was that the *body* carries the indent, not the group.

Median 3 is the case to optimise for; 48 is the case that must not break.
