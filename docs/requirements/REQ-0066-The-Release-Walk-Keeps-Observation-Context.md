---
type: "[[requirement]]"
id: REQ-0066
title: "The release walk keeps the action and context for each observation"
status: implemented
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-16
updated: 2026-09-25
source: ["Your Trainer FEAT-0122, 2026-09-16"]
priority: high
scope: "Release walk page in any project-os workspace"
acceptance: ["One current action and its exact result are visible", "Only relevant preparation and setup are requested", "Recording and resume preserve evidence without creating duplicate verdicts", "Unresolved work remains visible and the page agrees with the text sheet"]
reviewed_by: "model:claude-opus-5 (FEAT-0151 review, two reviewers then one)"
review_date: 2026-09-25
review_round: 2
review_verdict: approved
implements: "[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"
verifies: []
related: ["[[SUR-0004-The-Release-Walk]]", "[[RISK-0010-Saved-Walk-Observations-Can-Outlive-Their-Source]]"]
tests: []
---

# The release walk keeps the action and context for each observation

## Statement

The release walk must show the current action, its required state and exact expected result. It must record and resume observations with their originating build and platform without treating preparation or navigation as a verdict.

## Acceptance Criteria

- [x] One current action and its exact result are visible — evidence: FEAT-0151 B5, and the browser walk of Your Trainer's current corpus recorded in TASK-0631 "Result, 2026-09-25".
- [x] Only relevant preparation and setup are requested — evidence: FEAT-0151 A1, A2 and A4 (generator), D1 (page and sheet agree), and Your Trainer TASK-0960 for A3 (done 2026-09-24).
- [x] Recording and resume preserve evidence without creating duplicate verdicts — evidence: FEAT-0151 B8, C1 and C5, and the ledger-copy tests in `tests/test_guided_walk_ledger_copy.py` (D2).
- [x] Unresolved work remains visible and the page agrees with the text sheet — evidence: FEAT-0151 B7 and B9, and D1 on both platforms in `tests/test_walk_agreement.py`.

## Traceability

- Implements: [[FEAT-0151-The-Release-Walk-Has-One-Next-Action]].
- Verified by: pending guided walk tests and browser run.
