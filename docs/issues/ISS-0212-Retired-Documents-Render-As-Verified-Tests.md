---
type: "[[issue]]"
id: ISS-0212
aliases: ["ISS-0212"]
title: "Three retired documents render as `Verified` tests in your-trainer — a run plan and two checklists, in the group that means `this passed`"
status: open
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

## Done when

- [ ] A note whose status is terminal-but-not-passing never lands in `Verified`. Fail loud, not quiet: an unrecognised status gets its own visible group rather than the pass bucket.
- [ ] The three documents stop being typed as tests, or are excluded by a rule that says why.
- [ ] A guard covers the general case, not the three ids.
