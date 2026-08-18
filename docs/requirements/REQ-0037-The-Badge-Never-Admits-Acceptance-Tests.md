---
type: "[[requirement]]"
id: REQ-0037
aliases: ["REQ-0037"]
title: "The obligation badge never admits acceptance tests — the merge must not put 669 self-re-arming rows in front of a person"
status: draft
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: high
scope: "obligation registry"
implements: "[[FEAT-0118-The-Test-Type-Absorbs-The-Check]]"
acceptance:
  - "[ ] After the merge, the Tests badge in every repo reads what it read before it — measured per repo, not in aggregate. Baseline 2026-08-18: project-os-cockpit 1, your-trainer 5."
  - "[ ] No acceptance test appears in `obligations.owed_items` in any repo, at any status."
  - "[ ] A guard asserts the badge total across the fleet is unchanged by the migration, and fails loudly if an acceptance test ever reaches a status the Run obligation counts."
covers: []
related: ["[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[ADR-0028-Work-Has-Three-Phases]]"]
---

# The badge never admits acceptance tests

[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]] called acceptance rows *"the most self-re-arming population in the corpus"* and forbade per-check obligations. [[ADR-0030]] honoured it by giving checks their own type; [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] takes the type away and must honour it another way.

**It does so by construction, not by exemption.** `_is_owed` requires `status in ("ready",)` for a test; an acceptance test rests at `active`. The requirement exists because that construction is one careless status write away from failing, and the failure mode is 669 rows arriving on a badge at once.

**This is the single highest-risk invariant in the merge.** Everything else is recoverable by editing notes; this one is recoverable only after somebody has seen a number they cannot act on, which is the exact harm ADR-0027 exists to prevent.
