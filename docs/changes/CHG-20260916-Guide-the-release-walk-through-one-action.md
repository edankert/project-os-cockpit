---
type: "[[change]]"
id: CHG-20260916-Guide-the-release-walk-through-one-action
title: "Guide the release walk through one action"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["Your Trainer FEAT-0122, 2026-09-16: implement and test the focused release walk"]
commit: ""
pr: ""
impacts: ["[[SUR-0004-The-Release-Walk]]"]
issues: []
features: ["[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[REQ-0066-The-Release-Walk-Keeps-Observation-Context]]", "[[RISK-0010-Saved-Walk-Observations-Can-Outlive-Their-Source]]"]
---

# Guide the release walk through one action

## Summary
The release walk now shows one changed screen or one current action with its expected result and a direct way to record it. It retains declared preparation, readiness warnings, saved observations and the context needed to resume. Completed checks can be corrected, and source observations can carry build and PNG evidence. FEAT-0151 remains doing while corpus and human acceptance work continues.

## Impact

- [[SUR-0004-The-Release-Walk]]: The page opens at the next screen or step, shows the action and result together, and keeps details available when needed.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: new
- requirements: new
- tasks: new
- issues: not-applicable
- tests: new
- workflows: updated
- decisions: not-applicable
- risks: new
- changes: new
- snapshot: updated

## Follow-ups
- [x] Build the focused page and preserve observation state across a restart. The focused Node walk tests cover restart, evidence notes, source edits and failed writes.
- [x] Verify that page and text sheet agree for Android and iOS, and exercise pass, partial, fail, question and correction on ledger copies.
- [x] Attach evidence to its source action and support correction after a check leaves the owed payload. Focused renderer, API and attachment-route tests cover these paths.
- [ ] Complete a real browser and human walk.
