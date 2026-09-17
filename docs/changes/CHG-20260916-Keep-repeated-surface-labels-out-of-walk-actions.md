---
type: "[[change]]"
id: CHG-20260916-Keep-repeated-surface-labels-out-of-walk-actions
title: "Keep repeated surface labels out of walk actions"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["Your Trainer FEAT-0122 B1: the active action repeats its screen name and raw SUR id after the heading already names the screen"]
commit: ""
pr: ""
impacts: ["[[SUR-0004-The-Release-Walk]]: The active action begins with what to do when its authored screen label already appears in the step heading."]
issues: []
features: ["[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0629-Show-One-Walk-Action-And-Its-Readiness]]"]
---

# Keep repeated surface labels out of walk actions

## Summary
The active walk action should begin with the instruction, since the card heading already names its screen. Keep the source line and check expectation unchanged while removing its repeated screen label from the visible action.

## Impact

- [[SUR-0004-The-Release-Walk]]: The active action omits a repeated screen label and source id when the card heading already shows the screen.

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
- [x] Show that the active card drops only the leading screen label and leaves the authored source, later action text and exact check expectation intact.
