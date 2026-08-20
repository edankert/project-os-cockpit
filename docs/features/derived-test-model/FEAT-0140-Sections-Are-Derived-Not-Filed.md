---
type: "[[feature]]"
id: FEAT-0140
aliases: ["FEAT-0140"]
title: "Sections are derived, not filed — what a reader sees follows from `covers:` and `command:`, and `tier:` is read nowhere"
status: done
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: ["[[ADR-0039-Three-Sections-Derived-Not-Filed]]"]
goal: "Feature tests, Regression tests and Automated tests are computed from what a check covers and whether a machine executes it, in both front doors, with no field anybody files into."
requirements: ["[[REQ-0059-A-Section-Is-Derived-Never-Filed]]", "[[REQ-0060-A-One-Time-Check-Names-Its-Issue]]"]
tasks: ["[[TASK-0565-Derive-The-Three-Sections-And-Stop-Reading-Tier]]", "[[TASK-0566-Resolve-A-Command-And-The-Broken-Command-Section]]", "[[TASK-0567-The-Left-Pane-Six-Sections]]", "[[TASK-0568-The-Generated-Page-Follows-The-Sections]]", "[[TASK-0569-Invalidation-Narrows-To-Feature-Tests]]", "[[TASK-0570-The-Authoring-Rule-And-The-Sixty-Eight]]", "[[TASK-0571-Measure-The-Gate-Delta-Per-Repo]]", "[[TASK-0572-No-UI-String-Says-Run-Or-Walk]]"]
release: ""
acceptance: ""
design: "[[DES-0012-Tests-In-Two-Flows]]"
related: ["[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ISS-0208-Retire-The-Tier-Rule]]", "[[ISS-0237-An-Automated-Check-Still-Blocks-The-Manual-Walk]]", "[[ISS-0238-There-Is-Nowhere-To-Put-An-Automated-Check]]"]
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
tags: [feature, testing, cockpit]
---

# Sections are derived, not filed

## Goal

A check reached Tier 3 because a person moved it there, and 67 of the 68 that arrived that way now carry an `area:` naming a heading in a deleted document. Filing is the mechanism that failed. Every section this feature builds is computed, so nothing can be filed wrong and nothing has to be re-filed when it changes.

## Scope

- Three derived sections, one predicate each: `covers:` names a `FEAT-*`, `covers:` names an `ISS-*`, `command:` is non-empty.
- `Broken command` — an automated test whose command no longer resolves. **Zero members today**, so it is proved on constructed input.
- Six sections in the left pane, three on the generated page.
- `tier:` read nowhere; `GATING_TIERS` and `PERMANENT_TIERS` deleted.
- Invalidation narrows to Feature tests.

## Out of Scope

- Removing `tier:` from the 671 notes carrying it. It stops being read; the strip is later and separate.
- Repairing the 67 `area:` values.

## Acceptance

- [ ] Every section is computed; no note field selects one
- [ ] `tier:` appears in no read path, and the two tier constants are gone
- [ ] The gate delta is measured per repo before it lands — `your-trainer` 68 open to 59, this repo and `your-sudoku` unchanged
- [ ] A check whose covering test is deleted appears under `Broken command`, proved on constructed input
- [ ] No UI string contains *run* or *walk*

## Independent review 2026-08-20 — `changes-requested`

Reviewed by `model:claude-opus-5` from the notes and the diff alone, in a session that never saw the authoring reasoning.

Findings 2, 3, 4, 5 and 7 in [[CHG-20260820-The-Suite-Is-The-Verdict]]: the gate delta was measured over uncommitted state in `your-trainer` and moves `62 -> 68` against its committed record; `blocking()`'s comment still describes a tier filter that no longer exists; `tier:` is still read by three paths; the `Needs a run` -> `Needs you` rename is unguarded because the group is empty in this corpus; and `test_the_tiers_render_in_the_tests_view` carries a dead line and a degenerate assertion.

## Second independent review 2026-08-20 — `changes-requested` (verdict stands)

Second pass, `model:claude-opus-5`, fresh context, different session from both the author and the first reviewer. The `Broken command` wiring is now guarded end to end — deleting the routing branch fails three tests — and the vocabulary and parity guards both fail their mutants. Two findings remain: `missing_issue_refs` became a predicate that can never return a note-shape row (`your-trainer` 73 → 0, `return []` passes the whole suite), and all 74 of `your-trainer`'s Tier 3 checks derive to `Feature tests` — a population [[ADR-0039]] describes as *67 automated* and whose Tier 2 counterpart it grandfathered by ID. See [[REQ-0059]] and [[CHG-20260820-The-Suite-Is-The-Verdict]] sections B and E.

## Third independent review 2026-08-20 — `changes-requested` (verdict stands)

Third pass, `model:claude-opus-5`, fresh context, a different session from the author and from both prior reviewers.

**Both of the second pass's findings against this feature are fixed, and I proved each by mutation rather than on report.** `missing_issue_refs` can return a row: `return []` fails `test_every_tier_two_item_names_the_issue_that_created_it`, and measured through the index — the live load path — it reports **117** at `your-trainer`'s `HEAD`, **44** in its working tree and **0** here, each equal to `CHECK-SUBJECT`'s count on the same tree, so *"the validator and this reader agree by construction"* is true rather than hopeful. [[ADR-0039]]'s corrected context table is exact at both bases (working tree 349/164/68 with 89 commands split 17/5/67; `HEAD` 349/158/74 with **0**).

**Three things remain.** The stale-tier sweep missed `blocking()`'s docstring **summary line** — `acceptance.py:599`, still *"Unsettled Tier 1/2 items"* — and the orphaned `#:` block at `cockpit.py:4302-4327`, which still says *"`tier:` itself is untouched — it is still the field, still the grouping"* two lines above *"**Gone with `tier:`** (ADR-0039)"*. [[ISS-0240]]'s title still carries the 74 its body retracts, and says *579* where the body says *580* (579 is right). And `_covers_an_issue`'s delegation, while correct at its one call site, now answers *"is this in the Regression section"* under a docstring asking *"does this verify a past defect"* — `TST-0017`, `TST-0019` and `TST-0022` in this repo each cover an `ISS-*` and now get `False`, safe only because command-bearing records are routed away before the call. Its `fm["level"] = "acceptance"` is inert; `item_from_note` never reads `level:`.

Detail in [[CHG-20260820-The-Suite-Is-The-Verdict]] sections C1, D1 and F1.
