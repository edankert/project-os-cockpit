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
