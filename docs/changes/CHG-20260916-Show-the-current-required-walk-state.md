---
type: "[[change]]"
id: CHG-20260916-Show-the-current-required-walk-state
title: "Show the current required walk state"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["Your Trainer FEAT-0122 A3 and C2: the active step should name the state to restore after a tier, ride or equipment change"]
commit: ""
pr: ""
impacts: ["[[SUR-0004-The-Release-Walk]]: A later action keeps the last authored required-state reminder until the procedure changes it."]
issues: []
features: ["[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0629-Show-One-Walk-Action-And-Its-Readiness]]"]
---

# Show the current required walk state

## Summary
The current walk card keeps showing the last authored required state until the procedure changes it. The reminder tells Edwin what to restore after leaving the page; it does not claim the app state has been verified.

## Impact

- [[SUR-0004-The-Release-Walk]]: A resumed action names the tier, ride or equipment state the procedure last required.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated
- requirements: not-applicable
- tasks: updated
- issues: not-applicable
- tests: updated
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new
- snapshot: updated

## Follow-ups
- [x] Sync the shared generator and test that the active card shows the latest authored state after an omitted step and after a later transition.
