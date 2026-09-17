---
type: "[[change]]"
id: CHG-20260917-Show-expired-excuses-in-the-release-walk-review
title: "Show expired excuses in the release walk review"
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
related: ["[[TASK-0631-Verify-The-Guided-Walk]]"]
---

# Show expired excuses in the release walk review

## Summary
Review results lists every check the current walk owes. An excuse that expired when the previous release ledger sealed is named as earlier history. In the isolated Electron walk, the Android summary now lists all 39 owed checks; it previously hid ten, including one with a more recent rerun reason.

## Impact

- [[SUR-0004-The-Release-Walk]]: Review results lists every currently owed check and labels an expired earlier excuse clearly.

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
- [x] Use the current owed rows in Review results and explain expired excuses.
- [x] Verify the 39-check Android summary in the isolated Electron walk. The focused renderer suite passes 80 cases.
- [x] Run the documentation gates. Docs-first and the validator pass; the full desktop suite and 47 focused Python walk tests pass with local server access.
