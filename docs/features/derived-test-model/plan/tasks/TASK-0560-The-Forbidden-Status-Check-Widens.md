---
type: "[[task]]"
id: TASK-0560
aliases: ["TASK-0560"]
title: "The forbidden-status check ranges over `command:`, not over `level: acceptance`"
status: done
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: []
parent: "[[FEAT-0139-The-Suite-Is-The-Verdict]]"
effort: "M"
due: ""
depends: []
blocks: []
related: []
tests: []
---

# The forbidden-status check ranges over `command:`, not over `level: acceptance`

## Definition of Done
- [ ] A note with a `command:` holding `ready`/`passing`/`failing` is an error
- [ ] `last_run:`/`exit_code:` on the same population is an error
- [ ] The domain goes from 89 notes to 139, measured

## Steps
- [ ] Widen `ACCEPTANCE_FORBIDDEN_STATUSES`' predicate from the level to the command
- [ ] Add the evidence-field sibling check
- [ ] Register both in `FLAT_STATUS_TABLES` so a typo cannot silently disarm them

## Notes

The rule already exists over 64% of its domain and cannot say why it stops. This is a domain widening, not a new constraint — which is also why it needs no warning tier if [[TASK-0562]] lands first and leaves zero violations.
