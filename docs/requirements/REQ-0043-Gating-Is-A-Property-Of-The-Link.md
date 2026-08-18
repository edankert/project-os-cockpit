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
  - "[x] One rule gates every item type: an item may not reach a terminal status while a test covering it is unsettled. A task, an issue, a requirement, a feature and a release are gated by the same sentence."
  - "[x] No gate reads `level:`, `kind:` or a `command:` to decide WHETHER something gates. This is what the requirement asks, and it holds."
  - "[x] The derived gate names the same blocking SET as the tier gate, per repo, proven by membership rather than count: 0 / 56 / 60, identical sets."
  - "[~] RECONCILED, not delivered — retiring the `tier:` rule is conditional on a backfill (ADR-0034 decision 6) this requirement never had reach over, and carried by [[ISS-0208-Retire-The-Tier-Rule]]. The known blind spot (six unwalked Tier 3 checks the tier filter hides from the fail-closed clause) is documented in `blocking_for` and unfixed."
  - "[x] No acceptance row reaches a badge. Aggregation and ADR-0028's in-flight rule are what hold that, and both are explicit rather than incidental."
covers: []
reviewed_by: model:claude-opus-5
review_date: 2026-08-18
review_verdict: changes-requested
related: ["[[ISS-0208-Retire-The-Tier-Rule]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ADR-0032-The-Verification-Link-Has-One-Direction]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]"]
---

# Gating is a property of the link

Edwin: *"manual tests are not different to acceptance tests or other tests, they should be able to gate at any granularity."*

The rule this requirement forbids is any sentence of the form *"a test of kind X gates Y"*. What a test gates is what it says it covers — and that link already exists, in one direction, on one field.

**The measured hole is the reason for the third criterion**: 83 of 669 acceptance tests cover nothing today. Until they do, the derived gate is quieter than the rule it replaces, and quieter is the one direction a gate must never move without somebody deciding it.

## Acceptance criteria

- [x] **One rule gates every item type.** `Suite.blocking_for(subjects)`; `blocking()` is its `subjects=None` case, so the release gate and the per-item gate are one predicate.
- [x] **No gate reads `level:`, `kind:` or `command:`** to decide whether something gates. That is what this criterion says, it is true, and it is guarded.
- [x] **The derived gate names the same blocking set as the tier rule**, per repo, proven by membership rather than count: **0 / 56 / 60**, identical sets — `test_the_derived_gate_names_the_same_items_as_the_tier_rule`, parametrised over all three suites.

  **Corrected 2026-08-18 by the third independent review.** This criterion previously read *"loses nothing … a superset by six … 60 → 66 … the gate got louder"*, describing a change that the very same commit had **reverted**. Criterion 4, four lines below, said it was reverted. The reviewer measured `blocking()` at 60, found `git log -S"superset"` empty — that guard never existed — and applied the described change as a mutation to show the committed suite *forbids* it.

  That is the third time this requirement has read satisfied on a basis absent from the code, and the mechanism was new: I did not reword the tier criterion again, I moved the claim one criterion up while reverting the code under it. The blind spot it described is real and stays open on [[ISS-0208-Retire-The-Tier-Rule]].

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

## Independent review — 2026-08-18, `model:claude-opus-5`, changes-requested

Third verification pass, fresh context, separate session; the model is shared with the author and recorded above as provenance ([[project-os-dev#ADR-0013]]).

**Criterion 3 describes a change that was reverted before this note was committed, and names a guard that has never existed.**

`e7c056f` reverted the clause ordering in `Suite.blocking_for` — the tier filter runs first again, and the commit adds a comment saying so. That same commit wrote this note's criterion 3 as `[x]` **"The derived gate loses nothing the tier rule caught"**, with **"The clause now runs first"**, **"This moves a release gate, deliberately: `your-trainer` 60 → 66. The gate got louder, not quieter"**, and the frontmatter **"a superset by six: 0 / 56 / 66 against 0 / 56 / 60"**. Criterion 4, four lines below, says *"I reversed that ordering ... and **reverted it**."* Both cannot be true.

Measured against the committed code:

- `Suite.blocking()` on `your-trainer` is **60**, not 66. The derived gate and the tier rule name the **identical** set in all three repos: 0 / 56 / 60. [[PHASE-036-One-Human-Walk]]'s own exit criterion says exactly this, so the two notes contradict each other.
- **`tests/test_derived_gate.py` does not assert a superset and never has.** `git log --all -S"superset" -- tests/test_derived_gate.py` returns nothing; the assertion has been `derived == tier_rule` since `27e215c` and the docstring still reads *"those must name the identical set."*
- Implementing what criterion 3 describes — fail-closed clause before the tier filter — was applied in a scratch mutation: the gate goes to **66** and `test_the_derived_gate_names_the_same_items_as_the_tier_rule[your-trainer]` **fails**. The criterion therefore asserts a state the committed suite forbids.

**Criterion 4 is sound and is not the problem.** Reverting a gate-tightening change, measuring its cost (60 → 66), citing `TESTING.md`'s *"Tier 3 tests do not gate releases"*, and escalating to [[ISS-0208-Retire-The-Tier-Rule]] rather than shipping it quietly is the correct call — verified: the six checks are real (TST-0592..0597, Tier 3, `mark: todo`, covering nothing), ADR-0034 decision 6 does prescribe retirement after a backfill, and ISS-0208 is `open` with the criterion left `[ ]`. That reconciliation is not a reword. It is criterion 3 that absorbed the claim the reword used to carry.

**The criteria of record show nothing met.** `criteria._declared_criteria` treats the frontmatter `acceptance:` list as the criteria of record; it reads `[ ] [ ] [ ] [~] [ ]` — 0 of 5 — while the body shows four `[x]` and `status:` is `implemented`. [[REQ-0041]] ticks both halves, so the convention is this author's own. The previous review reported 1 of 4 against 4 of 4; the split is now wider.

**To clear this**: restate criterion 3 as what the code does (the derived gate reproduces the tier gate exactly, 0 / 56 / 60, and the fail-closed clause is subordinate to the tier filter — the blind spot ISS-0208 carries), drop the claim about `test_derived_gate.py`, and reconcile the frontmatter list with the body.
