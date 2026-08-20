---
type: "[[requirement]]"
id: REQ-0059
aliases: ["REQ-0059"]
title: "A check's section is derived from what it covers and who executes it, never filed"
status: implemented
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: ["[[ADR-0039-Three-Sections-Derived-Not-Filed]]"]
priority: high
scope: "Every acceptance check in every front door — 671 notes fleet-wide."
acceptance: ["One predicate returns the section, called by every front door", "No section and no gate decision reads `tier:`, and the tier constants are deleted", "A check gaining or losing a `command:` moves section with no other edit", "Exactly one section per check, and no id rendered twice"]
implements: "[[FEAT-0140-Sections-Are-Derived-Not-Filed]]"
verifies: []
related: ["[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[ISS-0208-Retire-The-Tier-Rule]]"]
tests: []
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
---

# A section is derived, never filed

## Statement

The section a check appears under **must** be computed: `command:` non-empty is *Automated tests*; otherwise `covers:` naming an `ISS-*` is *Regression tests*; otherwise *Feature tests*. No note field selects a section, and **no section or gate decision may read `tier:`**.

*(Corrected 2026-08-20 after a third independent review. This said `tier:` must not be read at all, and was marked `implemented` over four live readers — `sort_items` and `_delta_key` among them. The rule is about what DECIDES a section, which is what the implementation actually delivers; ordering and delta identity are [[ISS-0240]]'s subject.)*

## Acceptance Criteria

- [x] One predicate — `acceptance.section_of`, called by the payload, the navigator and the gate
- [~] **Narrowed after review.** `GATING_TIERS`, `PERMANENT_TIERS` and `TIER_LABELS` are deleted and every *section* and *gate* decision reads `section_of`. `tier:` is still read by `sort_items`, `_delta_key`, `Suite.tier` (the file-shape parser) and the migration script — see [[ISS-0240]]. The criterion said *"read by no code path"*, which was never true
- [x] A check gaining a `command:` moves section with no other edit — `tests/test_command_targets.py` proves the return trip on constructed input, since **zero** of the fleet's 139 commands are broken
- [x] Exactly one section per check — `test_the_tiers_render_in_the_tests_view` now asserts no id appears twice **anywhere**, which is strictly stronger than the rule it replaced, and it caught a real duplicate row while being written

## Notes

Precedence matters and is stated deliberately: `command:` wins over `covers:`, so an automated regression check is *Automated tests* — Edwin, *"it doesn't matter why they were automated"*.

## Independent review 2026-08-20 — `changes-requested`

Reviewed by `model:claude-opus-5` from the notes and the diff alone, in a session that never saw the authoring reasoning.

`section_of`'s fail-safe direction holds under mutation — flipping the unclassifiable default to `automated` fails 26 tests, and flipping the file shape's Tier 3 to `feature` fails 15 including `test_tier_three_never_gates`. But **`tier:` is still read by three code paths** on note-shape items (`sort_items`, `_delta_key`, `migrate-acceptance-checks._gated`), so this requirement's acceptance is not fully met, and the deferred strip-`tier:` migration would move 74 rows and change 232 delta keys in `your-trainer`. And the derivation's most consequential effect — six unattributed Tier 3 checks entering `your-trainer`'s release gate at its committed HEAD — was neither measured nor reported. Findings 2, 3 and 4 in [[CHG-20260820-The-Suite-Is-The-Verdict]].

## Second independent review 2026-08-20 — `changes-requested` (verdict stands)

Second pass, `model:claude-opus-5`, fresh context, different session from both the author and the first reviewer.

**A new defect against this requirement was introduced by the review fix.** `missing_issue_refs` was moved off `tier(2)` onto `section_of(i) == SECTION_REGRESSION and not any(r.startswith("ISS-") …)` (`acceptance.py:670-686`). For a note-shape item those clauses are contradictory — `section_of` returns `SECTION_REGRESSION` exactly when a ref matches `^\bISS-\d+`, which implies it starts with `ISS-` — so the method can never return one. Measured on `your-trainer`: **73 → 0**. Replacing the body with `return []` passes the entire suite, and its only consumer, `test_every_tier_two_item_names_the_issue_that_created_it`, can no longer fail. Moving a reader onto the derived section was the right direction; this instance made a live check into a tautology.

**Two further findings.** *"One predicate"* is two readings — `acceptance.section_of` uses `re.match` on normalised refs, `cockpit._covers_an_issue` uses `re.search` on raw frontmatter under a docstring saying they must stay one question; swapping `match` for `search` passes the whole suite. And this note is `status: implemented` with a frontmatter `acceptance:` entry and a Statement both asserting `tier:` is not read, above a review paragraph in the same note saying three paths read it — [[PHASE-039]]'s criterion got a `~`, this one did not.

Detail in [[CHG-20260820-The-Suite-Is-The-Verdict]] sections B and F.

## Third independent review 2026-08-20 — `changes-requested` (verdict stands)

Third pass, `model:claude-opus-5`, fresh context, a different session from the author and from both prior reviewers.

**Both defects the second pass raised against this requirement are fixed, proved by mutation.** `missing_issue_refs` can fire — `return []` fails its guard, and the predicate reports **117** at `your-trainer`'s `HEAD`, **44** in its working tree and **0** here, each equal to `CHECK-SUBJECT` on the same tree. *"One predicate"* is one: `cockpit._covers_an_issue` delegates to `acceptance.section_of`, and restoring its own regex fails `test_the_navigator_and_the_page_classify_a_note_identically`.

**The third finding is untouched, and it is this note itself.** `status: implemented`, frontmatter `acceptance:` still carrying *"`tier:` is read by no code path and the tier constants are deleted"*, criterion 2 still `[x]`, and a Statement still reading *"`tier:` **must not** be read"* — directly above a review paragraph in this same note naming three readers, and beside [[PHASE-039]], whose identical criterion carries a `~`. Two notes describing one fact and disagreeing is the handoff failure this review pass exists to catch; [[ISS-0240]] is the record of the fact, so the correction here is a `~` and a pointer, not new work.

Two smaller ones on the delegation: `fm["level"] = "acceptance"` at `cockpit.py:4038` is inert (`item_from_note` never reads `level:`), and the delegated question is *"is this in the Regression section"* rather than the docstring's *"does this verify a past defect"* — `TST-0017`, `TST-0019` and `TST-0022` here each cover an `ISS-*` and now return `False`, safe only because the caller routes command-bearing records away first. Detail in [[CHG-20260820-The-Suite-Is-The-Verdict]] sections F1 and G1.

## Fourth independent review 2026-08-20 — `changes-requested` (verdict stands)

Fourth pass, `model:claude-opus-5`, fresh context, a different session from the author and from all three prior reviewers.

**The third pass's finding against this note is fixed, and fixed honestly.** The Statement now says *no section or gate decision may read `tier:`*, criterion 2 is `~` with the four live readers named, the frontmatter `acceptance:` entry matches, and the correction states what the old wording claimed and why it was never true. Under mutation the delegation still holds: restoring `_covers_an_issue`'s own regex fails `test_the_navigator_and_the_page_classify_a_note_identically`, and it still fails after the `fm["level"] = "acceptance"` removal — that line is confirmed inert (`item_from_note` reads `id`, `tier`, `mark` and `invalidated_by`, never `level`), so dropping it weakened no guard. `missing_issue_refs` still cannot be emptied: `return []` fails its test.

**No finding against this requirement.** It is `changes-requested` only because the correction did not travel: [[CHG-20260820-The-Suite-Is-The-Verdict]] line 24, under **What changed**, still asserts *"`tier:` is read by no code path"*, and line 51 repeats it. The pair of notes that disagree about one fact is now that note and this one. Detail in section H5 there.
