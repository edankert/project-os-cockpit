---
type: "[[issue]]"
id: ISS-0199
aliases: ["ISS-0199"]
title: "20 of 61 feature→test edges are not reciprocated — the verification link is hand-maintained in two directions and a third of it already disagrees"
status: open
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: docs
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
related: ["[[ADR-0032-The-Verification-Link-Has-One-Direction]]", "[[FEAT-0121-The-Verification-Link-Normalises]]", "[[TASK-0486-Backfill-Covers-On-The-Ten]]", "[[ISS-0195-Two-Types-Carry-One-Act]]"]
---

# A third of the verification link disagrees with itself

Measured across the fleet, 2026-08-18, while answering Edwin's question about link direction.

One relationship — *this test verifies that feature* — is encoded three ways: the **directory path** (37 tests under `docs/features/<slug>/plan/tests/`), the **test's own** `features:`/`verifies:`/`validates:` (82 tests), and the **feature's** `tests:` list (61 edges).

**10 of those 61 edges are not reciprocated**: the feature claims a test verifies it and the test does not name the feature. By repo — `project-os-cockpit` 8, `project-os-dev` 2. *Corrected 2026-08-18: the title's "20" and `your-health`'s 10 were wrong. Independent review re-derived it — those ten reciprocate, and the first pass counted them as drift by reading only `features:` and not the other names a test may use. The defect is real and a sixth the size.*

Nothing reconciles the two sides, so the disagreement is silent and neither surface is wrong by its own data. A reader asking *what verifies FEAT-0059* gets a different answer depending on which end they ask from.

## Not a data-entry problem

Ten errors in sixty-one hand-maintained bidirectional edges is a **16% failure rate**, which is what hand-maintained bidirectional links cost. Adding a validator rule that the two sides agree would make it loud without making it go away — and all twenty would have to be fixed before the rule could be switched on, at which point one side is redundant.

[[ADR-0032-The-Verification-Link-Has-One-Direction]] proposes deleting two of the three encodings instead. This issue closes **by construction** when it lands: with one encoding there is no second copy to disagree.

## Next actions

- [ ] Resolve the twenty in [[TASK-0486-Backfill-Covers-On-The-Ten]], recording which side was right in each case, while both sides still exist to compare.
- [ ] Do not add a reconciliation rule in the meantime — it is work against a field that is being removed.
