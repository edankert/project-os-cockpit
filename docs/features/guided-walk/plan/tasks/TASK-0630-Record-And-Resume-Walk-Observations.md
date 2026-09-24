---
type: "[[task]]"
id: TASK-0630
title: "Record and resume walk observations with evidence"
status: done
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-16
updated: 2026-09-24
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

## Against the detailed criteria, 2026-09-24

FEAT-0151 now carries the detailed criteria. This task owns the six recording and resume criteria below; TASK-0629 owns presentation. The Definition of Done above was ticked on 2026-09-17 against the shorter list, and the audit on 2026-09-24 found these gaps against the detailed one. A criterion is ticked in FEAT-0151 only when a focused test proves it.

- **B6 (exceptions with context):** **Something wrong…** records its mark and then moves to the next step, so the problem just recorded disappears. It will stay on the step. **I can't perform this** does not carry the step's own readiness reason into the decision dialog. After a decision, the card does not show the decision it recorded.
- **B9 (honest completion):** the results summary is built from the payload loaded when the page opened. A check passed during this walk is still listed as "no current verdict". Checks still waiting on some of their steps are not named.
- **C1 (restart):** met in code; needs a test that leaves in the middle of a check cited by two steps, restarts, and finds no verdict written.
- **C2 (restore app state):** a resumed walk shows the step's required state but does not say the walk was resumed, how to restore the state, or that the cockpit has not checked the app.
- **C3 (changed work):** a changed step's old mark is archived, and the page names the affected checks in a banner. The card itself says nothing. Evidence saved before a candidate invalidation is still reused at the later comparison, because evidence has no invalidation basis.
- **C7 (stable navigation):** when the saved step no longer exists, the page silently jumps to the first unmarked step. It will move to the nearest valid step and say why.

**Done, 2026-09-24.** All six criteria above are met and ticked in FEAT-0151, each with its own test in `desktop/tests/walk-page.test.mjs`. [[CHG-20260924-The-Walk-Keeps-Problems-In-View-And-Says-Where-You-Resume]] records the change. The combination rule, the ledger format and the write path are unchanged.
