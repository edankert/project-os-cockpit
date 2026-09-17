---
type: "[[change]]"
id: CHG-20260917-Compare-a-real-walk-procedure-with-direct-check-verdicts
title: "Compare a real walk procedure with direct check verdicts"
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

# Compare a real walk procedure with direct check verdicts

## Summary
The guided walk verification will compare verdicts from actual Your Trainer FREE ride procedure steps with verdicts from marking those same checks directly. The test will use copied Android and iOS ledger data and will not write to a release ledger.

## Impact

- No screen changed: this adds verification for existing verdict behavior and does not alter the release walk page.

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
- [x] Generate current Android and iOS FREE ride procedure payloads from Your Trainer and compare real step verdict requests with direct check verdict requests. The two selected checks agree on each platform.
- [x] Replay both request paths on disposable working-ledger copies. Each selected check clears, and the source ledgers remain byte-identical.
- [x] Run the focused renderer suite, all six copied-ledger tests, docs-first, the documentation validator and `git diff --check`. All pass.
