---
type: "[[phase]]"
id: PHASE-011
aliases: ["PHASE-011"]
title: "Unproven claims become visible"
status: done
order: 11
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
goal: "Stop the cockpit presenting a claim and its evidence as the same thing. A waiver, a two-month-old manual verification, a hand-written register of what a test asserts and a status band that drifted out of its guard all read today exactly like earned completion — and every one of them is a claim nothing checked."
features:
  - "[[FEAT-0018-Verification-Health-Surface]]"
requirements: []
issues:
  - "[[ISS-0024-Status-Surfaces-Outside-The-Parity-Guard]]"
  - "[[ISS-0057-Staleness-Follows-The-Artifact-Only]]"
  - "[[ISS-0066-Test-Coverage-Registers-Drift-By-Hand]]"
depends: []
related: ["[[DES-0004-Attention-In-The-Squares]]", "[[DES-0003-Intent-Page-And-Claims-Board]]", "[[ADR-0010]]", "[[ADR-0011]]", "[[PHASE-012-Attention-In-The-Strip]]"]
tags: [verification, quality]
reviewed_by: "model:claude-opus-5"
review_date: 2026-07-30
review_verdict: "changes-requested"
---

# Unproven claims become visible

## Goal

This repo has decided twice already that a status must not assert what nothing performed — [[ADR-0010]] took `passing`/`failing` away from authors and gave it to the runner; [[ADR-0011]] put a deadline on unreviewed terminal notes. The surfaces did not follow. Measured on 2026-07-30:

- **22 items are terminal under a recorded `verification_waiver`** and render on the phase strip as clean solid squares, identical to items verified by proof.
- **21 of 22 tests are manual and all read `passing`.** Nothing in the UI distinguished a current verification from an old one. *(An earlier version of this line claimed 9 were stale; that used a 30-day threshold, not the project's 90. See the correction below — at 90 none are, and the waived items carry this phase on their own.)*
- **[[TST-0022]]'s `## Coverage` register needed four independent-review rounds to describe its own 27 assertions accurately**, and requirement criteria are ticked *against that register*.
- **[[ISS-0024]]** is the same failure one level down: `DONE_BY_TYPE` drifted outside TST-0019's parity guard, so a per-type done-set could claim a status the vocabulary had moved.

### Correction, 2026-07-30 — the stale-test figure was wrong

This note claimed *"9 were last verified 66–83 days ago"* as part of `unproven`'s motivating population. That used a **30-day threshold I chose**, not the project's.

The project's threshold is `DEFAULT_STALENESS_DAYS = 90` in `tools/scripts/validate-docs.py`, configurable via `SNAPSHOT.yaml` `verification.staleness_days` (unset here, so 90 applies). At 90 days **no test in this corpus is stale**, and the validator emits zero `TEST-STALE` warnings — which is the check that would have told me, and which I did not consult before writing the figure.

So `unproven`'s population today is **the 22 waived items alone**. The mark is still worth having, and for the stronger of the two reasons: a waiver is a standing claim that verification was skipped, whereas staleness is a clock that has not yet run out. But the design must not cite 9 stale tests as evidence, and the implementation must use the project's threshold and config source rather than a second one — inventing a parallel staleness rule is precisely what [[ISS-0024]] and [[ISS-0069]] are about.

The phase's claim is one sentence: **where the system already knows a claim is unproven, it must say so.** Every item here has the data already — waivers are frontmatter, staleness is arithmetic on `last_verified`, register drift is a set comparison. None of it needs new judgement, only surfacing.

## Scope

- Close out or finish [[FEAT-0018]]. Its three tasks are `done` and [[TST-0016]] is `passing`, yet it sits at `review` — it is the "6-week in-review stall" [[DES-0001]]'s plate 5 named, and it is the natural owner of validator/waiver/drift badges.
- The **static inverted fill** from [[DES-0004]] — *complete but unproven* on the phase strip. One mark from that design belongs here; the rest belongs to [[PHASE-012]].
- [[ISS-0066]] — derive or check the Coverage register instead of hand-maintaining it. The reviewer's own enumeration of the drift was also incomplete, which is the argument that neither copy should be by hand.
- [[ISS-0024]] — extend the parity guard to the surfaces it missed. Also unblocks [[PHASE-007]]'s PHASE-CHILDREN error, which this issue is the sole cause of.
- [[ISS-0057]] — design review staleness follows the artifact revision only, so a note's prose can change after an accepting verdict without invalidating it.

## Out of Scope

- **[[DES-0003]]'s claims board.** It is the right end state for this theme and it is blocked upstream: typed evidence needs project-os-dev ADR-0014. Left unphased deliberately rather than pulled in and stalled.
- **The rest of [[DES-0004]]** — the dot, the strike, the pulse. [[PHASE-012]].
- **Backfilling verification** on the 22 waived items or re-running the 9 stale tests. This phase makes the state legible; deciding what to do about each one is the work it enables, not the work it contains.
- **Changing waiver policy.** `ADR-0011`'s deadline stands; nothing here renegotiates it.

## Exit Criteria

- [x] A waived or stale-verified item is visually distinguishable from a proven one on the phase strip — evidence: the static inverted fill from [[DES-0004]], implemented in `_square_state`/`_is_unproven` and `.ov-phase-sq[data-state="unproven"]`. **22 items** carry it (every `verification_waiver` in the corpus), verified in the running app at 9px: `background: currentColor` with `inset 0 0 0 1.5px var(--bg)`, distinct from both solid and hollow. **Count is 22, not 22 + 9** — see the correction above; no test is stale at the project's 90-day threshold, and `test_the_staleness_threshold_is_the_validators` holds the cockpit to the validator's number so a second rule cannot reappear.
- [x] Coverage-register drift fails a check rather than waiting for a reviewer — evidence: `tests/test_coverage_registers.py::test_every_test_named_in_a_note_exists`, parametrised per note. **It found four dangling citations on its first run** (TST-0019 and TST-0002, all renames the notes never followed). Mutation-verified both ways: a typo in a citation fails, and renaming a test in source while leaving the note alone fails. The reverse direction is deliberately not enforced and `test_enumeration_is_not_the_convention` records the measurement why.
- [x] `PHASE-007` has no PHASE-CHILDREN error — evidence: [[ISS-0024]] is `fixed`; `phase_close_blockers(index, "PHASE-007")` returns `[]`; validator clean.
- [x] An accepting design verdict is invalidated by a change to the note's prose, not only to its artifact — evidence: `cockpit.design_note_digest`, `at_note_digest` on the request, and `note_digest`/`note_moved` on the review detail. Guarded by `test_a_design_note_digest_ignores_what_recording_a_review_touches`, asserted in both directions. **Reconciled with [[ISS-0071]]:** `status` had to join the exclusions, because `stamp_design_verdict` writes it and an accepting verdict was invalidating its own digest. — [~] **The desk does not yet render `note_moved`.** The signal exists and nothing displays it, which is the shape of [[ISS-0065]]. Recorded in [[ISS-0057]] rather than closed over; the criterion is met at the payload and unmet at the surface.
- [x] FEAT-0018 is terminal, with its review verdict recorded rather than assumed — evidence: `done`, and the mode-1 visual pass it was held for is written up in the note with measured values (badge `ok`→`failing` over SSE with `navigation.length` pinned at 1, drift rows deep-linking, amber waiver and green verdict chips). Independent review **approved** that half specifically. [[CHG-20260730]] carries the record.

**Also delivered, and not foreseen when this phase was written:** [[ISS-0069]] (a second, unguarded `review_verdict` vocabulary — 10 notes carried `CLOSE`), [[ISS-0070]] (an unanchored `.gitignore` pattern had kept a whole feature out of the repository), and [[ISS-0071]] (the review's own findings, including three guards that passed while what they claimed was broken).

## Notes

Sequenced first of the three new phases because it is the only one whose absence actively misleads. [[PHASE-012]] makes the overview quieter and [[PHASE-013]] makes the fleet legible; this one stops a surface asserting something untrue.

One honest caveat about the exit criteria: four of the five are mechanical, and the fifth (FEAT-0018 terminal) requires a judgement about whether the feature was ever finished or should be cancelled. That decision is Edwin's and is not prejudged here — a `review` status six weeks old is as likely to mean "abandoned" as "nearly done".

## Independent review — 2026-07-30 (model:claude-opus-5, fresh context, separate session) — changes-requested

The phase is well-shaped and the self-correction on the staleness threshold is the right instinct. **The correction is incomplete in this note and in the design it corrects**, which matters because a retracted measurement left in place reads as current to the next reader — the exact failure this phase exists to stop.

Still asserting the retracted figure:

- **Line 31** states "9 were last verified 66–83 days ago" as a measurement, with the retraction six lines below and no marker on the claim itself.
- **Line 57** (Out of Scope) — "re-running the 9 stale tests".
- **Line 62** (Exit Criteria) — "evidence: `<the unproven mark implemented, plus a count against the 22 + 9 measured here>`". This criterion now cannot be satisfied honestly: the count is 22, and the note itself says there is no 9.
- `DES-0004`'s `## Regions` line 101 — "the 9 stale tests that motivate *unproven*".
- **`DES-0004-attention-in-the-squares.html`**, the accepted artifact, twice: "**9 were last verified 66–83 days ago**. Today they would all be solid squares" and "13 proven, 9 stale, and a `ready` test that has never run carries the dot". The artifact was never touched, and DES-0004's own Tokens section says "if these diverge, the artifact is the specification".

The implementation half of the correction *is* complete and correct: `cockpit.DEFAULT_STALENESS_DAYS = 90` matches the validator, `_is_stale_verification` mirrors `is_stale`'s semantics (`> days`, absent/unparseable dates not stale, `command:` excluded at the caller), and `test_the_staleness_threshold_is_the_validators` reads the validator's literal rather than restating it. One latent divergence: `_staleness_days` hand-rolls `^verification:\s*$` plus an indented `staleness_days:` scan, so a snapshot writing `verification: {staleness_days: 30}` inline, or `verification:  # comment`, silently yields 90 while the validator's parser yields 30 — a parallel rule of the kind this phase's goal names, reachable by ordinary YAML.

Exit criteria 1–5 all appear satisfied by `74a2187..HEAD` yet none is ticked and the phase still reads `status: planned`, so from the notes alone this phase reads as unstarted while its work has shipped.
