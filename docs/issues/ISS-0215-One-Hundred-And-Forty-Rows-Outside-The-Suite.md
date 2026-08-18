---
type: "[[issue]]"
id: ISS-0215
aliases: ["ISS-0215"]
title: "140 acceptance rows sit in three unmigrated `TST-*` documents in your-trainer, invisible to the suite and to the release gate"
status: open
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: high
component: docs
phase: "[[PHASE-999-Future]]"
related: ["[[ISS-0213-Acceptance-Tests-Carrying-Level-System]]", "[[ADR-0030-One-Note-Per-Acceptance-Check]]", "[[PHASE-035-Acceptance-Checks-Are-Notes]]"]
---

# The migration reached the suite and not these

Found 2026-08-19 while levelling the five `level: system` manual tests ([[ISS-0213]]). Two were single procedures and were relevelled. The other three are **checklist documents in the pre-migration shape**:

| note | checklist rows |
| --- | --- |
| `TST-0013` iOS parity acceptance | **107** |
| `TST-0011` Android BLE hardening acceptance | 18 |
| `TST-0012` iOS BLE hardening acceptance | 15 |

**140 rows.** Each is an acceptance check by any reading — *"Manual acceptance coverage for everything the iOS parity push implemented, so Edwin can verify each new rider-facing surface before the iOS release"* — and not one of them is in `docs/tests/acceptance/`, so:

- the release gate cannot see them;
- `blocking_for` cannot scope them to a feature or a release;
- they carry no `mark:`, so nothing records whether they were run;
- the tests view shows three rows where there are 140 obligations.

[[PHASE-035]] migrated `ACCEPTANCE_TESTS.md` — the document the suite was named after — and these three were never in it. They were filed as ordinary `TST-*` notes under `docs/tests/`, so every sweep of *the suite* passed over them.

## Why this is not simply "run the migration again"

`TST-0013`'s 107 rows are the iOS parity push, batches 1–33. Splitting them needs a **surface** for each ([[FEAT-0130]]) and a `covers:` naming what each verifies — neither of which the rows carry today. Migrating them into 107 unattributed checks would move the problem rather than fix it, and would add 107 rows to a gate that fails closed on unattributed checks.

## Done when

- [ ] Each of the 140 rows is a check note, with a surface and a `covers:`.
- [ ] Or: a recorded decision that a named subset is retired instead, with the reason.
- [ ] The gate delta is measured and stated before it lands.
