---
type: "[[task]]"
id: TASK-0574
aliases: ["TASK-0574"]
title: "`STATUSES.md` stops attributing to `TESTING.md` a rule it does not state"
status: backlog
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
source: []
parent: "[[FEAT-0141-The-Contract-Says-It-Upstream]]"
effort: "S"
due: ""
depends: ["[[TASK-0573-Testing-Md-Five-Edits-Upstream]]"]
blocks: []
related: []
tests: []
---

# `STATUSES.md` stops attributing to `TESTING.md` a rule it does not state

## Definition of Done
- [ ] Line 144 no longer generalises *never removed, only deprecated* to any test

## Steps
- [ ] Edit upstream in the same commit as [[TASK-0573]]

## Notes

The misattribution is real today: `STATUSES.md` applies the rule to any test while `TESTING.md` scopes it to Tier 1 and Tier 2 and removes Tier 3. This is [[ISS-0238]]'s upstream ambiguity, and it resolves once nothing removes a check.
