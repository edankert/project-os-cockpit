---
type: "[[change]]"
id: CHG-20260917-Keep-guided-walk-readiness-quiet-after-start-and-add-step-picker
title: "Keep guided walk readiness quiet after start and add step picker"
status: merged
owner: user:edwin
created: 2026-09-17
updated: 2026-09-17
source: ["[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"]
commit: ""
pr: ""
impacts: ["[[SUR-0004-The-Release-Walk]]"]
issues: []
features: ["[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0629-Show-One-Walk-Action-And-Its-Readiness]]", "[[TASK-0631-Verify-The-Guided-Walk]]"]
---

# Keep guided walk readiness quiet after start and add step picker

## Summary
The release walk keeps the active warning beside its step while folding the session-wide warning list after the first action. Walk options has a short step picker so Edwin can reach a later action directly without recording a verdict. The isolated Electron walk resumed at step 12 with the list folded and jumped to step 20 without changing a mark.

## Impact

- [[SUR-0004-The-Release-Walk]]: Once a session is underway, its full readiness list folds away; Walk options lets the rider jump to a named step while the active step still shows its own warning.

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
- changes: updated
- snapshot: updated

## Follow-ups
- [x] Add a focused renderer test for step jumping and folded readiness.
- [x] Rebuild and verify the isolated Electron route. The focused renderer suite passes 80 cases.
- [x] Run the documentation gates. Docs-first and the validator pass; the full desktop suite and 47 focused Python walk tests pass with local server access.
