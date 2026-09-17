---
type: "[[task]]"
id: TASK-0630
title: "Record and resume walk observations with evidence"
status: doing
phase: ""
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["Your Trainer FEAT-0122, 2026-09-16"]
parent: "[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"
effort: "Large"
depends: ["[[TASK-0629-Show-One-Walk-Action-And-Its-Readiness]]"]
blocks: ["[[TASK-0631-Verify-The-Guided-Walk]]"]
related: ["[[RISK-0010-Saved-Walk-Observations-Can-Outlive-Their-Source]]"]
tests: []
---

# Record and resume walk observations with evidence

## Definition of Done

- [x] Pass and next saves an observation before moving. Fail, Partial, Question and inability to perform keep their separate existing meanings. The focused renderer tests cover the separate observation and decision controls.
- [x] Saved progress is scoped to workspace, release, platform and content, and survives a restart without borrowing changed or foreign observations. The completed-check correction index is scoped the same way.
- [x] An earlier note or attachment is available beside its later comparison with its originating build, state and platform. A timer helps with an authored wait and does not create a verdict. Focused renderer tests cover the restart, comparison and timer behavior; a real browser walk remains under TASK-0631.
- [x] Storage and ledger write failures are visible, retryable and cannot accidentally duplicate a verdict. An explicit new run can append an identical result.

## Steps

- [x] Define storage records, invalidation and correction behavior against the existing ledger rules. A completed-check index selects current authored steps for review; it never defines the owed set or a ledger verdict.
- [x] Build the controls and attach evidence to the originating action. The optional PNG is filed under the affected check; the browser stores its path with the source observation.
- [x] Exercise interruption, changed content and failed writes in focused tests.
