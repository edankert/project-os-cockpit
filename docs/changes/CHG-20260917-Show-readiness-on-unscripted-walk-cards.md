---
type: "[[change]]"
id: CHG-20260917-Show-readiness-on-unscripted-walk-cards
title: "Show readiness on unscripted walk cards"
status: merged
owner: unassigned
created: 2026-09-17
updated: 2026-09-17
source: ["[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]] A5/A8 fallback review"]
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

# Show readiness on unscripted walk cards

## Summary
An unscripted check with a declared platform readiness problem shows that reason on its walk card. A decision card offers only decision outcomes and does not offer Pass. A preparation card requires an explicit ready confirmation before its normal mark control appears. A malformed declaration becomes a visible decision warning and a payload error.

## Impact

- [[SUR-0004-The-Release-Walk]]: An unscripted release check now says why it cannot be performed on this platform before offering a verdict.

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
- [x] Include check-level readiness in the walk payload and fallback card. The live iOS payload shows eight Settings and backup decisions and still owes 327 checks.
- [x] Verify decision-only and preparation controls in rendered cards without writing a release verdict. The 82 passing renderer cases and ten bundle and agreement cases cover the change.
