---
type: "[[requirement]]"
id: REQ-0047
aliases: ["REQ-0047"]
title: "The tests view opens on what is owed and what has moved, with the inventory one click away"
status: implemented
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
priority: medium
scope: "tests view"
implements: "[[FEAT-0128-The-Tests-View-Leads-With-The-Work]]"
acceptance:
  - "[ ] The landing state of the tests view is not a list of every test. On a 579-test repo the reader sees groups and counts, not rows."
  - "[ ] Each tier reports walked, needing re-run, and still to walk — derived, never authored."
  - "[ ] Nothing is removed: every collapsed group expands to exactly the rows it collapsed."
  - "[ ] Feature tests appear above the flat state groups."
covers: []
related: ["[[ADR-0028]]", "[[ISS-0204-The-Acceptance-Filter-Bar-Is-Congested]]"]
tags: [requirement]
---

# Owed first, inventory on request

The view was built when the corpus had 23 tests, where showing all of them WAS the summary. At 579 it is a wall, and the same change that made it a wall — [[PHASE-035]]'s migration — also gave every row a state worth counting.

**Criterion 3 is the constraint on the other three.** The easy version of this feature deletes rows; the correct one moves them behind a summary that says how many there are. Every count must expand to its own rows, or the collapse has hidden work rather than organised it.

## Acceptance criteria

- [x] The landing state is not the inventory. — evidence: `test_the_nav_leads_with_what_is_owed` and `test_what_actually_hoists_needs_you_is_the_partition_not_the_index`. *(The index is **not** the mechanism: `_tests_groups` ends `return owed + rest`, partitioned on `needs_human`, and review showed that moving `needs-you`/`broken-command` to ranks 8 and 9 changes nothing. The original citation named the wrong cause.)*
- [x] Per-tier walked / re-run / to-walk, derived. — evidence: `test_the_tracking_line_counts_re_runs_and_stale_ticks_separately`; counts come from `_section_head_label`, derived, never stored.
- [x] Every collapsed group expands losslessly. — evidence: **`test_the_view_holds_the_whole_test_corpus`** (set equality against `notes_by_type("test")`, so a dropped row fails), with `test_both_storage_locations_reach_the_view` and `test_an_empty_group_is_absent_rather_than_zero`. *(**Citation corrected on review.** This first named `test_the_lines_count_equals_the_rows_it_expands_to`, `test_the_gate_breakdown_is_lossless_and_sums_to_its_list` and `test_every_test_appears_in_exactly_one_group` — all real, all passing, and **all three survive a row-dropping mutant**: the first exercises the FEATURES view, the second the RELEASE page, and the third searches only for duplicates, so a row in zero groups passes it. Appending `[1:]` to the `items` comprehension in `_tests_groups` fails 14 tests and not one of them was cited. Citing a real test that guards a different property is the same defect as citing one that does not exist, in better disguise.)*
- [x] Feature tests lead — **among the three derived sections** (`feature` / `regression` / `automated`), with `needs-you` and `broken-command` ahead of all three. Evidence: `test_the_section_order_is_pinned_and_feature_leads_the_derived_three`. See [[FEAT-0128]] — this was previously ticked against a guard that does not exist.

## Independent review — fifth pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`. **What was independent: the context** — this pass started from the notes and the diff at `c9c9563` and never saw the author's reasoning. **What was not: the model** — same family as the author, recorded in `reviewed_by` as provenance (ADR-0013). Verdict: **changes-requested**. Every claim below was executed or measured, not read.

**Three of the four criteria are ticked against tests that guard something else.** The property in each case may well hold; the named evidence does not establish it, which is the defect [[FEAT-0128]]'s phantom was the loud version of.

**Criterion 1** — *"the landing state is not a list of every test"*. `test_the_nav_leads_with_what_is_owed` asserts that surfaces inside tier groups are ordered by percentage incomplete, and that owed checks precede settled ones within a surface. It asserts nothing about collapse, counts, or the absence of rows. The second half of the evidence — *"`needs-you` is index 0 in `_SECTION_ORDER_INDEX`"* — names the wrong mechanism: setting `needs-you: 8` and `broken-command: 9` leaves the emitted order unchanged, because `_tests_groups` ends `return owed + rest` and the `needs_human` partition is what hoists them (executed).

**Criterion 3** — *"every collapsed group expands to exactly the rows it collapsed"*. Executed: dropping the first row of every tests-view group (`[1:]` on the `items` comprehension in `_tests_groups`) leaves **all three cited tests green**:

- `test_every_test_appears_in_exactly_one_group` only searches for **duplicates**; a row in *zero* groups passes it. The parenthetical *"a partition, so collapsing cannot drop or duplicate a row"* claims half a property the test does not have.
- `test_the_lines_count_equals_the_rows_it_expands_to` exercises `cockpit.suppressed_group(index, "features")` — the **features** view.
- `test_the_gate_breakdown_is_lossless_and_sums_to_its_list` is the release page's gate.

The mutant *is* caught — by `test_the_view_holds_the_whole_test_corpus`, `test_both_storage_locations_reach_the_view` and `test_routing_moves_the_row_and_never_the_note` (12 failures across the two files). None of those is cited. Citing them would make this criterion the best-evidenced of the four.

**Criterion 4** — the pin is on the wrong basis: the fixture emits `feature`/`regression`/`automated`, both live corpora emit `tier1`/`tier2`/`tier3`, and swapping `tier1` with `tier2` puts Regression above Feature on both repos with the whole suite green (`1968 passed`). Full measurement in [[FEAT-0128]].

**Criterion 2 holds as cited** — `_section_head_label` derives walked / re-check / stale from marks, and `test_the_tracking_line_counts_re_runs_and_stale_ticks_separately` asserts all three on constructed input, including the deliberate `2 of 5 outstanding` where a `rerun` row counts twice.
