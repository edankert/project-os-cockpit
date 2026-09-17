---
type: "[[change]]"
id: CHG-20260916-Show-screen-names-on-walk-actions
title: "Show screen names on walk actions"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["Your Trainer FEAT-0122 B5: the current action names its screen; standalone Chrome render of the Android walk, 2026-09-16"]
commit: ""
pr: ""
impacts: ["[[SUR-0004-The-Release-Walk]]"]
issues: []
features: ["[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0629-Show-One-Walk-Action-And-Its-Readiness]]"]
---

# Show screen names on walk actions

## Summary
The current walk action names its screen in words. A browser render of Your Trainer's Quick Ride step previously showed `SUR-0033` in the card heading, although the surface note calls it Quick Ride cockpit. The heading now reads Quick Ride cockpit at a narrow browser width.

## Impact

- [[SUR-0004-The-Release-Walk]]: The current action heading shows a readable screen name while its source screen id remains available for linking.

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
- [x] Sync the corrected shared generator and verify the current payload and renderer heading. The upstream, cockpit tool copy, bundled module and Your Trainer copy are byte-identical; the cockpit agreement fixture and a narrow Chrome render show Quick Ride cockpit with `SUR-0033` retained as the source id.
