---
type: "[[change]]"
id: CHG-20260917-Explain-unavailable-survey-when-a-platform-has-no-prior-release
title: "Explain unavailable survey when a platform has no prior release"
status: merged
owner: unassigned
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
related: ["[[TASK-0631-Verify-The-Guided-Walk]]"]
---

# Explain unavailable survey when a platform has no prior release

## Summary
The release walk tells the rider when its changed-screen survey is unavailable because the platform has no previous release to compare with. It does not imply that no screen changed, and the owed checks remain walkable.

## Impact

- [[SUR-0004-The-Release-Walk]]: When a platform has no earlier release, the survey states that a changed-screen comparison cannot be made yet.

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
- [x] Render an accurate empty-survey message when the platform has no comparison release.
- [x] Test the message in the 80-case focused renderer suite and inspect the isolated Electron iOS page. It has zero survey cards and 327 owed checks.
- [x] Run the cockpit documentation gates after recording the evidence. Docs-first, validator and `git diff --check` pass.
