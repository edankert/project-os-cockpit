---
type: "[[task]]"
id: TASK-0465
aliases: ["TASK-0465"]
title: "One walk layer — the component that walks checks is the component that walks manual-test steps"
status: done
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

## Outcome, 2026-08-17 — the verdict layer converged; the step wizard did not

`walkOneCheck` is the one layer: ask, write, catch the refusal, repaint without moving the reader. The release gate's rows and the acceptance view's rows both go through it and neither posts for itself — asserted as *no second `postJson` in either caller*, because the two copies had already drifted twice ([[ISS-0187]]'s unhandled rejection existed in one and not the other, and [[ISS-0188]]'s scroll fix had to be applied twice, one frame too early the first time).

**The manual-test runner deliberately did not converge, and this is the measurement rather than a shrug.** It looked like the same shape — a walkable list of steps — and is not: its per-step results are TRANSIENT and recorded in one batch at the end, where a check's verdict is persistent and written per row; it advances one step at a time where the check view is a filtered list. Three axes of difference against one of similarity is a parameterised component nobody can read.

So the shared thing is the verdict layer rather than the page, and that is recorded **in the component** — the next surface that walks something plugs into `walkOneCheck` and finds the reasoning beside it, which is what this task asked for.
