---
type: "[[task]]"
id: TASK-0276
aliases: ["TASK-0276"]
title: "The completed divider appears only where a group's own name does not say it is finished — issues and features, not tasks"
status: done
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["[[FEAT-0058-One-Shape-Per-Navigator]]"]
parent: "[[FEAT-0058-One-Shape-Per-Navigator]]"
effort: M
depends: ["[[TASK-0275-Settled-Groups-Are-Collapsed-Cards]]"]
blocks: []
related: ["[[ISS-0086-The-Rollup-Hid-The-Taxonomy]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# The divider, where names do not say finished

## Definition of Done

- `features` and `issues` render a `Completed · N` divider holding their settled groups as collapsed cards. `tasks` does **not** — `Done` already says it.
- The rule is expressed as a property of the view, named for **why** it holds, not as a list of modes that happen to want one.
- Inside the divider, a phase expands to its features and a feature to its requirements and plan — three levels, each shut until asked for.
- The divider keeps [[ISS-0086]]'s correction: it is a **heading**, defaulting open and persisted, never a door that hides which phases exist.

## Notes

Measured now: tasks has 3 settled groups of 5, issues 4 of 7, features 17 of 18. Only the last two need telling apart from live work by anything other than their names.

## Verification

The tasks navigator has no divider and the other two do; every phase, status and severity is still named without expanding anything.
