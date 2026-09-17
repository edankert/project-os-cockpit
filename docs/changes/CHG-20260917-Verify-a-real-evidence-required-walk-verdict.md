---
type: "[[change]]"
id: CHG-20260917-Verify-a-real-evidence-required-walk-verdict
title: "Verify a real evidence-required walk verdict"
status: merged
owner: unassigned
created: 2026-09-17
updated: 2026-09-17
source: ["[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"]
commit: ""
pr: ""
impacts: []
issues: []
features: ["[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0631-Verify-The-Guided-Walk]]"]
---

# Verify a real evidence-required walk verdict

## Summary
The real Your Trainer iOS FREE ride equivalence test will include a check cited by two steps whose later timed step requests saved evidence. It will prove that incomplete work and missing evidence write no verdict, then compare the completed step path with the direct check path on ledger copies.

## Impact

- No screen changed: this verifies the existing evidence requirement and verdict rule without changing the page.

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
- [x] Extend the current real-procedure test with the two-step TST-0370 and its saved evidence. The first step and a missing-evidence attempt at the second write no TST-0370 verdict.
- [x] Save the note and build, then replay the completed requests on copied ledgers. They match the direct check path and clear the selected checks without changing the source ledger.
- [x] Run the focused renderer suite, six copied-ledger tests, docs-first, documentation validator and `git diff --check`. All pass.

## Superseded in part, 2026-09-17

Your Trainer retired TST-0412 later the same day, and with it the ERG colour capture on the FREE ride's step 8. That real step no longer requests evidence, so the real-procedure test no longer checks the missing-evidence attempt on it. It still checks that the first of TST-0370's two steps writes no verdict. The evidence gate itself stays covered by the synthetic walk-page test ("requested evidence").
