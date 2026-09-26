---
type: "[[issue]]"
id: ISS-0064
aliases: ["ISS-0064"]
title: "The review desk shows two sections headed 'Reviewed' with different counts, and the registers sit in the wrong order"
status: fixed
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
severity: medium
component: review-desk
parent: "[[FEAT-0049-Review-Desk-As-Record]]"
related: ["[[CHG-20260729-Surface-Ownership]]", "[[TASK-0242-Reviewed-Register]]", "[[ADR-0007]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
reviewed_by: "model:claude-opus-5"
review_date: "2026-07-30"
review_verdict: "approved"
---

# ISS-0064 — Two "Reviewed" sections

## Problem

Reported by Edwin on 2026-07-29, immediately after [[PHASE-010]] landed: the desk's left pane shows **two sections headed `Reviewed`**, one just under the queue and one under the Tests register.

They are different things measuring different populations, and the shared word makes them read as a duplicate — or worse, as the same number rendered inconsistently:

| Section | Source | Count here |
|---|---|---|
| Just below the queue | `store.outcome_counts()` — outcomes of review interactions that passed through the desk (the ADR-0007 advisory-phase measurement) | **1** |
| Below the Tests register | Notes carrying a non-empty `review_verdict` ([[TASK-0242]]) | **62** |

`Reviewed · 1` sitting a few rows above `Reviewed · 62` is not a labelling nitpick. The first is "how many things you reviewed *at this desk*", the second is "how many things in the corpus carry a verdict". Both are worth having; neither is named for what it is.

Introduced by [[TASK-0242]], which took the word `Reviewed` for the new register without noticing the existing tally already used it (`renderer.ts:3919`).

## Repro

Open `~review`. Look at the left pane.

## Expected

Two sections whose headings say which question each answers, and an order that puts the durable record before the reference material.

Edwin's requested order: **Queue → Reviewed → Tests.** The reasoning holds up — the tests register is the least time-sensitive thing on the desk (a browsable list of what gets verified), so it belongs last, under both the queue and the review record.

## Actual

Order is Queue → tally (`Reviewed · 1`) → Tests → `Reviewed · 62`, so the two same-named sections are also split apart by an unrelated one.

## Evidence

```
$ curl -s localhost:8765/api/cockpit/review-queue
tally    reviewed = 1   outcomes = {'accepted': 1}
register reviewed = 62
register tests    = 22
```

## Next Actions

- [x] Rename the ADR-0007 tally so it says what it measures, keeping `Reviewed` for the register that lists reviewed items — [[TASK-0246]]; the tally is now `Outcomes · 1`
- [x] Reorder to Queue → Reviewed → Tests — [[TASK-0246]]

## Fix verified

Live DOM after a restart, direct children of `.review-queue` in document order:

```
HEADING: Queue
meta review-queue-empty
TALLY:    Outcomes · 1
REGISTER: Reviewed · 62
REGISTER: Tests · 22/22
```

`reviewedHeadingCount: 1`. Guarded by `test_only_one_desk_section_is_headed_reviewed` and `test_the_desk_pane_order_is_queue_outcomes_reviewed_tests` — the second exists because both registers are appended at the tail of the same function, so the order is positional and the next append in the obvious place would reshuffle it silently.

## Notes

Worth recording why [[TST-0022]]'s manual pass did not catch this. Step 5 asserted both registers were *present and populated* — `Tests · 22/22` and `Reviewed · 62` — which is exactly what it was written to check, and it passed correctly. It said nothing about their order relative to each other or to the pre-existing tally, because the step was written to test reachability and this is a legibility defect.

That is the honest limit of a checklist derived from a reachability requirement: [[REQ-0025]] asks whether a type can be found, and the answer here is still yes. A human looking at the pane spotted it in seconds.
## Independent review — 2026-07-30, approved

Fresh session, `model:claude-opus-5`, from the notes and the diff for `bed48ea`.

The account is accurate and the resolution is better than the fix originally requested. Verified: the collision is gone, `test_only_one_desk_section_is_headed_reviewed` holds, and `test_the_desk_pane_order_is_queue_reviewed_tests` fails when the two register appends are swapped — so the positional fragility that produced this issue is now pinned rather than merely noted. The two counts do measure different populations as described (1 desk interaction, 62 notes carrying a verdict).

**One correction inherited by the notes downstream of this issue.** The 1 is not disjoint from the 62: the desk interaction is [[DES-0002]], whose note carries `review_verdict: "accepted"` and is therefore inside the register's 62. The "1 of 63" arithmetic in [[ADR-0007]] and [[CHG-20260729-Advisory-Review-Settled]] should be 1 of 62. It strengthens the conclusion; it is still worth fixing.

The heading assertion is a source-level regex (`textContent = \`(\w+) · \${`) and would not catch a heading written another way. [[TST-0022]] labels it source-level, so this is a known limit rather than a finding.
