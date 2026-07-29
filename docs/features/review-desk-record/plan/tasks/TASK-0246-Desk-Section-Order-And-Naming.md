---
type: "[[task]]"
id: TASK-0246
aliases: ["TASK-0246"]
title: "Name the desk's two review sections for what they measure, and order the pane Queue → Reviewed → Tests"
status: done
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: ["[[ISS-0064-Two-Reviewed-Sections]]"]
parent: "[[FEAT-0049-Review-Desk-As-Record]]"
effort: XS
depends: []
blocks: []
related: ["[[TASK-0242-Reviewed-Register]]", "[[ADR-0007]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# TASK-0246 — Desk section order and naming

## Definition of Done
- [x] Only one section on the desk is headed `Reviewed` — live DOM reports `reviewedHeadingCount: 1`
- [x] The ADR-0007 tally is headed for what it measures — now `Outcomes · 1`
- [x] Pane order is **Queue → outcomes tally → Reviewed → Tests** — live DOM: `HEADING: Queue`, `TALLY: Outcomes · 1`, `REGISTER: Reviewed · 62`, `REGISTER: Tests · 22/22`
- [x] The tally's own semantics are untouched: same source (`store.outcome_counts()`), same rows, same "N of M sets changed on review" line — only the heading string changed
- [x] [[TST-0022]] gained `test_the_desk_pane_order_is_queue_outcomes_reviewed_tests` and `test_only_one_desk_section_is_headed_reviewed`

## Steps
- [x] In `renderReviewQueuePane`, rename the tally heading from `Reviewed · N` to `Outcomes · N`
- [x] Swap the two `appendIf` calls so the reviewed register precedes the tests register
- [x] Add a test asserting the section order, and one asserting the heading collision cannot return

## Notes

The tally keeps its place directly under the queue: it is *about* the queue (what happened to the things that passed through it), and ADR-0007 put it there so the gate-or-not decision is visible to whoever works the queue. Only its label changes.

`Outcomes` over alternatives like `Desk activity` or `Review outcomes`: the rows beneath it are already outcome names (`accepted as proposed`, `changes requested`, `rejected`), so the heading just names the list rather than re-describing it.

Why the ordering needs a test rather than a comment: both registers are appended at the end of the same function, so the order is positional and a future addition appending in the obvious place would change it without failing anything. That is precisely how [[ISS-0064]] happened.
