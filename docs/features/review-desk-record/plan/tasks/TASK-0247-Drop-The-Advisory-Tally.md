---
type: "[[task]]"
id: TASK-0247
aliases: ["TASK-0247"]
title: "Drop the advisory-phase tally from the desk — ADR-0007 is settled"
status: done
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: ["[[ADR-0007]]", "[[ISS-0064-Two-Reviewed-Sections]]"]
parent: "[[FEAT-0049-Review-Desk-As-Record]]"
effort: XS
depends: ["[[TASK-0246-Desk-Section-Order-And-Naming]]"]
blocks: []
related: ["[[FEAT-0041-Review-Desk]]", "[[TASK-0242-Reviewed-Register]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# TASK-0247 — Drop the advisory tally

## Definition of Done
- [x] The `Outcomes` block no longer renders in the desk's nav pane
- [x] `.review-tally*` CSS removed — no dead rules left behind
- [x] `ReviewStore` still records outcomes on `resolve()`, and `review_queue_payload` still exposes `outcomes`/`reviewed` — the data survives, only the surface goes
- [x] Pane order becomes **Queue → Reviewed → Tests**
- [x] [[TST-0022]]'s ordering assertion updated; the "only one section headed Reviewed" guard still holds
- [x] `test_queue_reports_the_advisory_phase_tally` keeps asserting the payload, with its docstring updated to say the tally is recorded but no longer surfaced

## Steps
- [x] Delete the tally block from `renderReviewQueuePane` and the `reviewed`/`outcomes` reads in the renderer
- [x] Delete `.review-tally`, `.review-tally-row`, `.review-tally-note` from `renderer.css`
- [x] Update the two TST-0022 ordering/naming assertions
- [x] Update the payload test's docstring — the assertion itself stays

## Notes

The block was built by [[TASK-0206]] to inform [[ADR-0007]]'s gating decision. That decision is now settled (stay advisory, permanently), so the instrument has no consumer.

Two independent reasons to remove rather than restyle, and they agree:

1. **Its purpose is discharged.** Keeping a measurement visible after the decision it fed is made turns a live instrument into decoration — and a number nobody acts on invites someone to act on it later for the wrong reason.
2. **It was the only non-interactive block in a pane of clickable rows** ([[ISS-0064]]), which is precisely how Edwin came to ask what it was for. A nav pane is a list of places to go; a counter is not one.

**Keep the recording.** `ReviewStore.resolve()` stamping outcomes is the ledger's own record of what the desk did — it costs nothing, and it is what a reopened gating question would read. What is retired is the obligation to watch it, not the data. Deleting the store's counting as well would be tidying past the point of usefulness and would take a genuinely tested behaviour with it.

## Verified

Live DOM after a restart, direct children of `.review-queue`:

```
HEADING: Queue
meta review-queue-empty
REGISTER: Reviewed · 62
REGISTER: Tests · 22/22
```

`tallyPresent: false`; the pane's headings are exactly `Queue`, `Reviewed · 62`, `Tests · 22/22`. 552 tests pass, `tsc` clean.

Guarded by `test_the_advisory_tally_is_gone_from_the_desk` (renderer **and** stylesheet — a stylesheet keeping selectors for a deleted block is how CSS rots), `test_the_desk_pane_order_is_queue_reviewed_tests`, and `test_only_one_desk_section_is_headed_reviewed` — the last kept even though the collision is now gone by subtraction, so it stays gone if a future section reaches for the same word.
