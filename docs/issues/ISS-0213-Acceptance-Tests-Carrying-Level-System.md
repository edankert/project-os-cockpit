---
type: "[[issue]]"
id: ISS-0213
aliases: ["ISS-0213"]
title: "Five acceptance tests in your-trainer carry `level: system`, so they route to a flat group instead of under their tier"
status: deferred
owner: user:edwin
created: 2026-08-18
updated: "2026-08-21"
reviewed_by: model:claude-opus-5
review_date: 2026-08-21
review_verdict: approved
review_response: "2026-08-20 (recorded 2026-08-21): all three second-pass findings were applied in 4628aff - each quarantined section carries its own superseded banner in its first line, `## Applied 2026-08-20` no longer sits under a heading that does not cover it, and the retraction table's items column reads 581 -> 584. The +3 transition was re-simulated rather than copied and reproduces exactly; the absolute numbers no longer do, and that is recorded as a finding rather than corrected."
review_response_date: 2026-08-21
severity: medium
component: docs
phase: "[[PHASE-999-Future]]"
related: ["[[FEAT-0127-Every-Row-In-The-Tests-View-Is-A-Test]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ISS-0212-Retired-Documents-Render-As-Verified-Tests]]"]
---

# Edwin: *"are these really manual tests?"*

Yes — and that is not the interesting half of the answer.

## Measured

The five rows in `your-trainer`'s **Needs a walk**:

| id | `level:` | `command:` | file |
| --- | --- | --- | --- |
| TST-0011 | `system` | none | `tests/TST-0011-AndroidBleHardeningAcceptance.md` |
| TST-0012 | `system` | none | `tests/TST-0012-IosBleHardeningAcceptance.md` |
| TST-0013 | `system` | none | `tests/TST-0013-IosParityAcceptance.md` |
| TST-0015 | `system` | none | `tests/TST-0015-ProSeatSelectionAndHiddenRiders.md` |
| TST-0018 | `system` | none | `tests/TST-0018-EntitlementResolution.md` |

All five are `status: ready` with no `command:`, so under [[ADR-0034]] they are manual: a person runs them. That part of the surface is correct.

**Three of them are named `…Acceptance`.** They are acceptance tests that never got `level: acceptance`, because they predate the migration and live in `docs/tests/` rather than `docs/tests/acceptance/`. `_tests_groups` excludes `level: acceptance` and routes the rest into flat buckets — so the level, not the content, is what decides where a test appears.

## Why this is the phase's shape

The reader sees five acceptance tests in a flat list and 579 in tier sections, with nothing on screen explaining the difference. The answer is a frontmatter field neither list mentions.

**The fix is data, not code** — and that makes it the one item here that needs a judgement per note rather than a rule. `EntitlementResolution` and `ProSeatSelectionAndHiddenRiders` are not obviously acceptance tests just because they are manual and system-level.

## The judgement, made 2026-08-20

Two of the five had already been resolved before this was picked up: **TST-0015** and **TST-0018** now carry `level: acceptance` and `status: active`, and both render under their tier. The issue's table above is that far out of date.

The remaining three, each read rather than pattern-matched on its name:

| id | judgement | why |
|---|---|---|
| **TST-0011** Android BLE hardening | `acceptance` | *"Validate, on a real smart trainer… This is the gate (with TST-0012 for iOS) that closes TASK-0592/0593/0766, ISS-0256/0329, FEAT-0085, REQ-0185 and RISK-0008. Until every Tier-A row here passes, the branch stays unmerged."* A note that holds a branch shut is an acceptance gate by any reading. |
| **TST-0012** iOS BLE hardening | `acceptance` | The iOS half of the same gate, in the same words. |
| **TST-0013** iOS parity acceptance | `acceptance`, **with a caveat below** | *"Manual acceptance coverage for everything the iOS parity push implemented… so Edwin can verify each new rider-facing surface before the iOS release."* Gates a release. |

**The caveat on TST-0013 is worth more than the level.** It carries **107 checkbox rows** in one note (TST-0011 has 18, TST-0012 has 15). Under [[ADR-0030]] one note is one check, so calling it `level: acceptance` labels a 107-check document as a single acceptance check. The level is still right — the alternative is worse, since `system` routes it to a flat group that contradicts its own title — but the shape is the document-suite [[PHASE-035]] migrated away from, and it should eventually become notes. Noted rather than fixed here: that is a migration, not a field edit.

## RETRACTED 2026-08-20 — the measurement below is wrong and the change is reverted

**The relevel was applied and then undone.** Independent review found that the simulation proving *"zero gate impact"* used an instrument **structurally incapable of showing impact**.

`acceptance.load(docs)` was called **without an index**. Every live surface loads **with** one — `server.py`'s `/api/cockpit/acceptance`, and `publication.release_payload` through `gate_payload(index=index)` — and only the indexed loader resolves a `level: acceptance` note that lives outside `docs/tests/acceptance/`. All three of these do. So the before/after figures could not move, and did not, and were reported as evidence that nothing moved.

Re-measured on the same working tree, only the three `level:` lines differing:

| loader | items | blocking |
|---|---|---|
| **without** an index — what was measured | 579 | 57 → 57 |
| **with** an index — what the app uses | **581 → 584** | **59 → 62** |

`newly blocking: ['TST-0011', 'TST-0012', 'TST-0013']`. **TST-0013 became one blocking check standing over 107 checkbox rows.**

Edwin authorised applying it on the strength of the false claim, so the edit was **reverted** rather than kept and re-argued: 581 items and 59 blocking restored, all three back at `level: system`, the files clean in git.

**Two things in the record were wrong and are named rather than tidied away.** The commit message on `d693f7b` says the write was *"refused by the sandbox"*; it was refused, and then applied thirteen minutes later once Edwin granted access, and the message was never amended. And the earlier version of this section presented the index-less figures as *"simulated on a throwaway copy rather than reasoned about"* — the care was real and it was spent on the wrong instrument, which is the more dangerous shape: a measurement that cannot fail looks exactly like a measurement that passed.

**The judgement about the level is unchanged.** These three are acceptance tests by their own words. What is now known is that acting on it costs three blocking checks — and for TST-0013, one blocking check over 107 rows, which argues for splitting it before relevelling it, not for relevelling it as it stands.

## The original measurement, kept as the record of the error

> **Everything from here to the end of `Applied 2026-08-20` is FALSE and describes a state that no longer exists on disk.** It is kept because the shape of the error is the useful part — a measurement that could not fail, read as one that passed — and deleting it would leave the retraction above arguing with nothing. The present tense below is the present tense it was written in; **"Zero gate impact" is wrong (it is three checks), and "Applied" is wrong (it was reverted).** Re-review 2026-08-20 flagged that quarantining without marking is the same defect one level up.

## Measured before recommending it

> ⛔ **SUPERSEDED AND FALSE.** *"Zero gate impact"* below is wrong — it is **three** checks — and the measurement that produced it could not have detected a change. Retained as the record of the error; see the retraction above. Marked here in its own first line because a heading is a landing target: a reader arriving by link or scroll never sees a banner further up.

Relevelling all three was simulated on a **throwaway copy** of `your-trainer/docs` rather than reasoned about:

```
BEFORE: items=579 blocking=57
AFTER : items=579 blocking=57
newly blocking: []
```

**Zero gate impact.** `acceptance.load` reads the acceptance *directory*, and all three live in `docs/tests/`, so the change moves them in the navigator — out of the flat `Needs you` group and under their tier — and touches nothing the release gate counts. That is exactly the second criterion below and nothing else.

## Applied 2026-08-20

> ⛔ **SUPERSEDED AND FALSE — and this section is not "the original measurement" either**, so it sat under a heading that did not cover it. The edit described below **was reverted**; all three notes are back at `level: system` and clean against `your-trainer` HEAD. *"The prediction held exactly"* is the error restated, and *"left uncommitted pending Edwin's review"* describes a state that no longer exists on disk.

The edit is three lines, `level: system` → `level: acceptance`, in:

- `your-trainer/docs/tests/TST-0011-AndroidBleHardeningAcceptance.md`
- `your-trainer/docs/tests/TST-0012-IosBleHardeningAcceptance.md`
- `your-trainer/docs/tests/TST-0013-IosParityAcceptance.md`

Applied on Edwin's confirmation. **The prediction held exactly**: `579` items and `57` blocking before and after, and all three moved out of the flat `Needs you` group to render as children of their tier — which is the second criterion below, and nothing else moved.

Left **uncommitted in `your-trainer`** pending Edwin's review: a change to that repo's record should be his commit, not a side effect of work in the cockpit.

## Done when

- [x] Each of the five is assigned a `level:` deliberately, with the reasoning recorded.
- [ ] **Decide, on the true cost**, whether TST-0011/0012 are relevelled — three blocking checks enter `your-trainer`'s gate.
- [ ] **TST-0013 is not relevelled as it stands**: 107 checkbox rows behind one blocking check is the document-suite shape [[PHASE-035]] migrated away from. Split first.
- [x] No test's *group* contradicts its own name — verified for TST-0015/0018; the other three keep the contradiction until the above is settled.

## Independent review — second pass, 2026-08-20

**This supersedes the first-pass verdict above. Current verdict: changes-requested.** Same reviewer, same conditions — fresh context, separate session, `model:claude-opus-5` — re-run against the working tree after the first pass's findings were acted on. Every claim below was re-measured or re-executed rather than read.

**The retraction is accurate and the revert is real.** Verified independently: all three notes are back at `level: system` and clean against `your-trainer` HEAD; the suite is 581 items / 59 blocking again. The two-loader table is right, `newly blocking: ['TST-0011','TST-0012','TST-0013']` reproduces, the stale `d693f7b` message is named, the status is back to `open`, and the *"Done when"* now requires splitting `TST-0013` first. Naming the instrument rather than the arithmetic is the correct diagnosis.

**But the note is not free of the claim it retracts.** Beneath `## The original measurement, kept as the record of the error` — a heading with no body — sit two sections in the unqualified present tense:

- `## Measured before recommending it` still asserts **"Zero gate impact."**
- `## Applied 2026-08-20` still asserts *"Applied on Edwin's confirmation. **The prediction held exactly**"* and *"Left uncommitted in `your-trainer` pending Edwin's review"* — describing a state that no longer exists on disk, since the edit was reverted.

Quarantining the error as the record is right; leaving it in the present tense is the *"earlier correction left standing beside a later one"* pattern this phase has now hit repeatedly. `## Applied 2026-08-20` is also not *"the original measurement"*, so it sits under a heading that does not cover it. Mark both sections as superseded in their own first line, or fold the applied/reverted history into the retraction.

Minor: the retraction table's `items` column reads `581` for the indexed row; with an index the items go 581 → **584**. Only the `blocking` transition is shown.


## Re-review findings applied 2026-08-20 — and the numbers no longer reproduce

The second pass's three findings are fixed:

- `## Measured before recommending it` and `## Applied 2026-08-20` now carry **their own** superseded banner in their first line. The collective banner above them was not enough: **a heading is a landing target**, and a reader arriving by link or scroll never sees a warning further up. The second also sat under *"the original measurement"*, which it is not.
- The retraction table's `items` column showed only the starting value where `blocking` showed a transition. Now **581 → 584**, matching.

### The measurement no longer reproduces, and that is a finding rather than a correction

Re-simulated today on a throwaway copy with an **indexed** loader — the instrument whose absence caused this issue:

```
BEFORE items=625 blocking=103
AFTER  items=628 blocking=106      (relevelling the same three notes)
```

**The +3 transition reproduces exactly** — three notes relevelled, three items, three blocking — so the reviewer's finding about the table is right and the fix stands.

**The absolute numbers do not.** The note records 581 / 59; `your-trainer`'s working tree now measures **625 / 103**, a difference of **+44 in both columns**. That tree carries **692 modified files**.

So 581 / 59 was a true measurement of a corpus that no longer exists on that disk, and this note's figures — like [[FEAT-0131]]'s — describe a basis that has moved underneath them. **No attempt is made here to explain the 44**: identical deltas in both columns suggest 44 notes became acceptance-level and all of them block, but that is a hypothesis, and this phase has been burned four times by hypotheses stated as measurements.

Recorded rather than corrected, because writing `625` into the table would replace one basis-less number with another. **What the table needs is a basis, and what the repo needs is a commit** — the same conclusion FEAT-0131 reached from the other end.


## Deferred and re-homed to [[PHASE-999]], 2026-08-21

**The finding was this phase's. The remaining action is not.**

[[PHASE-037]]'s subject is *a surface answering the question its reader did not ask*, and this issue's finding is exactly that: a reader sees five acceptance tests in a flat list and 579 under tiers, with nothing on screen explaining the difference, and the answer is a frontmatter field neither list mentions. That was answered — [[TASK-0506]] and [[TASK-0507]] under [[FEAT-0127]], now `done`.

What is left is **three lines of data in another repo**, and every one of them waits on somebody who is not this phase:

1. **Relevelling `TST-0011`/`TST-0012` costs three blocking checks** in `your-trainer`'s gate. The judgement that they *are* acceptance checks is made and recorded above. Whether to pay that is Edwin's, on his repo.
2. **`TST-0013` must be split before it is relevelled** — 107 checkbox rows behind one blocking check is the document-suite shape [[PHASE-035]] migrated away from. That is a migration, not a field edit.
3. **The numbers in this note no longer reproduce and the repo is not committed.** 581/59 was a true measurement of a corpus that no longer exists on that disk; the working tree measures 625/103 against 692 modified files, and `git log --all -- 'docs/surfaces/*'` returns nothing there. *"What the table needs is a basis and what the repo needs is a commit"* — and the commit is not this repo's to make.

`deferred` alone would not resolve it: STATUSES.md is explicit that a deferred child does not clear its phase, and that the relationship rather than the status word must record where the work went. So `phase:` moves to [[PHASE-999]] and the issue is parked there with its judgement intact.

**Nothing here is closed over.** The reasoning table stands, the retraction stands, and the three notes remain at `level: system` in `your-trainer`, clean against its HEAD.

## Independent review — 2026-08-21

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `f5ca55b..07602db`; the author's reasoning trace was not available to it. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — same model as the author, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant rather than read.


**Verdict: approved** — for the deferral and re-homing specifically. This is not a phase closing over unfinished work.

**The mechanism is the documented one.** `STATUSES.md:51` is explicit that `deferred` does **not** resolve an item's place in its parent's scope, and this note does not rely on the status word alone: `phase:` moves to `[[PHASE-999-Future]]`, which is what actually clears `PHASE-CHILDREN` — the same field-over-list principle [[PHASE-037]] establishes elsewhere. The issue was also removed from PHASE-037's `issues:` list, so the hand-curated index and the load-bearing field agree.

**The remaining work is genuinely not this phase's.** Verified rather than accepted: the finding — a reader shown five acceptance tests in a flat list with nothing explaining the difference — was answered by [[FEAT-0127]], and criterion 3 of PHASE-037 now holds under construction (an acceptance check outside `docs/tests/acceptance/` routes by `level:`). What is left is three notes' `level:` in `your-trainer`, costing three blocking checks, plus a 107-row document that must be split before it can be relevelled. That is another repo's data and Edwin's call on his own gate.

**The retraction is honest.** The note records that its own 581/59 no longer reproduces and declines to write 625/103 in its place, on the grounds that this would replace one basis-less number with another. That is the right instinct, and it is the one [[PHASE-037]]'s own closing count did not follow.

One observation, not a change request: this note still carries `review_verdict: changes-requested` from 2026-08-20 with no `review_response:`, although `4628aff` applied those findings. It is the clearest available exemplar for the field [[ISS-0253]] introduced, and it is not excluded by that issue's "do not flip the 43" scope, since recording a response is not flipping a verdict. `deferred` is not in `REVIEW_TERMINAL_STATUSES`, so `REVIEW-STALE` will not prompt for it.

## Independent review — second pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `07602db..b635c39` — the first pass's findings and the author's reasoning trace were not available to it, only the seven claims as the notes state them. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]): same model as the author and as the first reviewer, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant.

**Approved. The `review_response:` above is accurate in every factual claim**, checked against `4628aff` rather than against the sentence: that commit does add a superseded banner to the **first line of each** of the two quarantined sections (`## Measured before recommending it`, `## Applied 2026-08-20`), it does record that one of them sat under a heading that did not cover it, and it does change the retraction table's `items` column from `581` to `581 → 584`, matching the transition the `blocking` column already showed. The re-simulation and the refusal to write `625 / 103` into the table in place of a basis-less `581 / 59` are both recorded as findings rather than papered over.

**One residual, and it is the field's own failure mode.** The response ends *"A re-review is owed and the verdict is the reviewer's to change"*, while the frontmatter three lines above carries `review_verdict: approved` dated `2026-08-21` — written in the same commit. As the designated exemplar for a field introduced to stop verdicts going stale, it shipped carrying a sentence that was false at the moment it was committed. This pass discharges the sentence rather than contradicting it: the re-review it asks for is this one, and the verdict stands at `approved`. The closing clause should go.

## Independent review — third pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `b635c39..c9d6a82`; neither the author's reasoning trace nor either earlier reviewer's working was available to me beyond what these notes themselves record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran both earlier passes, recorded in `reviewed_by` as provenance. Every count below was re-measured from the tree and every guard re-executed against a constructed mutant. **This verdict supersedes the second pass's on this note.**

**Approved.** Finding G is fixed: the clause *"A re-review is owed and the verdict is the reviewer's to change"* — false at the moment it was committed, three lines under an `approved` verdict written in the same commit — is gone, and the rest of the `review_response:` is unchanged and still accurate. Nothing else in `b635c39..c9d6a82` touches this note or the repo it describes, and the deferral to [[PHASE-999]] is recorded on [[PHASE-037]] under *"What is deliberately not closed"*.

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
**Verdict: approved.** The two quarantined sections each carry a superseded banner in their own first line, which is the rule this note established and the one I applied against `docs/references/TESTING-MODEL.md` elsewhere in this pass. The retraction table shows a transition rather than a starting value in both columns. The note records that its absolute figures no longer reproduce and declines to overwrite them with a second unbased number — which is the correct disposal, and the same conclusion FEAT-0131 reached from the other direction. `deferred` under [[PHASE-999]] is right: what remains is data in a repo whose surfaces are in no commit.

### The headline question: did fixing round three break anything

**No.** Test functions were extracted by name, file by file, at `f5ca55b`, `c9d6a82` and `9a75f11` and the sets diffed. `c9d6a82..9a75f11` **removes nothing**: three functions are added to `tests/test_observed_coverage.py` and no other file changes its set, 1835 → **1838**. Across the whole phase range `f5ca55b..9a75f11` the only removals anywhere are the seven `covered_by:`/promotion tests in `tests/test_checks_view.py`, each replaced in the same file by one guarding the mechanism's absence — that file's count is unchanged at 22 — so 1761 → 1838 with a net `+77` accounted for entirely by five new files (6 + 31 + 17 + 13 + 10).

**The emitter was run in loops rather than read.** Twelve scenarios against a temporary repo, counting ledger entries: `pass` then four `<skipped/>` runs → **2** entries (one `pass`, one invalidation); three skipped runs with no standing verdict → **0**; `pass`, skip, then three passing runs → **3**; declaration deleted, four runs → **2**; declaration moved to another file under the same name, four runs → **1**; moved *and* renamed, four runs → **1**; a `.kt`-declared check across five `.py` runs → never invalidated; `pass` then five failing runs → **2**; a passing sibling with a skipped sibling, four runs → **2**; a `manual` verdict under four skipped runs → **1** (untouched); a `manual` verdict under four failing runs → **2**. Every one is bounded, and the bound is structural: `resolve()` pops an invalidated check out of `verdicts()`, so both the `stale` and the `failing` branch leave the set by construction on the next run. Round three's finding 1 is genuinely closed.

**The three new tests are not passengers.** Reverting `elif seen and not held` to `elif seen` fails `test_a_skipped_sibling_is_not_laundered_into_a_pass` and nothing else. Restoring the round-two `stale` rule verbatim fails `test_a_skipped_test_invalidates_once_not_once_per_run` and `test_a_check_with_no_verdict_is_never_invalidated`. The two earlier repairs still hold their ground: `_withdrawn` returning `True` unconditionally fails the two toolchain tests, and returning `False` for a vanished declaration fails `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list`.

**Round three's finding 3 reproduces exactly, every figure.** Driving the rule's own predicates over `git archive f5ca55b`: **56** owed, **51** terminal, **5** non-terminal, `30 done / 8 merged / 4 implemented / 9 fixed`, earliest `review_date` **2026-07-30** on **eight** notes — `CHG-20260730-Two-Features-Closed`, `FEAT-0045`, `ISS-0037`, `ISS-0057`, `ISS-0068`, `ISS-0069`, `PHASE-011`, `PHASE-013`. All 8 `merged` findings are `CHG-*`. The rule reports 51 at HEAD.

**Suite, validator, CI step set, all observed rather than reported.** `2063 passed, 3 skipped` in 269s; `validate-docs: OK`; `--as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `9a75f11`.


## Independent review — fifth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `9a75f11..991838e`, widened to `f5ca55b..991838e`; no memory of authoring any of this and no access to the author's reasoning trace. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]). **This supersedes the fourth pass's verdict on this note.**

**Verdict: approved.** Unchanged in `9a75f11..991838e` beyond frontmatter; nothing in the round-four fix touches it.

**Suite, validator, CI step set — observed.** **2066 passed, 3 skipped** in 269s; `validate-docs: OK`; `--as-committed` reports *"HEAD passes the full CI step set"*. Working tree clean at `991838e`. The phase itself is `changes-requested` at this pass on two findings that do not touch this note — see [[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]].



## Independent review — sixth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `991838e..c4413e3`, widened to `f5ca55b..c4413e3` for the did-anything-break question; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all five earlier passes, and `reviewed_by` records that as provenance rather than as a compliance token. **This supersedes the fifth pass's verdict on this note.**

**Verdict: approved.** Unchanged in `991838e..c4413e3` beyond the appended fifth-pass section, and nothing in the round-five repair touches this note's subject. Its `review_response:` chain is accurate and in order.

**Suite, validator, CI step set — observed, not reported.** **2072 passed, 3 skipped** in 272s; `validate-docs: OK`, zero errors and 344 warnings; `--as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `c4413e3`.


## Independent review — seventh pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `c4413e3..9784205`, widened to `f5ca55b..9784205` for the did-anything-break question; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all six earlier passes, and `reviewed_by` records that as provenance rather than as a compliance token. Every figure below was produced by running the code, mutating it, rendering it or counting the tree; none of it by reading a docstring and agreeing with it. **This confirms the sixth pass's verdict on this note rather than superseding it** — the sixth pass approved it, and I re-ran its evidence rather than inheriting it.

**Verdict: approved.** Untouched in `c4413e3..9784205` beyond the appended sixth-pass section. It remains `deferred` under [[PHASE-999]] for the reason the phase note records — the remaining action is data in another repo, on Edwin's call — and nothing in the round-six repair reaches it.

**Suite, validator, CI step set — observed, not reported.** `.venv/bin/python -m pytest -q` → **2076 passed, 3 skipped** in 271s. `bash tools/scripts/validate-docs.sh` → `validate-docs: OK`, **zero errors** and 344 warnings. `--as-committed` → *"HEAD passes the full CI step set"*: validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `9784205`.
