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
  - "[x] No gate reads `level:`, `kind:` or a `command:` to decide WHETHER something gates; execution mode decides only what `settled` MEANS. `tier:` is read as LIFETIME (ADR-0034 decision 6) — does this test still apply — which is prior to gating rather than a kind of it, and the constant is named `PERMANENT_TIERS` so the code says which question it is asking."
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
- [x] **No gate decides whether something gates from `level:`, `kind:` or `command:`.** Execution mode decides only what *settled* means.

  **`tier:` is read, and the criterion was wrong to forbid it outright** — which independent review was right to catch and which is settled here rather than reconciled away. [[ADR-0034-Three-Axes-Not-One-Word]] decision 6 says tier survives as a **lifetime** field, and TESTING.md defines Tier 3 as *"a one-time check for a specific build, promoted or removed after a verified release."* A test that has stopped applying cannot sensibly hold anything open, so asking *does this still apply* is **prior to** gating rather than a kind of it. The constant is now `PERMANENT_TIERS`, so the code names the question it is asking. Measured: 74 of `your-trainer`'s 83 unattributed checks are Tier 3 — already retired in practice.
- [x] **The derived gate names the same blocking set as the tier rule**, per repo, proven by membership rather than count: 0 / 56 / 60.
- [x] **No acceptance row reaches a badge** in any repo: 1 / 0 / 5 / 2, unchanged.

## Corrected after independent review

Two things this note claimed that the code does not do:

1. The tier filter above.
2. ~~**`blocking_for(subjects)` has no production caller.**~~ **Fixed.** `scope_tests_payload` now passes a scope's own ids, so a feature's panel answers *what blocks this feature* rather than *what blocks the release* — the question a reader opening one scope is actually asking, and the one a release-shaped gate could never answer. Measured on `your-trainer`: FEAT-0011 has 13 blocking, FEAT-0051 has 1, against 60 for the release. Guarded on the panel being genuinely narrower than the whole set, so a regression to the unscoped call fails.

## Advanced 2026-08-18

**A fifth thing this requirement did not ask for and got:** a check covering nothing now blocks rather than vanishing. Nine gating checks in `your-trainer` name no subject, and under a naive derived gate they would have been unable to block anything the day somebody unticked one — silently. Failing closed converts that into a loud state without inventing a `covers:` nobody could verify.
