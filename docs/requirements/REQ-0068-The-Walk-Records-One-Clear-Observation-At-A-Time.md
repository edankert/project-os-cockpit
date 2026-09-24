---
type: "[[requirement]]"
id: REQ-0068
title: "The walk records one clear observation at a time"
status: approved
phase: ""
owner: user:edwin
created: 2026-09-24
updated: 2026-09-24
source: ["Your Trainer REQ-0210, moved here 2026-09-24. Edwin: 'Make the changes as suggested. move them to the cockpit as suggested.'"]
priority: high
scope: "Release walk page and the existing ledger write path"
acceptance: ["One action and its exact expectations are prominent", "Preparation and navigation never create a verdict", "Success, problems and inability to perform keep the affected checks honest", "Saved marks can be corrected without duplicate events"]
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

- [ ] One action and its exact expectations are prominent — evidence: B1 to B5 are open. B2 is met.
- [ ] Preparation and navigation never create a verdict — evidence: B5 and D2 are open.
- [ ] Success, problems and inability to perform keep the affected checks honest — evidence: B6, B7 and B9 are open.
- [ ] Saved marks can be corrected without duplicate events — evidence: B8 is met; D2 is open.

A criterion is ticked only when every letter it names is met.

## Traceability

- Implements: [[FEAT-0151-The-Release-Walk-Has-One-Next-Action]].
- Overlaps: [[REQ-0066-The-Release-Walk-Keeps-Observation-Context]], this feature's first requirement, which states the same goal in four lines.
