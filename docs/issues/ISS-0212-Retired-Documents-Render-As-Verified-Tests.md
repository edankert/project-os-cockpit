---
type: "[[issue]]"
id: ISS-0212
aliases: ["ISS-0212"]
title: "Three retired documents render as `Verified` tests in your-trainer — a run plan and two checklists, in the group that means `this passed`"
status: fixed
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
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

**The general case is guarded harder than this issue asked for, and not in the nav.** The ask was *"an unrecognised status gets its own visible group"*. It cannot get one, because it cannot reach a committed corpus: an error fires on any value outside the type's allowed set (`active`, `failing`, `retired`, `passing`, `ready`, `draft` for a test), at pre-commit and in CI.

*(**The rule is `NOTE-STATUS`, not `STATUS-VALUE`.** Corrected after independent review, which probed it by committing a `TST-*` at `status: wibble` rather than reading the table. `STATUS-VALUE` reads the **snapshot's** statuses and most `TST-*` notes are not snapshot items, so it would not have fired — naming it would have pointed a future reader at a check that could not catch the case. The conclusion is unchanged; the citation was wrong.)* A nav group for the case would be a second, weaker copy of a check that already fails the commit — and a group nobody may notice is precisely the quiet this issue objects to. The `else` branch is now `Feature tests`, which claims nothing about a verdict.

**The three documents keep `type: [[test]]`**, which satisfies the second clause of the criterion rather than the first: they are not excluded, they are grouped under a label that says *no longer verified*. A run plan is still not a test, but the harm this issue was filed for — a document asserting it had passed — is gone.

`test_no_group_asserts_a_pass_for_a_status_it_does_not_recognise` holds both properties. It is anchored on `^Verified`, not on the substring: the first cut asserted `"verified" not in label` and failed against `Retired · no longer verified` — a label saying the opposite of what the guard was hunting.

## Done when

- [x] A note whose status is terminal-but-not-passing never lands in `Verified`.
- [x] The three documents are grouped by a rule that says why (`Retired · no longer verified`).
- [x] A guard covers the general case — plus the validator rule that makes the nav case unreachable.

## Independent review — 2026-08-20

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `222e19e..6cc7f72`; the author's reasoning trace was not available to it. Verdict: **changes-requested**.

**The rule named is not the rule that fires.** The note (and `test_no_group_asserts_a_pass_for_a_status_it_does_not_recognise`'s docstring) rests the decision *not* to build a nav group on `STATUS-VALUE`. Probed by committing a `TST-*` with `status: wibble` into this repo's corpus and running the validator:

```
ERROR [NOTE-STATUS] TST-9999 status 'wibble' not allowed for test (…);
      the note is not in SNAPSHOT.yaml, so no snapshot-driven check covers it
validate-docs: FAIL (3 errors)
```

The code is **`NOTE-STATUS`**, and its own message says the snapshot-driven check — `STATUS-VALUE`, which reads the *snapshot's* status (`validate_docs_bundled.py:1036`) — does **not** cover it. Since `_tests_groups` reads note frontmatter and most `TST-*` notes are not snapshot items, `STATUS-VALUE` is the wrong rule for this case.

**The conclusion holds**: the value is refused at pre-commit and in CI, so the unreachability argument stands — under a different rule name. The guard asserts against the `ALLOWED_STATUS` table rather than against either rule firing, so *"asserted against the validator rather than assumed"* is a table lookup; the probe above is the missing half. The allowed set quoted (`active`, `draft`, `failing`, `passing`, `ready`, `retired`) is exact.

## Independent review — second pass, 2026-08-20

**This supersedes the first-pass verdict above. Current verdict: approved.** Same reviewer, same conditions — fresh context, separate session, `model:claude-opus-5` — re-run against the working tree after the first pass's findings were acted on. Every claim below was re-measured or re-executed rather than read.

`NOTE-STATUS` is now named, with the reason `STATUS-VALUE` would not fire, and the test docstring carries the same correction. Re-probed: a `TST-*` at `status: wibble` produces `ERROR [NOTE-STATUS] … the note is not in SNAPSHOT.yaml, so no snapshot-driven check covers it` and `validate-docs: FAIL`. The unreachability argument now rests on the rule that actually fires.
