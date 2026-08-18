---
type: "[[feature]]"
id: FEAT-0113
aliases: ["FEAT-0113"]
title: "The check type and the migration — one note per acceptance check, upstream first, pilot here, fleet last"
status: done
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["Edwin 2026-08-17: 'I want to consider the TST note approach to capture acceptance tests … having this granularity should allow us to build a lot more functionality around these TST notes.'", "Independent functionality review, round 3, 2026-08-17 — the schema, the migration plan and the two-shape delta are its design"]
goal: "An acceptance check is a first-class note — type `check`, id `CHK-*`, `status:` for lifecycle and `mark:` for verdict — and all 669 rows across the three suites that exist migrate with parity asserted, without the release-gate delta losing a single historical tag."
requirements: []
tasks: ["[[TASK-0459-The-Check-Type-Lands-Upstream]]", "[[TASK-0460-The-Migration-Script]]", "[[TASK-0461-Pilot-This-Repo]]", "[[TASK-0462-The-Delta-Reads-Two-Shapes]]", "[[TASK-0463-The-Fleet-Migrates-Trainer-Last]]"]
design: ""
release: ""
depends: []
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[FEAT-0112-The-Acceptance-Suite-Gets-A-Machine-Readable-Projection]]", "[[ISS-0173-The-Suites-Own-Ids-Are-Written-In-A-Form-Nothing-Reads]]", "[[ISS-0178-A-Test-Cannot-Be-Retired]]", "[[PHASE-035-Acceptance-Checks-Are-Notes]]"]

---

# The check type and the migration

## What this is

The record half of [[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]: the `check` note type exists (upstream first — TAXONOMY.md, STATUSES.md, QUALITY.md, SCHEMAS.md, `validate-docs.py`, then synced down), a migration script turns suite rows into `CHK-*` notes with nothing lost, this repo pilots it at 34 rows, the delta learns to read file-shape at old refs and note-shape at new ones, and the fleet follows — `your-sudoku` (56), then `your-trainer` (579) last, after the schema has survived a real sweep.

## The schema, fixed by the ADR

`status:` is `draft`/`active`/`retired` and never carries a verdict. `mark:` is [[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]'s six values, beside `verdict_date:`, `verdict_reason:`, `invalidated_by:` (change id, reason, date — the RE-RUN triple, structured), `automation:` + `covered_by:`, `tier:`, `section:`/`area:`/`ordinal:` (display order only — ordinal is sparse, so inserts stop shifting anything), `covers:` (resolvable refs — [[ISS-0173-The-Suites-Own-Ids-Are-Written-In-A-Form-Nothing-Reads]] dissolves), `evidence:`, optional `burden:`, and `migrated_from:` (the old `#section.ordinal` address plus the pre-migration sha).

## Acceptance criteria

- [ ] The `check` type validates in every fleet repo after one template sync, and a `CHK-*` note with a verdict but no status change passes the validator, the review gate and the runner-status rule untouched.
- [ ] `acceptance.parse` output and migrated notes agree per repo — row count, marks, tiers, rerun reasons, refs — asserted by the migration itself, not by eye.
- [ ] `docs/tests/ACCEPTANCE_TESTS.md` is deleted in the migration commit and a README says where checks live and how to read pre-migration history.
- [ ] `gate_payload` at every real `your-trainer` tag returns the same blocking numbers after the cut as before it.
- [ ] The `CHK` counter exists per repo and `sync-snapshot.py` raises it like any other.

## Closed 2026-08-18

Every task scope-resolved and the linked tests `passing` — the feature had sat at `review` since its build leg finished on 2026-08-17, which is the state PHASE-035 could not close through.

**And it is closed knowing what came next.** [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] superseded this phase's own [[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]] one day after it was accepted, so parts of what this feature built have already been replaced. That is not a reason to leave it open: what it delivered was delivered, the record of *why the sibling type existed* is what makes ADR-0031 legible, and a feature left at `review` because its decision moved on is a phase that can never close.
