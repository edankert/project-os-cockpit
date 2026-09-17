---
type: "[[change]]"
id: CHG-20260916-Capture-build-and-image-at-a-walk-step
title: "Capture build and image at a walk step"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["Your Trainer FEAT-0122, criterion C5: capture evidence at the observation step with its build and platform"]
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

# Capture build and image at a walk step

## Summary
The walk collects a build identifier with a saved observation and allows a PNG to be attached at that step. A later comparison shows the note and picture with their originating release, platform, app state and build. Saving source evidence refreshes an already open comparison immediately.

## Impact

- [[SUR-0004-The-Release-Walk]]: The evidence prompt asks for the observed build and offers a PNG attachment. A later step displays the earlier note and screenshot beside its comparison.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated
- requirements: updated
- tasks: updated
- issues: not-applicable
- tests: updated
- workflows: not-applicable
- decisions: not-applicable
- risks: updated
- changes: new
- snapshot: updated

## Follow-ups
- [x] Save the build identifier with the source note, and require it before recording the source step.
- [x] File an optional PNG under the affected check through the existing attachment endpoint and show it at the comparison step. A verdict posted after attachment carries the PNG path in its ledger evidence references.
- [x] Verify restart, missing build, failed attachment and the later comparison in focused renderer and HTTP route tests.
- [ ] Confirm the capture and comparison in a real browser and Edwin's representative walk.
