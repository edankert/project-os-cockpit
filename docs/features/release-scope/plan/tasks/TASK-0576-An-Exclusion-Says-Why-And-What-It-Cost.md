---
type: "[[task]]"
id: TASK-0576
review_verdict: approved
review_response: "Fifth pass 2026-08-21: this task's fourth criterion was true of the block it added and false of the page it added it to - buildReleaseItemPage rendered markable check rows. Fixed, and the guard is bounded by discovered release surfaces with comments stripped rather than by a character window. || Sixth pass 2026-08-21: F1 and F2 fixed; the ADR-0035 guard is now on the argument rather than on the text, with exactly one legitimate call asserted."
review_response_date: 2026-08-21
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

## Independent review — fourth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `c9d6a82..9a75f11`; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all three earlier passes, recorded in `reviewed_by` as provenance rather than as a compliance token. Every count below was re-measured from the tree and every claim about behaviour was established by running the code, not by reading it. **This verdict supersedes the third pass's on this note.**
**Verdict: approved on what it built**, with one scoping note that belongs on [[PHASE-037]] rather than here. The held-back block draws rows and reasons, offers no verdict control, and the page reads the cost rather than a smaller number alone. The scoping note: `test_no_write_path_to_a_check_appears_on_the_release_page` scans a fixed **2600-character** slice from `const heldBack = c.held_back`, and `renderer.ts` runs 469,293 characters past that anchor — a write control inserted at anchor+2621 passes. That is right for a guard *over this block* and is why PHASE-037's criterion 1, which states the universal, is filed there as written wider than its guard. This task's own scope is guarded.

### The headline question: did fixing round three break anything

**No.** Test functions were extracted by name, file by file, at `f5ca55b`, `c9d6a82` and `9a75f11` and the sets diffed. `c9d6a82..9a75f11` **removes nothing**: three functions are added to `tests/test_observed_coverage.py` and no other file changes its set, 1835 → **1838**. Across the whole phase range `f5ca55b..9a75f11` the only removals anywhere are the seven `covered_by:`/promotion tests in `tests/test_checks_view.py`, each replaced in the same file by one guarding the mechanism's absence — that file's count is unchanged at 22 — so 1761 → 1838 with a net `+77` accounted for entirely by five new files (6 + 31 + 17 + 13 + 10).

**The emitter was run in loops rather than read.** Twelve scenarios against a temporary repo, counting ledger entries: `pass` then four `<skipped/>` runs → **2** entries (one `pass`, one invalidation); three skipped runs with no standing verdict → **0**; `pass`, skip, then three passing runs → **3**; declaration deleted, four runs → **2**; declaration moved to another file under the same name, four runs → **1**; moved *and* renamed, four runs → **1**; a `.kt`-declared check across five `.py` runs → never invalidated; `pass` then five failing runs → **2**; a passing sibling with a skipped sibling, four runs → **2**; a `manual` verdict under four skipped runs → **1** (untouched); a `manual` verdict under four failing runs → **2**. Every one is bounded, and the bound is structural: `resolve()` pops an invalidated check out of `verdicts()`, so both the `stale` and the `failing` branch leave the set by construction on the next run. Round three's finding 1 is genuinely closed.

**The three new tests are not passengers.** Reverting `elif seen and not held` to `elif seen` fails `test_a_skipped_sibling_is_not_laundered_into_a_pass` and nothing else. Restoring the round-two `stale` rule verbatim fails `test_a_skipped_test_invalidates_once_not_once_per_run` and `test_a_check_with_no_verdict_is_never_invalidated`. The two earlier repairs still hold their ground: `_withdrawn` returning `True` unconditionally fails the two toolchain tests, and returning `False` for a vanished declaration fails `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list`.

**Round three's finding 3 reproduces exactly, every figure.** Driving the rule's own predicates over `git archive f5ca55b`: **56** owed, **51** terminal, **5** non-terminal, `30 done / 8 merged / 4 implemented / 9 fixed`, earliest `review_date` **2026-07-30** on **eight** notes — `CHG-20260730-Two-Features-Closed`, `FEAT-0045`, `ISS-0037`, `ISS-0057`, `ISS-0068`, `ISS-0069`, `PHASE-011`, `PHASE-013`. All 8 `merged` findings are `CHG-*`. The rule reports 51 at HEAD.

**Suite, validator, CI step set, all observed rather than reported.** `2063 passed, 3 skipped` in 269s; `validate-docs: OK`; `--as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `9a75f11`.


## Independent review — fifth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `9a75f11..991838e`, widened to `f5ca55b..991838e` for the did-anything-break question; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all four earlier passes, and `reviewed_by` records that as provenance rather than as a compliance token. **This supersedes the fourth pass's verdict on this note.**

**Verdict: changes-requested — on the universal sentence, not on what was built.** The held-back block itself is right and I checked it rather than read it: it draws the count and its cost in one line, every row carries its reason, an exclusion with no reason renders *"no reason recorded (hand-edited)"* instead of inventing one, and the block offers no verdict control. The criterion written above it is what fails.

### Finding 1 (high) — "no write path to a check appears on the release page" is false at `991838e`

`renderer.ts:7610`, inside `buildReleaseItemPage`, renders every acceptance-check row of `~release/<id>/<ITEM-ID>` with `s.appendChild(buildCheckRow(item))` and no `manual` argument — so `manual` defaults to `true` and each row gets a `checkMark(item)` button (click → `markCheckRow` → `walkOneCheck` → `askForMark` → `postJson('/api/notes/mark-check', …)`) **and** a `Retire` button (→ `retireCheckRow`). Both change a check. The page is routed at `renderer.ts:1249` off `~release/`, renders in `publication` nav mode, and its rows are real `GateItem`s from `publication.release_item_payload`. The code says it in its own voice at `renderer.ts:7608` — *"The mark control INLINE — the same one the view and the gate wear"* — while `retireCheckRow`'s docstring says the control *"lives on `~checks`, never on a release page ([[ADR-0035]])"*.

**Why the widened guard misses it, established by mutation rather than by reading.** Inserting `void askForMark({});` into each of the eight `subjects` functions fails the test **8/8**. Inserting `wrap.appendChild(buildCheckRow(item));` into the same eight — the exact call the release item page already makes — **passes 8/8**, including into `buildReleasePage`. The guard is one call deep; the live violation is one call deep.

### Finding 2 (medium) — the guard's docstring claims more than the guard does

It says *"The region is every release-page render function"* and *"Named rather than pattern-matched, so renaming one into existence outside this list is a visible edit here."* Constructed: a new `function buildReleaseChecksPanel(items: GateItem[])` calling `askForMark`, inserted before `renderReleasePage` → **17 passed**. `found == subjects` catches only the *disappearance* of one of the eight; a ninth is invisible, and the `^(?:async )?function` scan cannot see an arrow-function surface at all. The functions the release pages delegate row rendering to — `buildCheckRow`, `checkMark`, `gateGroup` — are not in the set, which is the mechanism of Finding 1.

**What is genuinely closed.** The 2600-character window is gone; comments are stripped, so the note recording `markGateRow`'s deletion no longer reads as a write path; the two file-wide `function gateMark` / `function markGateRow` assertions hold; and the anchor really is inside `buildReleasePage`'s region (`covered` is asserted, not assumed). The widening is a real improvement that does not reach the sentence it is cited under.

**Suite, validator, CI step set — observed, not reported.** **2066 passed, 3 skipped** in 269s; `validate-docs: OK` (warnings only); `--as-committed` reports *"HEAD passes the full CI step set"*. Working tree clean at `991838e`.



## Independent review — sixth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `991838e..c4413e3`, widened to `f5ca55b..c4413e3` for the did-anything-break question; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all five earlier passes, and `reviewed_by` records that as provenance rather than as a compliance token. **This supersedes the fifth pass's verdict on this note.**

**Verdict: changes-requested — and the fifth pass's blocker is genuinely fixed.** `~release/<id>/<ITEM-ID>` no longer offers any control that changes a check, and I established that by walking the call graph rather than by trusting the guard: `buildCheckRow` has exactly two callers in `renderer.ts` — `paintCheckList` (the `~checks` page, legitimate under [[ADR-0035]]) and `buildReleaseItemPage` (now `manual = false`) — and `checkMark`, `markCheckRow`, `walkOneCheck`, `askForMark` and `retireCheckRow` are reachable only through it. The five other helpers a release surface calls directly (`gateGroup`, `gateLine`, `gateNote`, `buildRecordRow`, `buildRecordCard`) hold no write path. There is no second surface reaching a verdict write through a shared helper. What holds the note is what the repair put in the control's place.

### Finding 1 (medium-high) — the page stopped offering a false control and started making a false statement

`buildCheckRow(item, false)` also takes the **other** branch of every `if (!manual)` in that function: the row gains the class `is-automated`, and the body gains `checks-row-command` with `item.command || 'automated'`. **Every acceptance check in this repo is manual** — 34 of 34 carry no `command:` — so each row on that page now prints the literal word **`automated`** under its description and wears the class whose own CSS comment reads *"An automated check's row ([[ADR-0039]]). It carries the command that executes it INSTEAD OF a checkbox."*

**Constructed, not inferred.** `buildCheckRow` was lifted out of `desktop/dist/renderer/renderer.js` and executed under a DOM shim. The same manual check, both ways: `manual = true` → mark control, `Retire`, no command line; `manual = false` → `<div class="checks-row is-automated">` … `<div class="checks-row-command mono"> "automated"`. Counted against the real corpus: `publication.release_item_payload` built for all **143** features in this repo yields **67** rows across *Checks it originated* / *invalidated* / *in its areas* with no `command:`.

**The flag belongs to the item and this call hard-codes it.** `paintCheckList` derives `manual` from the section it paints — the partition that exists precisely because some checks are machine-executed and some are not. This function has no such partition. The fallback's own comment four lines away says *"the fallback should never fire — a section is non-manual BECAUSE its checks carry a `command:` — so what it prints is a statement about broken data, and it must not be a claim about CI"* ([[ISS-0241]]). It fires on every row of the page now.

This falsifies no ticked criterion: *"no write path to a check appears on the release page"* is about controls and it holds. It is a new instance of the thing this phase exists to remove, written by the commit that closes it.

### Finding 2 (medium) — the widened guard forbids spellings, not the property

`forbidden` names `buildCheckRow(item)`, `buildCheckRow(item,\n` and `buildCheckRow(row)`. Three mutants planted in `buildReleasePage`, each re-arming both the mark dialog and `Retire` on the main release page, and each of which the guard **passes**: `buildCheckRow(item, true)`; `const manual = true; … buildCheckRow(item, manual)`; and `const c = …; buildCheckRow(c)` — **the identical defect to the fifth pass's F1 with one letter changed.** The positive assertion beside it, `assert "buildCheckRow(item, false)" in src`, is scanned over the whole 470,000-character file rather than over the release region, so it stays satisfied by the one legitimate call while a live one sits next to it. The property the rule wants is *no `buildCheckRow` call in a release region whose second argument is not `false`*; what is written is three ways of spelling one call. Two further constructions the guard cannot see, both honestly scoped in its own comment and neither guarded: a release surface whose name omits *release* (`function buildShipmentPage` calling `askForMark` → passes), and an arrow-function surface (`const renderReleaseDrawer = async () => { await askForMark(); }` → passes, because the scan is `^(?:async )?function`).

**What the widening did close, verified by mutant:** reverting to `buildCheckRow(item)` fails it; planting `retireCheckRow(` inside `buildReleaseItemPage` fails it; adding `function buildReleaseChecksPanel` calling `askForMark` fails it on the discovered-set assertion — so appearance is now caught, which is what the fifth pass asked for. Three for three, including the exact regression it was written for.

**Suite, validator, CI step set — observed, not reported.** **2072 passed, 3 skipped** in 272s; `validate-docs: OK`, zero errors and 344 warnings; `--as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `c4413e3`.


## Independent review — seventh pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `c4413e3..9784205`, widened to `f5ca55b..9784205` for the did-anything-break question; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all six earlier passes, and `reviewed_by` records that as provenance rather than as a compliance token. Every figure below was produced by running the code, mutating it, rendering it or counting the tree; none of it by reading a docstring and agreeing with it. **This supersedes the sixth pass's verdict on this note.**

**Verdict: approved.** This task's fourth criterion — no write path to a check on the release page — is now true of the page as well as of the block, and I established it two ways: a transitive scan of every call out of all nine release surfaces finds exactly one route to a check write (`buildReleaseItemPage` → `buildCheckRow`, gated on `manual && controls` with `controls` hard-`false`), and the row was rendered under a DOM shim to confirm the mark button and `Retire` are absent while nothing false is printed in their place. The other criteria hold: a removal with no reason is a 400, the reason lands in `held_back:` beside `features:`, and the page reads `N feature(s) held back · M check(s) no longer gating` from `gate.deselection` rather than from a second count.

**The guard is weaker than its own comment, which is recorded in full on [[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]] and does not change this verdict.** `checkMark(item)` and a button calling `markCheckRow(item)` each typecheck clean inside `buildReleaseItemPage` and leave all 18 tests in this file green; and `buildCheckRow(item, false, false)` passes the argument rule, caught only by a whole-file substring that one comment line disarms.

**Suite, validator, CI step set — observed, not reported.** `.venv/bin/python -m pytest -q` → **2076 passed, 3 skipped** in 271s. `bash tools/scripts/validate-docs.sh` → `validate-docs: OK`, **zero errors** and 344 warnings. `--as-committed` → *"HEAD passes the full CI step set"*: validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `9784205`.
