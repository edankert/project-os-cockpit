---
type: "[[change]]"
id: CHG-20260821-Three-Silences-Get-A-Voice
review_verdict: approved
review_response: "2026-08-21: the REVIEW-STALE figure of 43 was two errors agreeing. Corrected to the measured 51 at f5ca55b, with the note that the rule could not see CHG-* notes at all. || Second pass 2026-08-21: the corrected 51 reproduces at f5ca55b. No further change to this note. || Third pass 2026-08-21: no change required to this note beyond the corrected figures already carried."
review_response_date: 2026-08-21
review_date: 2026-08-21
reviewed_by: model:claude-opus-5
aliases: ["CHG-20260821-Three-Silences-Get-A-Voice"]
title: "A held-back feature says why, an orphaned surface is reported, and a verdict nobody answered is counted — three states the record could not express"
status: merged
owner: user:edwin
created: 2026-08-21
updated: "2026-08-21"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[FEAT-0142-A-Release-Says-What-Is-In-It]]", "[[TASK-0576-An-Exclusion-Says-Why-And-What-It-Cost]]", "[[ISS-0250-A-Surface-Rename-Silently-Orphans-Its-Checks]]", "[[ISS-0253-A-Verdict-Outlives-The-Work-It-Judged]]", "[[ISS-0252-Two-Sessions-Closing-Out-Collide-In-The-Snapshot]]", "[[ISS-0249-Two-Check-Write-Paths-Reach-No-Front-Door]]", "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]"]
tags: [change, validator, release, review]
---

# Three silences get a voice

Four changes, one shape: **a number, a state or a decision that the record had no way to express, so it was expressed by nothing.**

## 1. An exclusion says why, and the page says what it cost ([[TASK-0576]])

`note_writes.release_contents` gains a **fourth refusal**: a removal with no reason is a 400. The reason lands in `held_back:` on the release note, beside `features:` — one file, one diff — and re-adding the feature retires the entry.

The release page reads `N feature(s) held back · M check(s) no longer gating`, in **one sentence**, with the cost read from `gate.deselection.checks` so the page cannot report a number the gate never computed. An exclusion with no recorded reason draws as *"no reason recorded (hand-edited)"* rather than being filled in.

**Two things were unreachable and are now not.** `Remove` was guarded on `c.kind !== 'derived'` and no third kind was ever emitted, so a feature could be added through the front door and never taken back out through it — `contents.kind` is `chosen` now when a release names its contents. And the held-back set was read with `index.by_id(release_id)`, which is `None` on `~release/next`, so the subtraction never fired on the page a person actually opens.

## 2. `SURFACE-ORPHAN` ([[ISS-0250]])

A check's `area:` naming no surface is now reported by the validator — **one finding per orphaned name, not per check**, guarded on *"this repo has surfaces"*, and warned with a promotion date of `2026-11-18`. **21 distinct names over 34 checks** in this repo at introduction; zero in the other eleven, which hold no `SUR-*` note.

Editing a surface's `title:` moved its coverage to zero and moved nothing else, and the two states rendered identically: a surface nobody has tested and a surface whose 91 checks were orphaned by one em dash retyped as a hyphen both read *"no checks"*.

The reverse direction is **not** reported: a surface no check names is the row [[FEAT-0130]] built the type to produce.

## 3. `review_response:` and `REVIEW-STALE` ([[ISS-0253]])

A new frontmatter field — `review_response:` with `review_response_date:` — where the author records **what was done about the findings**, without touching the verdict. `review_verdict` stays the reviewer's; self-clearing it turns an independent gate into a formality.

`REVIEW-STALE` reports a note at a terminal status carrying an owed verdict with no response. It fires on **51** notes at `f5ca55b`. Warned, promoting `2026-11-18`. **None of the 51 was flipped.**

*(It reported 43 for one commit and [[ISS-0253]] had filed 43, and the agreement was a coincidence of two errors: the issue's count was never re-measured, and the rule read `note_index`, which holds no `CHG-*` note — 8 of the 51 are change notes and every `merged` one is. It walks the files now.)*

It deliberately does **not** trigger on `updated:` later than `review_date:` — [[ISS-0007]] records that heuristic re-arming a gate on any edit, and stamping a verdict *is* an edit, so 85 of 103 verdicts in this corpus have `updated <= review_date`.

The review desk's register rows now read `answered <date>` or `no response recorded`.

## 4. Two smaller ones

**`close-out-commit.sh` names its `SNAPSHOT.yaml` membership changes** ([[ISS-0252]]) — added, removed, and separately **dangling**: an entry whose note is in no commit, which turns `--as-committed` red and does not self-heal. Reported in stderr and in the commit message; never refused.

**`POST /api/notes/retire-check`** ([[ISS-0249]]) — `retire_check` was a complete, tested write path no front door reached. It is routed now, loopback-guarded like the other 27, with a `Retire` control on `~checks`. Wiring it found that it wrote `verdict_reason:`, a field this repo's validator refuses — so it would have failed the commit it was part of, and nothing caught it because nothing called it.

## Behaviour a caller can see

- `POST /api/notes/release-contents` with `action: "remove"` and no `reason` now returns **400**.
- `POST /api/notes/retire-check` exists; the guarded-route count moved 27 → 28.
- Two new validator codes, both warnings until `2026-11-18`: `SURFACE-ORPHAN`, `REVIEW-STALE`.
- `release_payload().contents.kind` can be `"chosen"`, which it never was before; `contents.held_back` and `gate.deselection` are new keys.

## Independent review — 2026-08-21

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `f5ca55b..07602db`; the author's reasoning trace was not available to it. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — same model as the author, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant rather than read.


**Verdict: changes-requested.** Two of the three sections are accurate; the third repeats a number as independent corroboration when it is not.

### Accurate

- *"21 distinct names over 34 checks"* — reproduces exactly. 21 warnings emitted, per-name counts summing to 34, which is every acceptance check in the repo.
- The [[ISS-0252]] section is accurate, and the dangling detection fails when mutated.
- *"None of the 43 was flipped"* — confirmed. `grep` finds no `review_verdict` change on those notes in this diff.

### Finding — *"it fires on exactly 43 notes, which is the number ISS-0253 measured by hand"*

The two numbers are not the same population and neither confirms the other.

`ID_PREFIXES` in `validate-docs.py` has no `CHG`, so `build_note_index` indexes no change note and `REVIEW-STALE` **cannot fire on one**. Measured against `git archive f5ca55b`: **56** owed verdicts, **51** terminal, **8** of them `CHG-*`. 51 − 8 = 43.

[[ISS-0253]]'s hand count was itself 49/43 against an actual 56/51, and its breakdown claims *7 merged* — a class the rule can never report, since every `merged` note here is a `CHG`. An undercount and a structurally-blind rule landing on the same integer is exactly the shape this change set was written to remove.

Correct the sentence, or fix `ID_PREFIXES` and restate the number. Detail on [[ISS-0253]].

## Independent review — second pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `07602db..b635c39` — the first pass's findings and the author's reasoning trace were not available to it, only the seven claims as the notes state them. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]): same model as the author and as the first reviewer, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant.

**This supersedes the first-pass verdict. The `review_response:` above is accurate**: the 43 was two errors agreeing, and 51 is the measured figure. I reproduced both independently against `git worktree add … f5ca55b`, driving the rule's own predicates (`OWED_VERDICTS`, `REVIEW_TERMINAL_STATUSES`, `has_value`) over the tree: **56** notes carry an owed verdict, **51** of them at a terminal status with no `review_response:`, broken down **30 `done` / 8 `merged` / 4 `implemented` / 9 `fixed`** — exactly the corrected claim. Walking `build_note_index` instead of the files over the same tree yields **43**, missing exactly the 8 `CHG-*` notes and nothing else. The file walk drops nothing that the index walk reported, and `__templates__` / `__bases__` are excluded. The claim is right and the fix is right.

**Finding F (low-medium) — three of the four numbers in that sentence were re-measured and the fourth was carried over unchecked, and the refuted figures survive in three other places.** The corrected `PROMOTIONS` comment reads *"**51 findings in this repo** … 30 `done`, 8 `merged`, 4 `implemented`, 9 `fixed`, **dating to 2026-08-02**"*. Measured at `f5ca55b`, the earliest `review_date` among those 51 is **2026-07-30**, on six notes — `CHG-20260730-Two-Features-Closed`, `FEAT-0045`, `ISS-0037`, `ISS-0057`, `ISS-0068`, `ISS-0069`. The date came from the original filing and was the one field the re-measurement did not touch. Separately, the refuted breakdown is still asserted in the present tense at `tools/scripts/validate-docs.py:279` — *"the population it describes is 27 `done`, 7 `merged`, 4 `implemented` and 5 `fixed`"* — and the rule's own header comment still says *"49 notes carry `changes-requested`, 43 of them at a terminal status"* and *"Six of the 49 are that"*. Two sites were corrected and four were not, so the file now states both numbers about one population, twenty lines apart.

## Independent review — third pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `b635c39..c9d6a82`; neither the author's reasoning trace nor either earlier reviewer's working was available to me beyond what these notes themselves record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran both earlier passes, recorded in `reviewed_by` as provenance. Every count below was re-measured from the tree and every guard re-executed against a constructed mutant. **This verdict supersedes the second pass's on this note.**

**Verdict: changes-requested.** This note's own body is accurate: the 51 reproduces, and *"two errors agreeing"* is the right description of the 43 — I confirmed the index walk misses exactly the eight `CHG-*` notes and nothing else. The problem is in the file this note is about.

**Finding 3 (medium) — "Finding F fixed" is not true, and the correction that was written is itself wrong.**

*Two of the four sites F named are untouched.* `tools/scripts/validate-docs.py` lines 2884–2886 (and the byte-identical bundled copy) still read *"Measured 2026-08-20: **49 notes carry `changes-requested`, 43 of them at a terminal status**, dating back to 2026-08-02"*, and line 2935 still reads *"Six of the 49 are that"*. Measured at `f5ca55b` by driving the rule's own predicates over the tree: **56** owed, **51** terminal, therefore **5** non-terminal, earliest `review_date` **2026-07-30**. Every one of those five figures is refuted by the `PROMOTIONS` comment 1,800 lines above in the same file. One file states two populations about one rule, which is the exact condition the second pass reported and the response claims to have removed.

*The new number is wrong.* The corrected comment reads *"the earliest six dated **2026-07-30**"* and its parenthesis reads *"Measured: 2026-07-30, on six notes."* Re-measured twice — once through the rule's own predicates over `git archive f5ca55b`, once independently by `grep` over the archived tree — the answer is **eight**: `CHG-20260730-Two-Features-Closed`, `FEAT-0045`, `ISS-0037`, `ISS-0057`, `ISS-0068`, `ISS-0069`, **`PHASE-011`** and **`PHASE-013`**. The two phase notes are not excludable: drop them and the population totals 49, not the 51 the same sentence gets right. The six is the second pass's figure, adopted verbatim rather than re-measured — a number copied instead of counted, in the correction to a comment about numbers copied instead of counted.

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
**Verdict: approved.** The figures this note carries are the measured ones and they reproduce exactly; see the fourth-pass section on [[ISS-0253]] for the re-measurement and the eight ids. Nothing in `c9d6a82..9a75f11` changes this note's substance.

### The headline question: did fixing round three break anything

**No.** Test functions were extracted by name, file by file, at `f5ca55b`, `c9d6a82` and `9a75f11` and the sets diffed. `c9d6a82..9a75f11` **removes nothing**: three functions are added to `tests/test_observed_coverage.py` and no other file changes its set, 1835 → **1838**. Across the whole phase range `f5ca55b..9a75f11` the only removals anywhere are the seven `covered_by:`/promotion tests in `tests/test_checks_view.py`, each replaced in the same file by one guarding the mechanism's absence — that file's count is unchanged at 22 — so 1761 → 1838 with a net `+77` accounted for entirely by five new files (6 + 31 + 17 + 13 + 10).

**The emitter was run in loops rather than read.** Twelve scenarios against a temporary repo, counting ledger entries: `pass` then four `<skipped/>` runs → **2** entries (one `pass`, one invalidation); three skipped runs with no standing verdict → **0**; `pass`, skip, then three passing runs → **3**; declaration deleted, four runs → **2**; declaration moved to another file under the same name, four runs → **1**; moved *and* renamed, four runs → **1**; a `.kt`-declared check across five `.py` runs → never invalidated; `pass` then five failing runs → **2**; a passing sibling with a skipped sibling, four runs → **2**; a `manual` verdict under four skipped runs → **1** (untouched); a `manual` verdict under four failing runs → **2**. Every one is bounded, and the bound is structural: `resolve()` pops an invalidated check out of `verdicts()`, so both the `stale` and the `failing` branch leave the set by construction on the next run. Round three's finding 1 is genuinely closed.

**The three new tests are not passengers.** Reverting `elif seen and not held` to `elif seen` fails `test_a_skipped_sibling_is_not_laundered_into_a_pass` and nothing else. Restoring the round-two `stale` rule verbatim fails `test_a_skipped_test_invalidates_once_not_once_per_run` and `test_a_check_with_no_verdict_is_never_invalidated`. The two earlier repairs still hold their ground: `_withdrawn` returning `True` unconditionally fails the two toolchain tests, and returning `False` for a vanished declaration fails `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list`.

**Round three's finding 3 reproduces exactly, every figure.** Driving the rule's own predicates over `git archive f5ca55b`: **56** owed, **51** terminal, **5** non-terminal, `30 done / 8 merged / 4 implemented / 9 fixed`, earliest `review_date` **2026-07-30** on **eight** notes — `CHG-20260730-Two-Features-Closed`, `FEAT-0045`, `ISS-0037`, `ISS-0057`, `ISS-0068`, `ISS-0069`, `PHASE-011`, `PHASE-013`. All 8 `merged` findings are `CHG-*`. The rule reports 51 at HEAD.

**Suite, validator, CI step set, all observed rather than reported.** `2063 passed, 3 skipped` in 269s; `validate-docs: OK`; `--as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `9a75f11`.


## Independent review — fifth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `9a75f11..991838e`, widened to `f5ca55b..991838e`; no memory of authoring any of this and no access to the author's reasoning trace. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]). **This supersedes the fourth pass's verdict on this note.**

**Verdict: approved.** Unchanged in `9a75f11..991838e` beyond frontmatter. The three-round `review_response:` chain is accurate and in order, and nothing in the round-four fix touches this note's subject.

**Suite, validator, CI step set — observed.** **2066 passed, 3 skipped** in 269s; `validate-docs: OK`; `--as-committed` reports *"HEAD passes the full CI step set"*. Working tree clean at `991838e`. The phase itself is `changes-requested` at this pass on two findings that do not touch this note — see [[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]].
