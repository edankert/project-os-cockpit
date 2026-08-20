---
type: "[[issue]]"
id: ISS-0212
aliases: ["ISS-0212"]
title: "Three retired documents render as `Verified` tests in your-trainer — a run plan and two checklists, in the group that means `this passed`"
status: fixed
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: cockpit-server
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[FEAT-0127-Every-Row-In-The-Tests-View-Is-A-Test]]", "[[ADR-0034-Three-Axes-Not-One-Word]]"]
---

# `Verified` is the else-branch, so anything unrecognised lands in the one group that asserts a pass

Edwin: *"on the tests view, the needs a walk view and 'Resting no feature in flight' view are not showing the correct TSTS."*

## Measured

`_tests_groups` on `your-trainer` puts these in **`Verified`**:

| id | `status:` | what it actually is | path |
| --- | --- | --- | --- |
| `ACCEPTANCE-CHECKLIST-2.1.1` | `retired` | a checklist | `tests/ACCEPTANCE_CHECKLIST_v2.1.1.md` |
| `ACCEPTANCE-TESTS-V2-1-0` | `retired` | a test *list* | `tests/ACCEPTANCE_TESTS_v2.1.0.md` |
| `ACCEPTANCE-RUN-2.1.1` | `retired` | a **run plan** | `tests/ACCEPTANCE_RUN_PLAN_v2.1.1.md` |

All three carry `type: "[[test]]"`, no `level:`, and `status: retired`.

## Two bugs stacked

1. **A retired note is reported as verified.** `_tests_groups` buckets by a chain of `elif`s ending in `else: verified`. `retired` matches nothing above it, so it falls into the group whose label asserts the strongest possible claim — *this was checked and it passed*.
2. **These are not tests.** They are the documents the suite was migrated *out of* ([[PHASE-035]]), left behind carrying the type. A run plan has no verdict to report.

The first is the dangerous one and is general: **any status the chain does not name reads as `Verified`**. `retired` is merely the one the corpus happens to contain.

## Resolved 2026-08-20

**There is no `Verified` group any more.** `_tests_groups` buckets on `_RESOLVED_NOT_PASSING` first, so a `retired` note routes to a band that names what it is. Measured on `your-trainer`: all three documents land in `Retired · no longer verified`, alongside six retired `TST-*`.

**The general case is guarded harder than this issue asked for, and not in the nav.** The ask was *"an unrecognised status gets its own visible group"*. It cannot get one, because it cannot reach a committed corpus: `STATUS-VALUE` errors on any value outside the type's allowed set (`active`, `failing`, `retired`, `passing`, `ready`, `draft` for a test), at pre-commit and in CI. A nav group for the case would be a second, weaker copy of a check that already fails the commit — and a group nobody may notice is precisely the quiet this issue objects to. The `else` branch is now `Feature tests`, which claims nothing about a verdict.

**The three documents keep `type: [[test]]`**, which satisfies the second clause of the criterion rather than the first: they are not excluded, they are grouped under a label that says *no longer verified*. A run plan is still not a test, but the harm this issue was filed for — a document asserting it had passed — is gone.

`test_no_group_asserts_a_pass_for_a_status_it_does_not_recognise` holds both properties. It is anchored on `^Verified`, not on the substring: the first cut asserted `"verified" not in label` and failed against `Retired · no longer verified` — a label saying the opposite of what the guard was hunting.

## Done when

- [x] A note whose status is terminal-but-not-passing never lands in `Verified`.
- [x] The three documents are grouped by a rule that says why (`Retired · no longer verified`).
- [x] A guard covers the general case — plus the validator rule that makes the nav case unreachable.
