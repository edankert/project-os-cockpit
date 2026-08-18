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
  - "[ ] No gate anywhere reads `level:`, `tier:`, `kind:` or the presence of a `command:` to decide WHETHER something gates. Execution mode may decide what `settled` means; it may not decide what is gated."
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
- [~] **No gate decides WHETHER something gates from `level:`, `tier:`, `kind:` or `command:`.** Reconciled: `blocking_for` still opens on `item.tier not in GATING_TIERS`, so Tier 3 is excluded by the tier field rather than by anything derived. Removing that line changes the blocking set, which independent review demonstrated. **The criterion as written is not met**, and the honest statement is narrower: *no gate decides whether something gates from who RUNS it*. Tier remains a lifetime filter on the release gate, which [[ADR-0034-Three-Axes-Not-One-Word]] decision 6 leaves open rather than resolves.
- [x] **The derived gate names the same blocking set as the tier rule**, per repo, proven by membership rather than count: 0 / 56 / 60.
- [x] **No acceptance row reaches a badge** in any repo: 1 / 0 / 5 / 2, unchanged.

## Corrected after independent review

Two things this note claimed that the code does not do:

1. The tier filter above.
2. **`blocking_for(subjects)` has no production caller.** It is exercised by tests and by `blocking()`'s `subjects=None` case; nothing on a surface passes it a real subject set yet, so *gating at any granularity* is implemented and not yet **used**. That is the difference between a capability and a feature, and it belongs in the record rather than in a later discovery.

## Advanced 2026-08-18

**A fifth thing this requirement did not ask for and got:** a check covering nothing now blocks rather than vanishing. Nine gating checks in `your-trainer` name no subject, and under a naive derived gate they would have been unable to block anything the day somebody unticked one — silently. Failing closed converts that into a loud state without inventing a `covers:` nobody could verify.
