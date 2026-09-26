---
type: "[[task]]"
id: TASK-0236
aliases: ["TASK-0236"]
title: "Render the plan as a child row under its feature in the Features mode"
status: done
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
parent: "[[FEAT-0046-Plans-On-The-Feature]]"
effort: S
depends: ["[[TASK-0235-Plan-Lookup-By-Path]]"]
blocks: ["[[TASK-0245-Drop-Relocated-Groups]]"]
related: ["[[TASK-0030-Nested-Requirements]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# TASK-0236 — Plan nested under its feature

## Definition of Done
- [ ] `_features_groups` attaches the resolved plan to the feature item's `children`
- [ ] The row carries the plan's status when it has one and omits the chip when it does not
- [ ] A feature with no plan renders exactly as before — no empty child, no placeholder
- [ ] Clicking the row opens the plan

## Steps
- [ ] In `_features_groups`, call `_feature_plan` per feature record
- [ ] Build the child item with a `plan` type so the existing type icon applies
- [ ] Order it after the requirement children (requirements say what, the plan says how)
- [ ] Test: a feature with a typed plan, one with an untyped plan, one with none

## Notes

Requirements already nest via `children` ([[TASK-0030]]) and the renderer handles them generically, so no renderer change should be needed. Confirm that during implementation rather than assuming it — if the child rendering is requirement-specific, this task grows.
