---
type: "[[requirement]]"
id: REQ-0048
aliases: ["REQ-0048"]
title: "A preparing release can be composed from features and phases, and its gate reports what blocks it"
status: implemented
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
priority: medium
scope: "release surface"
implements: "[[FEAT-0129-A-Release-Names-Its-Own-Contents]]"
acceptance:
  - "[ ] A preparing release can add and remove features and phases from the cockpit, written to `features:` on its own note."
  - "[ ] A phase contributes its features; the phase is not stored as a second encoding of the same set."
  - "[ ] When a release names contents, its gate is `blocking_for(those subjects)` rather than the whole suite."
  - "[ ] A release naming nothing behaves exactly as today — derived contents, whole-suite gate. The new path is opt-in."
  - "[ ] The write refuses on a frozen release, like every other release write."
covers: []
related: ["[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ISS-0206-A-Check-Cannot-Belong-To-A-Release]]"]
tags: [requirement]
---

# Composing a release

Criterion 4 is the safety property. Deriving contents is what every existing release relies on, and a picker that quietly changed the meaning of `features: []` would rewrite the gate for eleven historical releases. Named contents are **opt-in**, and absence keeps today's behaviour.

Criterion 3 is what makes the picker worth building rather than merely convenient: it is the difference between a release page reporting *the suite* and reporting *itself*. `blocking_for(subjects)` exists and has a production caller; this gives it the subject set a release actually has.

## Acceptance criteria

- [x] Add and remove features and phases from the cockpit. — evidence: `test_add_then_remove_round_trips`; the endpoint is loopback-only (`test_the_endpoint_is_loopback_only`).
- [x] A phase contributes features; no second encoding. — evidence: `test_a_phase_contributes_its_features_and_is_not_stored`, `test_a_phase_clash_names_the_feature_not_the_phase`.
- [x] Named contents scope the gate. — evidence: `test_a_release_that_names_contents_subtracts_from_its_own_gate`; [[ADR-0040]] — selection subtracts, never divides, so a check covering one held-back and one carried feature still gates.
- [x] Naming nothing keeps today's behaviour. — evidence: `test_nothing_held_back_moves_no_gate`; the invariant eleven historical releases depend on.
- [x] Frozen releases refuse. — evidence: `test_a_shipped_release_is_immutable`, `test_compose_is_offered_only_before_a_release_ships`.

## Independent review — fifth pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`. **What was independent: the context** — this pass started from the notes and the diff at `c9c9563` and never saw the author's reasoning. **What was not: the model** — same family as the author, recorded in `reviewed_by` as provenance (ADR-0013). Verdict: **approved**. Every claim below was executed or measured, not read.

All five criteria trace to tests that exist, pass, and assert the stated property. Verified by mutation rather than by reading — see [[FEAT-0129]] for the six mutants (four on `blocking_minus`, two on the `release_contents` refusals), all caught.

Two details I checked because they are the kind that get asserted loosely and were not: criterion 1's round-trip test asserts the **inline list form** in the written file (`features: ["[[FEAT-0001-Thing]]"]`, never a quoted string — [[FEAT-0107]]'s defect), and criterion 2's test asserts `"PHASE-0001" not in raw`, which is the *no second encoding* half stated as a negative rather than implied by the positive.

Criterion 4 is the safety property this requirement turns on, and it is guarded on both the unit (`blocking_minus(None)` and `blocking_minus(set())` equal `blocking()`) and the wiring (`gate("[]") == 2` → `gate(one) == 1` → `gate(both) == 2`). Removing the short-circuit fails the suite; it is load-bearing, not decorative.
