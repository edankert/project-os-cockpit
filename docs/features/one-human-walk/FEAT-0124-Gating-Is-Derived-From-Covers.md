---
type: "[[feature]]"
id: FEAT-0124
aliases: ["FEAT-0124"]
title: "Gating is derived from `covers:` — one rule at every granularity, and the tier gate retires only once the derived one is proven identical"
status: done
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
goal: "Replace every gate keyed on a test's level or tier with one rule read from `covers:` — an item may not reach a terminal status while a test covering it is unsettled — so that a task, an issue, a requirement, a feature and a release are gated by the same sentence, and no rule anywhere asks what kind of test it is."
requirements: ["[[REQ-0043-Gating-Is-A-Property-Of-The-Link]]"]
tasks: ["[[TASK-0499-Backfill-The-Eighty-Three]]", "[[TASK-0500-Derive-The-Gate-From-Covers]]", "[[TASK-0501-Prove-The-Derived-Gate-Then-Retire-The-Tier-Rule]]"]
release: ""
acceptance: ""
design: ""
related: ["[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ADR-0032-The-Verification-Link-Has-One-Direction]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]"]
reviewed_by: model:claude-opus-5
review_date: 2026-08-18
review_verdict: changes-requested
---

# Gating is derived from `covers:`

**Edwin's point, and it is not new mechanism.** [[ADR-0032-The-Verification-Link-Has-One-Direction]] already made `covers:` the single encoding of what a test verifies; only the release gate reads it, and only as a tier filter. Deriving every gate from it is reading a link the corpus already carries.

One rule replaces three: **an item may not reach a terminal status while a test covering it is unsettled.** A release is an item whose covered set is the union of its contents'. Granularity stops being a property of the test — which is exactly what *"they should be able to gate at any granularity"* asks for.

## The precondition, and it is the whole risk

**83 of 669 acceptance tests carry an empty `covers:` — 12%.** *(Measured further during the work: **74 are Tier 3**, which does not gate, and only **9 are Tier 1/2**. The precondition was a twelfth of its stated size, and the nine were closed in the gate rather than by inventing data — see [[TASK-0499-Backfill-The-Eighty-Three]].)* Under a derived gate those 83 gate nothing and leave the release **silently**. The tier rule (`tier` in 1/2 and unsettled) has no such hole.

So the order is forced, and [[TASK-0501-Prove-The-Derived-Gate-Then-Retire-The-Tier-Rule]] exists to enforce it: backfill, then prove the derived gate reproduces the tier gate **per repo** — 0 / 56 / 60 blocking — and only then retire the tier rule. **A gate that goes quiet during a migration is the failure this project has already paid for once**, in a repo where nobody was looking.

## What this must not become

Uniform gating must not become **per-check obligations**. [[ADR-0027-The-Registry-Counts-What-Needs-A-Person]] is untouched: what keeps 669 rows off a badge is aggregation — *"60 unwalked checks stand between this release and shipping"*, one row — plus [[ADR-0028-Work-Has-Three-Phases]]'s in-flight rule. Both were incidental before; under a uniform gate they become load-bearing and must be explicit.
