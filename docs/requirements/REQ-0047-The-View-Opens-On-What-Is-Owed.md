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

- [x] The landing state is not the inventory. — evidence: `test_the_nav_leads_with_what_is_owed`; `needs-you` is index 0 in `_SECTION_ORDER_INDEX`.
- [x] Per-tier walked / re-run / to-walk, derived. — evidence: `test_the_tracking_line_counts_re_runs_and_stale_ticks_separately`; counts come from `_section_head_label`, derived, never stored.
- [x] Every collapsed group expands losslessly. — evidence: `test_the_lines_count_equals_the_rows_it_expands_to`, `test_the_gate_breakdown_is_lossless_and_sums_to_its_list`, and `test_every_test_appears_in_exactly_one_group` (a partition, so collapsing cannot drop or duplicate a row).
- [x] Feature tests lead — **among the three derived sections** (`feature` / `regression` / `automated`), with `needs-you` and `broken-command` ahead of all three. Evidence: `test_the_section_order_is_pinned_and_feature_leads_the_derived_three`. See [[FEAT-0128]] — this was previously ticked against a guard that does not exist.
