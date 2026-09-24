---
type: "[[requirement]]"
id: REQ-0069
title: "The walk resumes with valid evidence and the required state"
status: approved
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-24
updated: 2026-09-24
source: ["Your Trainer REQ-0211, moved here 2026-09-24. Edwin: 'Make the changes as suggested. move them to the cockpit as suggested.'"]
priority: high
scope: "Release walk page: local progress, evidence and resume"
acceptance: ["Position, observations and evidence survive restart in their workspace", "Changed source content and platform cannot silently reuse old marks", "Persistence or ledger failures are visible and retryable", "Required live app state is named but never assumed confirmed", "Evidence and timers stay separate from verdicts"]
implements: "[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"
verifies: []
related: ["[[TASK-0630-Record-And-Resume-Walk-Observations]]", "[[TASK-0631-Verify-The-Guided-Walk]]", "[[RISK-0010-Saved-Walk-Observations-Can-Outlive-Their-Source]]"]
tests: []
---

# The walk resumes with valid evidence and the required state

## Statement

The cockpit must restore valid progress after interruption, identify the state the rider still needs, and prevent old or unsaved evidence from appearing as a completed check.

## Where this came from

Your Trainer wrote this requirement as REQ-0211 on 2026-09-16, under its FEAT-0122. It describes how the walk page behaves in any project-os workspace, so it moved here on 2026-09-24. Your Trainer's REQ-0211 is now `superseded` and points here.

The letters in the evidence column (A1, B5 and so on) are the detailed criteria in [[FEAT-0151-The-Release-Walk-Has-One-Next-Action]].

## Acceptance Criteria

- [x] Position, observations and evidence survive restart in their workspace — evidence: C1 and C7 are met (2026-09-24).
- [x] Changed source content and platform cannot silently reuse old marks — evidence: C3 is met (2026-09-24).
- [x] Persistence or ledger failures are visible and retryable — evidence: C4 is met.
- [x] Required live app state is named but never assumed confirmed — evidence: C2 is met (2026-09-24).
- [x] Evidence and timers stay separate from verdicts — evidence: C5 and C6 are met.

A criterion is ticked only when every letter it names is met.

## Traceability

- Implements: [[FEAT-0151-The-Release-Walk-Has-One-Next-Action]].
- Overlaps: [[REQ-0066-The-Release-Walk-Keeps-Observation-Context]], this feature's first requirement, which states the same goal in four lines.
