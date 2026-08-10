---
type: "[[task]]"
id: TASK-0376
aliases: ["TASK-0376"]
title: "Requirement approval and the acceptance entry point surface on the feature they concern"
status: backlog
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[FEAT-0088-Features-Carries-Its-Own-Judgments]]"]
parent: "[[FEAT-0088-Features-Carries-Its-Own-Judgments]]"
effort: M
due: ""
depends: ["[[TASK-0369-The-Obligation-Registry]]"]
blocks: []
related: ["[[FEAT-0085-The-Navigator-Shows-The-Structure-The-Record-Has]]", "[[DES-0006-The-Acceptance-Desk]]"]
tests: []
---

# Approval and acceptance on the feature

## Definition of Done
- [ ] A `draft` requirement is marked as awaiting approval where it already sits, nested under its feature
- [ ] A feature at `acceptance: requested` is marked and carries the acceptance run's entry point
- [ ] `changes-requested` on a feature or task is visible in the tree
- [ ] All three counted in the view's badge, from the registry
- [ ] Approving writes `approved` through the guarded transition and satisfies **no** close-out gate

## Steps
- [ ] Mark obligated rows in `_features_groups`' items and children
- [ ] Add the acceptance entry point on the feature row, per [[DES-0006]]
- [ ] Coordinate with [[FEAT-0085]]: whichever lands second must not restate the other's ordering or status vocabulary

## Notes
[[ADR-0007]]'s separation is load-bearing and easy to lose here: the desk writes `plan-accepted`, close-out writes `approved`, and the validator accepts any non-`changes-requested` value — so a plan stamp landing on a gate-bearing note silences a gate it never satisfied. That is why `GATE_BEARING_TYPES` refuses by type rather than by string, and this task must not widen it.
