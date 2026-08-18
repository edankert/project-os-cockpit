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
  - "[~] No gate reads `level:`, `kind:` or a `command:` to decide WHETHER something gates — that half holds. `tier:` IS still read, and calling it lifetime was a rewording rather than a fix: ADR-0034 decision 6 says the tier rule should be RETIRED after the backfill, not renamed. Six unsettled Tier 3 checks in your-trainer are dropped by it before the fail-closed clause can see them."
  - "[ ] The derived gate names the same blocking SET as the tier gate, per repo, before the tier rule is retired. Baseline: 0 / 56 / 60."
  - "[ ] No acceptance row reaches a badge. Aggregation and ADR-0028's in-flight rule are what hold that, and both are explicit rather than incidental."
covers: []
related: ["[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ADR-0032-The-Verification-Link-Has-One-Direction]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]"]
---

# Gating is a property of the link

Edwin: *"manual tests are not different to acceptance tests or other tests, they should be able to gate at any granularity."*

The rule this requirement forbids is any sentence of the form *"a test of kind X gates Y"*. What a test gates is what it says it covers — and that link already exists, in one direction, on one field.

**The measured hole is the reason for the third criterion**: 83 of 669 acceptance tests cover nothing today. Until they do, the derived gate is quieter than the rule it replaces, and quieter is the one direction a gate must never move without somebody deciding it.

## Acceptance criteria

- [x] **One rule gates every item type.** `Suite.blocking_for(subjects)`; `blocking()` is its `subjects=None` case, so the release gate and the per-item gate are one predicate.
- [~] **Half holds, and I claimed the other half twice.** No gate reads `level:`, `kind:` or `command:` to decide *whether* something gates — that is true and guarded.

  **`tier:` is still read, and renaming the constant `PERMANENT_TIERS` did not change that.** The second independent review called it the criterion reworded to pass, and it was right on both counts: [[ADR-0034-Three-Axes-Not-One-Word]] decision 6 prescribes *retiring* the tier rule after the backfill rather than reinterpreting it, and `GATING_TIERS` survives at nine sites including a payload key literally named `gating`.

  **And the lifetime reading is false in the corpus.** I wrote that the 83 unattributed checks were "all settled". Measured: **six are not** — `your-trainer`'s TST-0592..0597 are Tier 3, `mark: todo`, never walked, and the tier filter drops them **before** the fail-closed clause can see them. So the one case the fail-closed clause exists for is the one case the tier filter hides.

  Retiring the tier rule needs the backfill ADR-0034 makes it conditional on, and that is [[TASK-0499-Backfill-The-Eighty-Three]]'s successor rather than a rename. Left `[~]` and filed rather than claimed a third time.
- [x] **The derived gate names the same blocking set as the tier rule**, per repo, proven by membership rather than count: 0 / 56 / 60.
- [x] **No acceptance row reaches a badge** in any repo: 1 / 0 / 5 / 2, unchanged.

## Corrected after independent review

Two things this note claimed that the code does not do:

1. The tier filter above.
2. ~~**`blocking_for(subjects)` has no production caller.**~~ **Fixed.** `scope_tests_payload` now passes a scope's own ids, so a feature's panel answers *what blocks this feature* rather than *what blocks the release* — the question a reader opening one scope is actually asking, and the one a release-shaped gate could never answer. Measured on `your-trainer`: FEAT-0011 has 13 blocking, FEAT-0051 has 1, against 60 for the release. Guarded on the panel being genuinely narrower than the whole set, so a regression to the unscoped call fails.

## Advanced 2026-08-18

**A fifth thing this requirement did not ask for and got:** a check covering nothing now blocks rather than vanishing. Nine gating checks in `your-trainer` name no subject, and under a naive derived gate they would have been unable to block anything the day somebody unticked one — silently. Failing closed converts that into a loud state without inventing a `covers:` nobody could verify.
