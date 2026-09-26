---
type: "[[task]]"
id: TASK-0359
aliases: ["TASK-0359"]
title: "The left pane becomes the queue only once something is selected, and the walk gets `1 of N` and Next"
status: superseded
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-10
source: ["[[DES-0010-The-Desk-Shows-What-It-Owes]]"]
parent: "[[FEAT-0082-The-Desk-Shows-What-It-Owes]]"
effort: M
due: ""
depends: ["[[TASK-0358-The-Board-Is-The-Desks-Landing]]"]
blocks: []
related: ["[[TST-0022-Surface-Ownership]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# The pane is the walk

## Definition of Done
- [ ] Nothing selected → the left pane shows the registers (Tests, Reviewed) and no queue
- [ ] Something selected → the left pane shows the queue, current row marked, registers folded to one line
- [ ] The board and the queue list are never both on screen
- [ ] The detail view carries `1 of N` and a `Next ▸` that advances within the current obligation kind
- [ ] [[TST-0022]] step 10 is rewritten to describe the mode-dependent pane, and its manual run passes

## Steps
- [ ] Branch `renderReviewQueuePane` on whether a target is selected
- [ ] Keep the registers' relative order in the selected-nothing state; the ordering rationale in the existing comment survives, only its trigger changes
- [ ] `Next ▸` walks the payload order already used by the queue rows — no second ordering
- [ ] Update TST-0022's step 10, its manual steps, and its `## Runs` log with a new run

## Notes
**This is the test-gated part of the feature.** TST-0022 step 10 asserts the pane order is Queue → Reviewed → Tests, source-level *and* manually, because both registers are appended at the tail of one function and the order is positional — that is exactly how [[ISS-0064]] happened. A mutation swapping the two appends was caught. The test is doing its job; it needs updating, not bypassing.

The mode split is what stops the board and the list being visibly redundant at n=3 while still giving n=39 both a map and a walk. It came out of drawing the plates: the first formulation kept the queue in the pane at all times, and plate B made the duplication obvious.


## Superseded 2026-08-10 — [[ADR-0020]]

The walk it specifies belonged to a queue that no longer exists. [[TST-0022]] still needs its desk steps rewritten; that is now [[TASK-0378]].
