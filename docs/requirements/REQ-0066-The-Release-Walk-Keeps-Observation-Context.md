---
type: "[[requirement]]"
id: REQ-0066
title: "The release walk keeps the action and context for each observation"
status: approved
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["Your Trainer FEAT-0122, 2026-09-16"]
priority: high
scope: "Release walk page in any project-os workspace"
acceptance: ["One current action and its exact result are visible", "Only relevant preparation and setup are requested", "Recording and resume preserve evidence without creating duplicate verdicts", "Unresolved work remains visible and the page agrees with the text sheet"]
implements: "[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"
verifies: []
related: ["[[SUR-0004-The-Release-Walk]]", "[[RISK-0010-Saved-Walk-Observations-Can-Outlive-Their-Source]]"]
tests: []
---

# The release walk keeps the action and context for each observation

## Statement

The release walk must show the current action, its required state and exact expected result. It must record and resume observations with their originating build and platform without treating preparation or navigation as a verdict.

## Acceptance Criteria

- [ ] One current action and its exact result are visible — evidence: pending browser walk.
- [ ] Only relevant preparation and setup are requested — evidence: pending generator and page comparison.
- [ ] Recording and resume preserve evidence without creating duplicate verdicts — evidence: pending restart and ledger-copy tests.
- [ ] Unresolved work remains visible and the page agrees with the text sheet — evidence: pending Android and iOS comparison.

## Traceability

- Implements: [[FEAT-0151-The-Release-Walk-Has-One-Next-Action]].
- Verified by: pending guided walk tests and browser run.
