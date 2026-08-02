---
type: "[[feature]]"
id: FEAT-0058
aliases: ["FEAT-0058"]
title: "Every navigator is a live section plus collapsed cards, and a completed divider appears only where the group names do not already say finished"
status: done
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["Edwin 2026-08-02, specifying all four navigators: 'I would like to see something similar as on the review page, but each phase having the possibility of opening them up. And then an expanded or collapsed completed section (maybe this is shown using a card similar as in the right panel) at the bottom with all phases… Tasks do not need a completed section since the done/cancelled and superseded states already are completed sections… Issues/risks do need a different mechanism and a completed section… The Review section does not have a completed section at the moment, a little of an odd one out.'"]
goal: "Give all four navigators one shape — live work above, finished work as collapsed cards — with the completed divider appearing only where a group's own name does not already say it is finished."
requirements: []
tasks:
  - "[[TASK-0275-Settled-Groups-Are-Collapsed-Cards]]"
  - "[[TASK-0276-The-Divider-Where-Names-Do-Not-Say-Finished]]"
  - "[[TASK-0277-Changes-Requested-Is-Not-Finished]]"
release: ""
related: ["[[FEAT-0057-The-Record-Grammar]]", "[[ISS-0086-The-Rollup-Hid-The-Taxonomy]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# One shape per navigator

## The rule

Every navigator becomes **a live section, then finished work as collapsed cards** — the right pane's grammar, which is the one Edwin keeps pointing at.

A completed **divider** appears only where a group's own name does not already say it is finished:

| view | group names | says it? | shape |
|---|---|---|---|
| **Tasks** | `Done`, `Cancelled`, `Superseded` | **yes** | no divider — each is a collapsed card in place |
| **Issues** | `Critical`, `High`, `Medium` | no — that is severity | divider, then a collapsed card per severity |
| **Features** | `PHASE-007 · Agent instrumentation` | no | divider, then every finished phase, expandable to features and on to requirements and plans |
| **Review** | `approved`, `accepted` | — | divider, then a card per verdict |

Edwin specified the first three view by view; the fourth follows from the same rule. **Three special cases collapsed into one principle** — which is the difference between a design and a list of preferences.

## Depth

A finished phase opens to its features; a feature opens to its requirements and its plan. Three levels, each shut until asked for, so a finished phase costs one line until it does not.

## Review, and the thing the data changed

`Reviewed · 82` already **was** review's completed section — it only lacked the shape. But 10 of those 82 are `changes-requested`: a reviewer asked for work and nothing has recorded it happening.

Filing that under "reviewed" is the same error the old Hide-completed switch made — **a terminal-looking label on something still owed.** Those 10 are promoted into their own live section; `Completed · 2` then holds `approved · 70` and `accepted · 2`.

## Out of Scope

- **The verdict vocabulary.** `accepted` and `approved` are both live in the corpus and [[ISS-0069]] already covers that; this feature reads them, it does not reconcile them.
- **The context pane.** It has been the model throughout and does not change.

## Verification

Each navigator measured in the running app: what is above the fold, what a finished group costs, and that nothing has become unreachable.
