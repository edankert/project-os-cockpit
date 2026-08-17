---
type: "[[task]]"
id: TASK-0465
aliases: ["TASK-0465"]
title: "One walk layer — the component that walks checks is the component that walks manual-test steps"
status: backlog
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["[[FEAT-0114-The-Suite-Is-A-View]]"]
parent: "[[FEAT-0114-The-Suite-Is-A-View]]"
effort: M
depends: ["[[TASK-0464-The-Generated-List-View]]"]
blocks: []
related: []
tests: []
---

# One walk layer

Edwin: *"we don't need to show the acceptance tests the way they are stored on disk probably the same for normal tests."* The manual-test runner already presents a TST note as a walkable list of steps with per-step state; a check is one step of that with a persistent verdict. This task converges them into one component parameterised by what it walks — the acceptance side ships in this phase, the TST side keeps working unchanged, and the next surface that needs a walk inherits it instead of inventing a third.

## Done when

- [ ] One walk component serves the check view; the manual-test runner behaves identically before and after.
- [ ] The convergence is recorded in the component, so the next author finds one place, not two.
