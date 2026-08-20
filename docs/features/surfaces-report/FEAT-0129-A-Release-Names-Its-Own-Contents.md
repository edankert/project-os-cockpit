---
type: "[[feature]]"
id: FEAT-0129
aliases: ["FEAT-0129"]
title: "A release names its own contents — features and phases are chosen, not only derived — and the gate scopes to them"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
requirements: ["[[REQ-0048-A-Release-Can-Be-Composed]]"]
tasks: ["[[TASK-0511-A-Picker-Writes-Features-And-Phases]]", "[[TASK-0512-The-Gate-Scopes-To-The-Release]]", "[[TASK-0557-One-Release-Per-Platform]]", "[[TASK-0558-A-Release-Composes-Its-Contents]]"]
related: ["[[ISS-0206-A-Check-Cannot-Belong-To-A-Release]]", "[[FEAT-0125-The-Release-Page-Reports-What-Holds-It]]"]
tags: [feature]
---

# Choosing what ships

Edwin: *"on the release view I would like to be able to select the features and/or phases to add to a release."*

Today a release's contents are **derived** — *"32 features unshipped since REL-0012"* — or **frozen** at `Mark released`. There is no middle state, which is the state a person preparing a release is actually in: `REL-0013` is `preparing: 2026-08-16` with `features: []` and 32 derived rows.

The field already exists and is already used: `REL-0001` carries 27 `features:` entries. What is missing is a way to put them there other than by hand.

**This is the one item here that is new scope rather than a fix**, and it unlocks the other half of [[FEAT-0125]]: once a release names its features, `blocking_for(subjects)` scopes the gate to them, and *"what holds this release"* stops meaning *"what holds any release"*. It also bears on [[ISS-0206]] — a check that cannot be scoped to a release — without resolving it: choosing features narrows the gate honestly, where inventing a `release:` field on a check would encode something derivable.

## Acceptance

- [x] A preparing release can add and remove features and phases, written to its note. — `test_add_then_remove_round_trips`, `test_a_shipped_release_is_immutable`, `test_an_unresolvable_id_is_refused`.
- [x] Adding a phase adds its features, and says so rather than storing a second encoding. — `test_a_phase_contributes_its_features_and_is_not_stored`, `test_a_phase_clash_names_the_feature_not_the_phase`.
- [x] With contents named, the gate reports what blocks *this* release. — `test_a_release_that_names_contents_subtracts_from_its_own_gate` ([[ADR-0040]]: selection subtracts, never divides).
- [x] A release with no named contents keeps today's derived behaviour. — `test_nothing_held_back_moves_no_gate`; the invariant eleven historical releases depend on.
- [x] **One preparing release per platform**, and two on one platform is an error — the state [[ADR-0037]]'s ledger cannot represent, since sealing assigns one working ledger to one release. *Edwin, 2026-08-19: two concurrent releases on a platform are a branch, not a schema problem.* — evidence: `test_two_preparing_on_one_platform_is_an_error`, `test_two_platforms_preparing_at_once_is_fine`, `test_a_release_with_no_platform_is_its_own_key`; the `RELEASE-PREPARING` validator error, `tests/test_release_preparing.py`.
- [x] **A feature in two open releases on the same platform is an error; across platforms it is the normal case.** The obvious version of this rule — any two open releases — is wrong the first time a feature ships to both, which is where it is going ([[ISS-0236]]). — evidence: `test_the_same_feature_in_two_open_releases_on_one_platform_is_refused`, `test_across_platforms_it_is_the_normal_case`, `test_a_candidate_is_not_claimed_by_another_release_on_this_platform`.

## Independent review — fourth pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`. Verdict: **approved**. Re-measured or re-executed, not read.

All six criteria trace to mechanisms I have now re-executed:

1. add/remove features and phases — `release_contents`, 5 refusal mutants, all caught.
2. a phase contributes rather than stores — mutant caught by three tests.
3. with contents named, the gate reports what blocks *this* release — `blocking_minus` wired through `release_payload`; 59 → 58 when `FEAT-0047` is held back.
4. **no named contents keeps derived behaviour** — the one flagged, and it is the strongest of the six: `blocking_minus(None)` and `blocking_minus(set())` both return exactly `blocking()` (59 on the live corpus), and removing the `if not deselected: return base` short-circuit fails **14** tests, so it is load-bearing rather than a convenience.
5. one preparing release per platform — 3 mutants, all caught.
6. same-platform clash is an error, cross-platform is normal — 2 mutants, caught, including the per-contributed-feature case that names the member rather than the phase.

Status is `doing` with the boxes unticked, which is right — the criteria are met in mechanism, and nothing here ticked itself.

## Independent review — fifth pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`. **What was independent: the context** — this pass started from the notes and the diff at `c9c9563` and never saw the author's reasoning. **What was not: the model** — same family as the author, recorded in `reviewed_by` as provenance (ADR-0013). Verdict: **approved**. Every claim below was executed or measured, not read.

All six criteria name tests that exist, pass, and assert the property claimed. I re-executed the mechanisms rather than reading the assertions.

**Mutants, all caught.** On `blocking_minus`: subset→intersection (the mixed cell), the `if not deselected: return base` short-circuit, the no-`covers:` fail-closed clause, and the non-feature-subject clause — four for four against `tests/test_gate_subtraction.py`. On `note_writes.release_contents`: the shipped-release refusal and the same-platform clash refusal, both caught by `tests/test_release_contents.py`.

**Criterion 4 remains the strongest**, and it is the one an author is most tempted to assume: `test_nothing_held_back_moves_no_gate` asserts `blocking_minus(None)` and `blocking_minus(set())` both equal `blocking()`, and the end-to-end test pins `gate("[]") == 2`, `gate('["[[FEAT-0001]]"]') == 1`, `gate(both) == 2` on constructed input — which is the right call, since no repo composes a release yet and a corpus guard here would never fire.

**Criterion 2's test asserts the negative that matters**: `"PHASE-0001" not in raw`, so the phase is genuinely not stored as a second encoding, and the clash message names the member rather than the phase.

**One stale sentence, not a finding against the work:** the fourth-pass section below ends *"Status is `doing` with the boxes unticked, which is right"*. It is now `done` with the boxes ticked — that pass's `approved` was carried into a close-out it did not review. This pass reviews the closed state and approves it.
