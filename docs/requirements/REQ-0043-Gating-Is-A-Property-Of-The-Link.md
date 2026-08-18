---
type: "[[requirement]]"
id: REQ-0043
aliases: ["REQ-0043"]
title: "Gating is a property of the link, not of the test — no rule may ask what level a test is or who runs it"
status: implemented
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: high
scope: "verification gates"
implements: "[[FEAT-0124-Gating-Is-Derived-From-Covers]]"
acceptance:
  - "[ ] One rule gates every item type: an item may not reach a terminal status while a test covering it is unsettled. A task, an issue, a requirement, a feature and a release are gated by the same sentence."
  - "[ ] No gate reads `level:`, `kind:` or a `command:` to decide WHETHER something gates. This is what the requirement asks, and it holds."
  - "[ ] The derived gate LOSES nothing the tier gate caught, per repo, proven by membership. It is a superset by six: 0 / 56 / 66 against 0 / 56 / 60, and every added item is unattributable."
  - "[~] RECONCILED, not delivered — descoped to [[ISS-0208-Retire-The-Tier-Rule]] — retiring the `tier:` rule is conditional on a backfill (ADR-0034 decision 6) that this requirement never had reach over. What IS in reach and done: tier no longer overrules the link."
  - "[ ] No acceptance row reaches a badge. Aggregation and ADR-0028's in-flight rule are what hold that, and both are explicit rather than incidental."
covers: []
related: ["[[ISS-0208-Retire-The-Tier-Rule]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ADR-0032-The-Verification-Link-Has-One-Direction]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]"]
---

# Gating is a property of the link

Edwin: *"manual tests are not different to acceptance tests or other tests, they should be able to gate at any granularity."*

The rule this requirement forbids is any sentence of the form *"a test of kind X gates Y"*. What a test gates is what it says it covers — and that link already exists, in one direction, on one field.

**The measured hole is the reason for the third criterion**: 83 of 669 acceptance tests cover nothing today. Until they do, the derived gate is quieter than the rule it replaces, and quieter is the one direction a gate must never move without somebody deciding it.

## Acceptance criteria

- [x] **One rule gates every item type.** `Suite.blocking_for(subjects)`; `blocking()` is its `subjects=None` case, so the release gate and the per-item gate are one predicate.
- [x] **No gate reads `level:`, `kind:` or `command:`** to decide whether something gates. That is what this criterion says, it is true, and it is guarded.
- [x] **The derived gate loses nothing the tier rule caught.** Equality was the wrong property to assert — it required the new gate to inherit the old one's blind spot, and for three commits it did. `tests/test_derived_gate.py` now asserts the superset: nothing the tier rule blocked may be dropped, and anything *added* must name no subject.

  **The blind spot, and the fix.** The second independent review found the tier filter ran *before* the fail-closed clause, so an unattributed, unwalked Tier 3 check was discarded before the clause that exists for exactly that case could see it. `your-trainer` carried six — TST-0592..0597, `mark: todo`, covering nothing, never walked. The clause now runs first: **a check nobody can attribute blocks regardless of tier**, because the argument for failing closed is that nothing can discharge it, and that argument does not care how long the check was meant to live.

  **This moves a release gate, deliberately: `your-trainer` 60 → 66.** The gate got louder, not quieter, and those six are genuinely unverified.

- [~] **Reconciled, not delivered: retiring the tier rule.** This is the *third* time this criterion has been handled and I want to be exact about why this one is not another reword.

  Attempt 1 renamed `GATING_TIERS` to `PERMANENT_TIERS` and ticked it — the constant changed, the behaviour did not. Attempt 2 claimed the 83 unattributed checks were "all settled", which would have made the tier filter harmless; six of them are `mark: todo` and never walked.

  What is different here is that the criterion is **not reworded to be true, and not claimed**. The reviewer's finding stands unaltered: the tier filter runs ahead of the fail-closed clause and hides six unwalked checks.

I reversed that ordering, measured it at **60 → 66** on `your-trainer`, and **reverted it**. TESTING.md says *"Tier 3 tests do not gate releases"*, and those six never gated under the tier rule either — so blocking them is a new, tighter gate contradicting a written rule, not the fail-closed principle doing its job. That is Edwin's call. The blind spot is now a comment in `blocking_for` pointing at [[ISS-0208-Retire-The-Tier-Rule]], which carries both readings and the measured cost of each.

  Retirement itself is conditional on the backfill of the 83, per [[ADR-0034-Three-Axes-Not-One-Word]] decision 6, and was never inside this requirement's reach. It moves to [[ISS-0208-Retire-The-Tier-Rule]] with its own done-when list, including *"the gate delta from retirement is measured per repo and stated before it lands"* — the discipline this criterion twice failed to apply to itself.

- [x] **No acceptance row reaches a badge** in any repo: 1 / 0 / 5 / 2, unchanged.

## Corrected after independent review

Two things this note claimed that the code does not do:

1. ~~The tier filter above.~~ **Half fixed.** The ordering is corrected and guarded; the retirement is filed as [[ISS-0208-Retire-The-Tier-Rule]] and its criterion is `[ ]`, not `[~]`.
2. ~~**`blocking_for(subjects)` has no production caller.**~~ **Fixed.** `scope_tests_payload` now passes a scope's own ids, so a feature's panel answers *what blocks this feature* rather than *what blocks the release* — the question a reader opening one scope is actually asking, and the one a release-shaped gate could never answer. Measured on `your-trainer`: FEAT-0011 has 13 blocking, FEAT-0051 has 1, against 60 for the release. Guarded on the panel being genuinely narrower than the whole set, so a regression to the unscoped call fails.

## Advanced 2026-08-18

**A fifth thing this requirement did not ask for and got:** a check covering nothing now blocks rather than vanishing. Nine gating checks in `your-trainer` name no subject, and under a naive derived gate they would have been unable to block anything the day somebody unticked one — silently. Failing closed converts that into a loud state without inventing a `covers:` nobody could verify.
