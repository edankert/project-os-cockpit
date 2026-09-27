---
type: "[[requirement]]"
id: REQ-0068
title: "The walk records one clear observation at a time"
status: superseded
superseded_by: "[[REQ-0071-A-Result-Is-Recorded-On-The-Check-Where-It-Was-Seen]]"
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-24
updated: 2026-09-27
source: ["Your Trainer REQ-0210, moved here 2026-09-24. Edwin: 'Make the changes as suggested. move them to the cockpit as suggested.'"]
priority: high
scope: "Release walk page and the existing ledger write path"
acceptance: ["One action and its exact expectations are prominent", "Preparation and navigation never create a verdict", "Success, problems and inability to perform keep the affected checks honest", "Saved marks can be corrected without duplicate events"]
reviewed_by: "model:claude-opus-5 (FEAT-0151 review, two reviewers then one)"
review_date: 2026-09-25
review_round: 2
review_verdict: approved
implements: "[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"
verifies: []
related: ["[[TASK-0629-Show-One-Walk-Action-And-Its-Readiness]]", "[[TASK-0630-Record-And-Resume-Walk-Observations]]", "[[TASK-0631-Verify-The-Guided-Walk]]"]
tests: []
---

# The walk records one clear observation at a time

## Statement

The cockpit must show one current action and its exact expected result, save one observation with an explicit mark, and leave unrelated or unavailable checks unresolved.

## Where this came from

Your Trainer wrote this requirement as REQ-0210 on 2026-09-16, under its FEAT-0122. It describes how the walk page behaves in any project-os workspace, so it moved here on 2026-09-24. Your Trainer's REQ-0210 is now `superseded` and points here.

The letters in the evidence column (A1, B5 and so on) are the detailed criteria in [[FEAT-0151-The-Release-Walk-Has-One-Next-Action]].

## Acceptance Criteria

- [x] One action and its exact expectations are prominent — evidence: B1 to B5 are met (B1, B3, B4 and B5 on 2026-09-24).
- [x] Preparation and navigation never create a verdict — evidence: B5 and D2 are met (D2 on 2026-09-25, TASK-0631).
- [x] Success, problems and inability to perform keep the affected checks honest — evidence: B6, B7 and B9 are met (2026-09-24).
- [x] Saved marks can be corrected without duplicate events — evidence: B8 and D2 are met (D2 on 2026-09-25, TASK-0631).

A criterion is ticked only when every letter it names is met.

## Traceability

- Implements: [[FEAT-0151-The-Release-Walk-Has-One-Next-Action]].
- Overlaps: [[REQ-0066-The-Release-Walk-Keeps-Observation-Context]], this feature's first requirement, which states the same goal in four lines.

## Superseded 2026-09-27

The walk page this describes was replaced by the release test in the Tests pane, which Edwin approved on 2026-09-27. [[REQ-0071-A-Result-Is-Recorded-On-The-Check-Where-It-Was-Seen]] carries it on ([[TASK-0644-Retire-The-Walk-Page-In-The-Publication-View]]).
