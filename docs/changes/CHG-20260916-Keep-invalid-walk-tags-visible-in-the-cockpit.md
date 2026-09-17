---
type: "[[change]]"
id: CHG-20260916-Keep-invalid-walk-tags-visible-in-the-cockpit
title: "Keep invalid walk tags visible in the cockpit"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["Your Trainer FEAT-0122: a malformed check tag can silently disappear from the guided walk"]
commit: ""
pr: ""
impacts: ["[[SUR-0004-The-Release-Walk]]: A procedure with an unreadable check tag shows an error and the complete per-check instructions."]
issues: []
features: ["[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0629-Show-One-Walk-Action-And-Its-Readiness]]"]
---

# Keep invalid walk tags visible in the cockpit

## Summary
The cockpit walk will show a procedure error and complete per-check instructions when a check tag cannot be parsed. A malformed tag currently looks like ordinary prose and can hide an owed action when another valid tag satisfies coverage.

## Impact

- [[SUR-0004-The-Release-Walk]]: A sitting with an unreadable check tag shows the problem and the full instructions from the affected checks.

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
- [x] Sync the upstream generator into both cockpit copies and prove payload fallback retains every owed check. The payload test keeps TST-0001 in the row list, reports the malformed tag and drops the invalid script; the focused Python suite passes 36 tests.
