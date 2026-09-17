---
type: "[[change]]"
id: CHG-20260916-Correct-completed-walk-observations
title: "Correct completed walk observations"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["Your Trainer FEAT-0122, criterion B8: correct a saved step after its check leaves the owed walk"]
commit: ""
pr: ""
impacts: ["[[SUR-0004-The-Release-Walk]]"]
issues: []
features: ["[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0630-Record-And-Resume-Walk-Observations]]", "[[RISK-0010-Saved-Walk-Observations-Can-Outlive-Their-Source]]"]
---

# Correct completed walk observations

## Summary
The walk now keeps a correction route for an observation after its check receives a clearing ledger verdict. The server rebuilds the step from the current authored procedure, so changed instructions cannot reuse an older observation.

## Impact

- [[SUR-0004-The-Release-Walk]]: A completed check remains available in a correction section with its current action and earlier result. A correction keeps the ledger history and returns a newly failed check to the owed walk.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated
- requirements: not-applicable
- tasks: updated
- issues: not-applicable
- tests: updated
- workflows: not-applicable
- decisions: not-applicable
- risks: updated
- changes: new
- snapshot: updated

## Follow-ups
- [x] Keep a scoped index of checks this browser completed. Rebuild only those checks from current procedure text when they leave the owed set.
- [x] Show the current step and prior verdict in a correction section. Reopen a newly failed or questioned check in the main walk.
- [x] Prove restart, changed instructions, duplicate suppression and ledger history with focused tests.
- [ ] Confirm the correction section in a real browser and complete Edwin's human walk.
