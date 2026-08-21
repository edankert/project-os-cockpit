---
type: "[[task]]"
id: TASK-0576
review_verdict: approved
review_date: 2026-08-21
reviewed_by: model:claude-opus-5
aliases: ["TASK-0576"]
title: "An exclusion says why, and the page says what the selection cost"
status: done
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-20
updated: "2026-08-21"
source: ["[[FEAT-0142-A-Release-Says-What-Is-In-It]]", "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]"]
parent: "[[FEAT-0142-A-Release-Says-What-Is-In-It]]"
effort: S
due: ""
depends: []
blocks: []
related: ["[[ADR-0028-Publication-Is-The-Third-Phase]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]"]
tests: []
---

# An exclusion says why, and the page says what it cost

**The last outstanding criterion of [[FEAT-0142]]** — six of its seven are met, five delivered under [[FEAT-0129]]'s tasks and one ([[FEAT-0142]] c5, `chronic`) found already true and now guarded.

## Definition of Done

- [x] Holding a feature back records a **reason**, stored on the release note beside the selection — `held_back:` in the release note's frontmatter, written by `note_writes.release_contents`, which now **refuses a removal with no reason** (refusal 4, `test_a_removal_with_no_reason_is_refused`)
- [x] The release page reads `N features held back · M checks no longer gating` — `renderer.ts`, the `heldBack` block; `test_the_page_never_shows_a_smaller_number_alone`
- [x] A total that fell **says why it fell** — the count and the cost are one sentence and the cost is read from `gate.deselection.checks`, so the page cannot report a number the gate never computed
- [x] No write path to a check appears on the release page — `test_no_write_path_to_a_check_appears_on_the_release_page`

## Measured before starting, 2026-08-20

`publication.py` already computes the held-back set — from the note's frontmatter, correctly, after a first cut read `held.get("features")` and could never fire. What does **not** exist:

| | state |
|---|---|
| `held_back` count in the payload | absent |
| any `held back` / `no longer gating` string in `renderer.ts` | **absent** — grep returns nothing |
| a `reason` on an exclusion | absent |

So this is additive: the mechanism is built and the **reporting** is not.

## Why the reason matters more than the count

A count that shrinks with no cause beside it is the defect this whole phase exists to remove — [[ISS-0243]] (90% complete over checks with no recorded result), [[ISS-0241]] (89 executed by CI with no observed run). A gate that drops from 59 to 23 because somebody deselected six features, rendered as *"23 blocking"* with nothing beside it, is the same lie in a new place.

[[ADR-0040]] chose subtraction over division partly to avoid emptying `chronic`. This task is the other half of that argument: **subtraction must be visible, not just conservative.**

## Not in scope

- Changing what subtracts. [[ADR-0040]] decided it and `blocking_minus` implements it.
- Anything that writes to a check from the release page.


## Built 2026-08-21

`tests/test_release_held_back.py`, 17 tests. Four mutants were constructed and each failed the test that claims it:

| mutant | caught by |
|---|---|
| the refusal is removed | `test_a_removal_with_no_reason_is_refused` |
| the cost becomes `len(blocking)` — a second count rather than the subtraction | `test_the_cost_is_the_size_of_the_subtraction_not_a_second_count` |
| the selection is read off the caller's argument again | `test_next_reads_the_selection_of_the_release_it_resolved` |
| an unrecorded reason is filled in with a plausible sentence | `test_a_hand_edited_exclusion_says_it_has_no_reason` |

**The second mutant survived the first version of its own test**, and how is worth recording. With two features and two checks, the subtraction (1), the survivors (1) and the cost (1) are all the same integer, so `checks: len(blocking)` passed. A third check was added so no two of the numbers can coincide. *Measured, not reasoned about — the mutant was run before and after.*

### Two defects found while building it, neither of them this task's subject

**`Remove` was unreachable.** The renderer offers it only on `c.kind !== 'derived'` and a test pins that guard — but `publication.py` emitted `derived` for every unshipped release and `frozen` only after the seal, so **no third kind was ever produced**. A feature could be added through the front door and never taken back out through it, and [[FEAT-0142]]'s *"the page distinguishes derived rows from chosen rows"* was unbuilt. `contents.kind` is now `chosen` when the release names its contents, which is the semantic jump the compose warning already announced.

**The subtraction could not fire on `~release/next`.** The held-back set was read with `index.by_id(release_id)`, and `release_id` is the literal `"next"` on the page a person actually opens — so `by_id` returned `None`, `named` came back empty, and nothing was ever held back. Same family as the defect [[TASK-0512]]'s own test records (`held.get("features")`, `None` every time): **a rule that cannot fire, passing every test that does not construct the positive case.** It reads `held["id"]` now, and `test_the_held_back_set_is_read_from_the_note` asserts it.

### What an exclusion with no reason does

It is **reported, not filled in**. The write path refuses a removal without a reason, so an empty one means `features:` was hand-edited — and the row says *"no reason recorded (hand-edited)"* rather than inventing a plausible sentence, which would be the overclaiming this phase spent itself removing.

### The seal keeps them

A shipped release's `held_back:` is part of what it was measured against: a release whose gate was smaller than the repo's must still say what made it smaller. [[ADR-0035]] is unweakened — that is a fact about the release, not a verdict about a check.

## Independent review — 2026-08-21

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `f5ca55b..07602db`; the author's reasoning trace was not available to it. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — same model as the author, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant rather than read.


**Verdict: approved.** Delivered as scoped, and the two mutants that matter both fail.

- The 4th refusal is real and enforced server-side: disabling `if action == "remove" and not reason:` fails `test_a_removal_with_no_reason_is_refused`.
- The cost is the subtraction: replacing `len(unsubtracted) - len(blocking)` with `len(blocking)` fails two tests, because the fixture deliberately uses three checks so that 1, 2 and 3 are distinct integers.
- The renderer draws `${heldBack.length} feature(s) held back · ${cost} check(s) no longer gating` as one sentence, and reads `cost` from `deselection?.checks` rather than recomputing — so the page cannot report a number the gate never produced.
- A hand-edited `features:` list yields a held-back row with `reason: ""` rather than an invented sentence, guarded by `test_a_hand_edited_exclusion_says_it_has_no_reason`. That is the right refusal.

Scope was held: no write path to a check appeared on the release page, and ADR-0040's subtraction decision was not reopened.

No changes requested.

## Independent review — second pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `07602db..b635c39` — the first pass's findings and the author's reasoning trace were not available to it, only the seven claims as the notes state them. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]): same model as the author and as the first reviewer, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant.

**Approved, confirming the first-pass verdict.** No first-pass finding attached to this note; this commit added a review section only. Spot-checked against the code: the held-back block exists end to end — `publication._held_back_rows` (reason recorded, and a missing reason reported rather than hidden), the `held_back` key on the payload, and the `N feature(s) held back · M check(s) no longer gating` line at `renderer.ts:7965`, drawn *whenever anything is held back, including on a shipped release*. Guarded by `tests/test_release_held_back.py` and `tests/test_gate_subtraction.py`.

## Independent review — third pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `b635c39..c9d6a82`; neither the author's reasoning trace nor either earlier reviewer's working was available to me beyond what these notes themselves record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran both earlier passes, recorded in `reviewed_by` as provenance. Every count below was re-measured from the tree and every guard re-executed against a constructed mutant. **This verdict supersedes the second pass's on this note.**

**Approved.** Verified with [[FEAT-0142]] rather than separately: the reason is recorded per exclusion, an exclusion carrying none is drawn as such rather than hidden, the cost is read from `gate.deselection` rather than recounted, and the sentence *"N feature(s) held back · M check(s) no longer gating"* is drawn at `renderer.ts:7965`. Four mutants against the payload and the renderer each fail a named test. Nothing in `b635c39..c9d6a82` changed this task's mechanism.

### What survived refutation

- **Finding A's restoration is verbatim and the tests are not vacuous.** I extracted both functions from `07602db` and from `c9d6a82` and diffed them: byte-identical. `tests/test_checks_view.py` is back to **22** `def test_` functions. Both guards kill mutants: flattening `for (const area of areas)` and deleting `checkPercent(area.items)` each fail `test_the_page_groups_by_surface_and_not_as_one_flat_list`; changing `(done.length / total)` to `(settled.length / total)` fails `test_a_stale_tick_is_not_drawn_as_done`.
- **Nothing else was lost anywhere in `f5ca55b..c9d6a82`.** I parsed every `tests/**/*.py` at all four commits and diffed the `def test_` sets file by file. The only removals in the whole range are the seven `covered_by:`/promotion tests at `07602db`, every one of them a test for the mechanism `REQ-0057` deleted, replaced in the same commit by seven guarding its absence; the two at `b635c39`, restored here. No test file was deleted at any point. Totals 1761 → 1829 → 1830 → **1835**.
- **Finding B's own tests are real.** Restoring the absence rule (`check not in passing and check not in failing`) fails `test_two_runs_covering_different_toolchains_do_not_retract_each_other` and `test_a_run_that_never_reached_the_test_leaves_it_alone`; deleting the skipped branch fails `test_disabling_the_covering_test_does_the_same` and the latter; folding skipped back into absence fails two. I also built the alternating-toolchain loop myself — `TST-0001` by a `.py` test, `TST-0002` by a `.kt` test, one platform, three full cycles — and counted **two** ledger entries, both `pass`, no retraction.
- **Finding C's test is real.** Restoring `and standing.by == args.by` fails `test_a_second_machine_saying_pass_adds_nothing` and nothing else.
- **Finding E's claim is true.** `validate_moved_verdict_fields` returns early unless `docs/releases/ledgers/` exists *and* holds a `*.json`, so the twelve `LEDGER_MOVED_FIELDS` are refused only in a ledger-keeping repo. The enumeration is right at its stated arity: all ten named fields are written by `note_text`, `covered_by` is not, and the twelfth (`merged_from`) is correctly absent from both lists.
- **Finding G is done.** The false closing clause is gone from `ISS-0213`'s `review_response`.
- **Suite, validator, CI step set.** `2060 passed, 3 skipped` (268s), `validate-docs: OK`, and `validate-docs.sh --as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `c9d6a82`.
