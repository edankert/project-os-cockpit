---
type: "[[requirement]]"
id: REQ-0044
aliases: ["REQ-0044"]
title: "A page whose subject is a release reports the gate and records nothing"
status: implemented
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
priority: high
scope: "release surface"
implements: "[[FEAT-0125-The-Release-Page-Reports-What-Holds-It]]"
acceptance:
  - "[ ] No control on a release page can change a check's mark. Guarded, not merely removed."
  - "[ ] The gate is reported as a verdict plus a breakdown, not as one row per blocking check."
  - "[ ] Every gate row remains a link to the check's own surface, so the walk is one click away."
  - "[ ] The release page shows the open tests for the features it contains."
covers: []
related: ["[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ISS-0210-The-Release-Page-Offers-Sixty-Live-Marks]]"]
tags: [requirement]
---

# A release page records nothing

The rule is [[ADR-0035]]'s: a release is not the subject of an acceptance check, and a page that shows a check's *name* but not its *steps* must not offer the control that attests to the steps.

**Guarded rather than removed** is the operative half of criterion 1. Removing the control fixes today; the guard is what stops the next person adding a convenient tick to the page where clearing the gate is the goal. The same control has now been removed twice from two surfaces ([[ISS-0192]], then this) and neither removal left a test behind.

## Acceptance criteria

- [x] No control on a release page can change a check's mark. — evidence: `test_the_release_page_has_no_write_path_for_a_check`; [[ADR-0035]].
- [x] The gate is a verdict plus a breakdown — **and the rows beneath it**, up to 40. Evidence: `test_the_gate_breakdown_is_lossless_and_sums_to_its_list` (the parts sum to the list, so the breakdown cannot drop a row) — note that this test asserts the rows *survive*, which is the opposite of the "not one row per blocking check" reading the prose invited. Corrected on review 2026-08-20.
- [x] Gate rows link to the check. — evidence: `tests/test_release_page.py:243` and `:521` assert the row renders `'scoped-row-id mono ov-typed'` with `dataset.type = 'test'`; `test_the_breakdown_chip_opens_rows_that_exist` proves the target resolves.
- [x] Open tests for the release's contents are shown. — evidence: `publication._open_tests_for_contents`, filtered on `item.settled`; asserted on both payload and renderer in `tests/test_release_page.py`.

## Independent review — fifth pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`. **What was independent: the context** — this pass started from the notes and the diff at `c9c9563` and never saw the author's reasoning. **What was not: the model** — same family as the author, recorded in `reviewed_by` as provenance (ADR-0013). Verdict: **changes-requested**. Every claim below was executed or measured, not read.

**Criterion 2 is false as worded.** *"The gate is reported as a verdict plus a breakdown, **not as one row per blocking check**"* — the page reports a verdict, a breakdown, **and** one row per blocking check (capped at 40 with a `…N more` line). `gateGroup` renders `gateAreaBreakdown(items)` and then the `gate-rowlist`; the cited test, `test_the_gate_breakdown_is_lossless_and_sums_to_its_list`, asserts the breakdown comes **before** the rows — i.e. that the rows are still there. The implementing task [[TASK-0503]] says so plainly (*"in front of the blocking list — never instead of it"*). The breakdown half of the criterion is met and well guarded; the *"not as one row per blocking check"* half describes a page that was deliberately not built.

**Criterion 3's evidence is described more strongly than it is.** The note says `tests/test_release_page.py:243` and `:521` *"assert the row renders `'scoped-row-id mono ov-typed'` with `dataset.type = 'test'`"*. They assert the class string only. `n.dataset.type = 'test'` is real in the gate-row builder, but the sole assertion of it anywhere in the suite is `tests/test_tests_view.py:2507`, which is a different surface. Line-number citations also drift on the next edit; a test name survives.

**Criteria 1 and 4 verified by mutation** — see [[FEAT-0125]] for the two mutants and which test each fired.
