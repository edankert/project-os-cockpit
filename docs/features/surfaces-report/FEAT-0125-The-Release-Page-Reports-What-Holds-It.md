---
type: "[[feature]]"
id: FEAT-0125
aliases: ["FEAT-0125"]
title: "The release page reports what holds the release, and offers no control that changes a check"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
requirements: ["[[REQ-0044-A-Release-Page-Records-Nothing]]"]
tasks: ["[[TASK-0502-Delete-The-Actionable-Mark-On-Release-Rows]]", "[[TASK-0503-The-Gate-Band-Becomes-A-Breakdown]]", "[[TASK-0504-The-Release-Shows-Its-Open-Tests]]"]
issues: ["[[ISS-0210-The-Release-Page-Offers-Sixty-Live-Marks]]"]
related: ["[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]"]
tags: [feature]
---

# What holds this release

Three changes to one page, from [[ADR-0035]] and [[ISS-0210]].

**The control goes.** `gateMark`'s `actionable` parameter is deleted rather than set false everywhere — a parameter with one value is a decision waiting to be re-litigated by the next caller. The `quiet` and `stale` groups already render the token as a plain `<span>`; every group now does.

**The wall becomes a breakdown.** Sixty rows sorted by nothing but "blocks" is an inventory, not an answer. The page keeps its verdict line and its confidence roll-up, and replaces the list with counts per area or feature, each a link into `~checks` pre-filtered.

**The page gains what Edwin asked for**: the open `TST-*` rows for the features in the release. `blocking_for(subjects)` already scopes to a feature set — the production caller landed in [[PHASE-036]] — so the data path exists.

## Acceptance

- [x] No release-page row can write a check. — `test_the_release_page_has_no_write_path_for_a_check` ([[ADR-0035]]).
- [x] The blocking wall is **led** by a breakdown whose parts link to a filtered `~checks`. — `test_the_gate_breakdown_is_lossless_and_sums_to_its_list`, `test_the_breakdown_chip_opens_rows_that_exist`. *(**"Replaced by" overstated it and is corrected here.** The breakdown is *prepended*; the rows survive, up to 40 of them, and the cited test asserts precisely that they do. [[TASK-0503]] words it correctly. Keeping the rows is right — the breakdown is a summary and losing the detail behind it would be the wall's opposite failure — but the criterion claimed a removal that never happened, and a reader checking it against the screen would have found the wall still there.)*
- [x] Open tests for the release's contents are shown. — `publication._open_tests_for_contents`, filtered on `item.settled`; asserted in `tests/test_release_page.py` on both the payload and the renderer.

## Independent review — fifth pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`. **What was independent: the context** — this pass started from the notes and the diff at `c9c9563` and never saw the author's reasoning. **What was not: the model** — same family as the author, recorded in `reviewed_by` as provenance (ADR-0013). Verdict: **changes-requested**. Every claim below was executed or measured, not read.

**Criterion 2 claims a replacement that was deliberately not built, and its own guard asserts the opposite.**

The criterion reads *"The blocking wall is **replaced by** a breakdown"*, and the section above says the page *"replaces the list with counts per area or feature"*. It does not. `gateGroup` appends `gateAreaBreakdown(items)` and then a `<ul class="scoped-rowlist gate-rowlist">` of up to 40 rows with a `…N more` line — the source comment beside it reads *"IN FRONT of the rows, never instead of them"*, and the cited test asserts exactly that: *"the list itself is still rendered: the tally goes in FRONT of it"*, with `gateAreaBreakdown(items)` required to appear **before** `gate-rowlist`. [[TASK-0503]], the task that built it, states it correctly — *"renders in front of the blocking list — never instead of it"*. Only this note and [[REQ-0044]] say replaced. The word, not the work, is what needs changing.

**Criteria 1 and 3 hold, and I proved the guards fire rather than taking them.** Two mutants, both caught: putting `createElement('button')` with `className = 'acc-mark'` on an open-tests row fails `test_the_release_shows_the_tests_owed_for_its_own_contents`; making `walkOneCheck` reachable from `buildGateSection` fails `test_the_release_page_has_no_write_path_for_a_check`. `publication._open_tests_for_contents` exists, filters on `item.settled`, and is asserted on both payload and renderer.

**Bookkeeping:** [[TASK-0503]] is `status: done` carrying `review_verdict: changes-requested` with no later review section, under a feature that has now closed. Its findings *were* fixed — I checked all three: the unconditional-accumulation assertion is in the test, the JSDoc above `GATE_BREAKDOWN_MIN` is now a comment about the constant, and the `.gate-breakdown` CSS comment is the right one with its basis caveat. The verdict field is simply stale, which is the one place a reader looks to find out whether a review closed.
