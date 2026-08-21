---
type: "[[task]]"
id: TASK-0542
aliases: ["TASK-0542"]
title: "The test declares the check it covers — comment-and-grep for v1, one convention per language"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-21"
reviewed_by: model:claude-opus-5
review_date: 2026-08-21
review_verdict: approved
parent: "[[FEAT-0138-Coverage-Is-Observed-Not-Declared]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# The inversion

## Definition of Done

- [x] A convention exists for declaring the covered check from inside a test, findable by one grep — `# Covers: TST-0044`, and `grep -rn "Covers: TST-" .` finds every one (`test_one_grep_finds_every_declaration`).
- [x] It works in this repo (pytest) and in `your-trainer` (JVM) without a shared library — one comment prefix and one test-declaration pattern per language, `.py`/`.kt`/`.java`/`.swift`, no annotation and no dependency (`test_it_works_in_both_toolchains_without_a_shared_library`).
- [x] A declaration naming a check that does not exist is an error — `coverage-declarations.py --check`, wired into CI as its own job.
- [x] Nothing in any note declares coverage — `covered_by:` is removed from the reader, the writer and the schema; see [[REQ-0057]].

## Notes

**Why the inversion is the structural fix, not a preference.** A standing `covered_by:` on the check rots silently: rename, delete or `@Ignore` the test and the note keeps asserting coverage while the check leaves the run list permanently, with no signal. With the declaration in the test, deleting the test deletes the claim.

`@Covers("TST-0028")` is the shape; the annotation is not required for v1 and a comment is enough. Choosing an annotation first would make this task depend on shipping a library into two toolchains.

## Re-homed 2026-08-20 — the parent moved and this did not

[[FEAT-0138]] was re-homed from [[PHASE-999]] into [[PHASE-037]] on 2026-08-20 (Edwin). **Its tasks stayed behind**, so a task pointed at a parking-lot phase while the feature it delivers pointed at an active one.

That is not cosmetic: `PHASE-CHILDREN` gates a phase on **notes naming it in `phase:`**, so for as long as this task named `PHASE-999` it was invisible to the gate on the phase that actually owns its work — and `PHASE-999` is never closed, so it was invisible to every gate. A child in a parking lot cannot hold anything open.

The phase's own widening note records the same class of miss one level up: *"FEAT-0138 also pointed at PHASE-999 without ever being listed in it, which is why nothing flagged it."*

**The consequence is deliberate.** [[PHASE-037]] now cannot close while this task is unresolved. That is the honest reading of Edwin's re-homing: if the feature belongs to this phase, so does the work that delivers it.

## Independent review — fresh-context pass, 2026-08-20 (`4521a7a`)

Separate session, `model:claude-opus-5`, starting from the notes and the diff with no access to the author's reasoning. Same model family as the author, recorded in `reviewed_by`; the independence claimed here is **context**, not weights ([[project-os-dev#ADR-0013]]).

**Verdict: approved.** The consequence the note claims was constructed and watched rather than reasoned about.

Materialised `HEAD` into a scratch tree, set `PHASE-037` to `done` in **both** the phase note and `SNAPSHOT.yaml` — `effective_status` reads the snapshot, so editing the note alone leaves the rule silent, which is worth knowing before anyone tries to reproduce this — and ran the validator:

```
ERROR [PHASE-CHILDREN] PHASE-037 is 'done' but 14 item(s) still name it as their phase
without a resolved status: … TASK-0542 (backlog), TASK-0543 (backlog); …
```

So the claim holds exactly: both tasks are now inside the gate on the phase that owns their work, and `PHASE-037` cannot close while either is unresolved. `PHASE_RESOLVED["task"]` is `{done, cancelled, superseded}` and `backlog` is not in it; `CLOSED_PHASE_STATUSES` is `("done", "superseded")` and `PHASE-999` is `planned`, so the note's *"a child in a parking lot cannot hold anything open"* is accurate rather than rhetorical.

The `SNAPSHOT.yaml` half was checked separately: both entries carry `phase: "[[PHASE-037-…]]"`, and `sync-snapshot.py` does propagate `status` and not `phase`, so the hand edit was necessary. `TASK-0541` keeping `PHASE-038` is consistent with it being `done`.


## Built 2026-08-21

`tools/scripts/coverage-declarations.py`. `--scan` lists every declaration as `check / test / file:line`; `--check` refuses two things, and both are the same thing: **a declaration that cannot be observed**.

- one naming a check that does not exist, or is not an acceptance check — the emitter would append an entry for it and the gate would read a verdict about nothing;
- one that is **not inside a test** — nothing runs it, so nothing can ever emit or stop emitting for it, which is the whole mechanism.

**The owning test is the nearest test declaration at or above the marker.** That is what makes the association mechanical rather than guessed, and it is why a marker outside a test is refused instead of attributed to whatever happens to be near it.

### It read its own documentation, and that is why it uses a parser

The first cut asked whether the comment prefix appeared before the marker on the line. This file's usage example is a `#` comment **inside a string**, indented under a `def test_...` line that is also inside that string — so the tool reported two coverage claims for a test it had never seen, sourced from its own docstring.

That is the guard-matching-its-own-comment failure this repo keeps paying for. Python is handled by `tokenize` and `ast` now: the tokenizer knows a comment from a string containing one, and the AST knows a function from a line that looks like one. `test_a_declaration_in_a_string_is_not_a_declaration` is the regression guard, and it fails on the old heuristic.

*(A second instance survived the fix: a `#:` comment describing the regex still contained a literal declaration, and `--check` correctly reported the tool reporting itself. The comment was reworded rather than the rule weakened.)*

### What is declared today, and what is not

Three checks, each mapped by reading the check against the test rather than by pattern-matching a name:

| check | declared by | why it is the check |
|---|---|---|
| [[TST-0076]] | `test_every_guarded_endpoint_refuses_a_remote_peer` | the check says *"enumerate the POST dispatch and confirm each handler consults the guard"*; the test drives all 28 from a peer the server believes is remote and requires 403 |
| [[TST-0075]] | `test_changes_requested_is_not_treated_as_finished` | the check is [[ISS-0121]]'s predicate; the test is that predicate |
| [[TST-0069]] | five tests in `test_close_out_commit.py` | one per clause of the check — staged paths, dirty left alone, message from ids, hook run, no push |

**The other 31 are deliberately undeclared.** They are person-facing walks — *open the printed URL, expect the three-pane cockpit* — and inventing a mapping for them would be the assertion this feature exists to remove. An undeclared check stays on the run list, which is the correct and conservative state.

## Independent review — 2026-08-21

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `f5ca55b..07602db`; the author's reasoning trace was not available to it. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — same model as the author, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant rather than read.


**Verdict: approved.** The declaration convention and its scanner hold up.

- `# Covers: TST-####` is findable by one grep, and the scanner uses `tokenize` + `ast` rather than a regex — so a `#` inside a string literal is not a declaration (`test_a_declaration_in_a_string_is_not_a_declaration`), which is the defect the note records catching in its own docstring.
- A declaration outside a test function, and one naming a check that does not exist, are both refused.
- `--check` runs in CI as its own cheap job, correctly separated from the macOS observe job.
- `test_nothing_declares_coverage_in_a_note()` closes the loop from the other side: the convention lives in test source, not in frontmatter.

The findings on this feature are in the emitter ([[TASK-0543]]), not here.

No changes requested.

## Independent review — second pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `07602db..b635c39` — the first pass's findings and the author's reasoning trace were not available to it, only the seven claims as the notes state them. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]): same model as the author and as the first reviewer, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant.

**Approved, confirming the first-pass verdict.** No first-pass finding attached to this note, and this commit added only a review section. The declaration half is untouched by the fix commit; the two emitter findings and the guard finding land on [[TASK-0543]], [[FEAT-0138]], [[REQ-0057]] and [[ISS-0249]] rather than here.

## Independent review — third pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `b635c39..c9d6a82`; neither the author's reasoning trace nor either earlier reviewer's working was available to me beyond what these notes themselves record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran both earlier passes, recorded in `reviewed_by` as provenance. Every count below was re-measured from the tree and every guard re-executed against a constructed mutant. **This verdict supersedes the second pass's on this note.**

**Approved.** Nothing in `b635c39..c9d6a82` touches the declaration scanner, and I found no cause to reopen it. Re-checked rather than assumed: the four-language scan, the `tokenize`/`ast` refusal of a declaration inside a string, and the refusal of one outside a test all still pass, and the alternating-toolchain construction in Finding 1's work exercised a `.py` and a `.kt` declaration side by side in one repo — both were found, by name, and neither leaked into the other's run. The defects this pass records are in `emit-coverage.py`, downstream of this task, and are recorded on [[FEAT-0138]] and [[TASK-0543]].

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
**Verdict: approved.** The declaration convention holds under every construction I could put to it. One grep finds every declaration; the marker must sit inside a test and a marker above one is refused; the four language patterns each attribute to the nearest enclosing test; and the tokenizer/AST path genuinely fixes the scanner-reads-its-own-docstring defect — a `#` comment inside a string literal, indented under a `def test_` that is also inside that string, yields no declaration. Scanning this repo returns 7 declarations over 3 checks, each resolving to a real acceptance note.

The one thing this task's convention does *not* carry, recorded here because it is where it belongs rather than as a change request against this note: the declaration names a **bare test name**, and the emitter consumes it as one. `test_it_does_not_push` is defined in two files in this repo, one of which declares `TST-0069`. That is a property of the consumer and is filed against [[FEAT-0138]] / [[TASK-0543]].

### The headline question: did fixing round three break anything

**No.** Test functions were extracted by name, file by file, at `f5ca55b`, `c9d6a82` and `9a75f11` and the sets diffed. `c9d6a82..9a75f11` **removes nothing**: three functions are added to `tests/test_observed_coverage.py` and no other file changes its set, 1835 → **1838**. Across the whole phase range `f5ca55b..9a75f11` the only removals anywhere are the seven `covered_by:`/promotion tests in `tests/test_checks_view.py`, each replaced in the same file by one guarding the mechanism's absence — that file's count is unchanged at 22 — so 1761 → 1838 with a net `+77` accounted for entirely by five new files (6 + 31 + 17 + 13 + 10).

**The emitter was run in loops rather than read.** Twelve scenarios against a temporary repo, counting ledger entries: `pass` then four `<skipped/>` runs → **2** entries (one `pass`, one invalidation); three skipped runs with no standing verdict → **0**; `pass`, skip, then three passing runs → **3**; declaration deleted, four runs → **2**; declaration moved to another file under the same name, four runs → **1**; moved *and* renamed, four runs → **1**; a `.kt`-declared check across five `.py` runs → never invalidated; `pass` then five failing runs → **2**; a passing sibling with a skipped sibling, four runs → **2**; a `manual` verdict under four skipped runs → **1** (untouched); a `manual` verdict under four failing runs → **2**. Every one is bounded, and the bound is structural: `resolve()` pops an invalidated check out of `verdicts()`, so both the `stale` and the `failing` branch leave the set by construction on the next run. Round three's finding 1 is genuinely closed.

**The three new tests are not passengers.** Reverting `elif seen and not held` to `elif seen` fails `test_a_skipped_sibling_is_not_laundered_into_a_pass` and nothing else. Restoring the round-two `stale` rule verbatim fails `test_a_skipped_test_invalidates_once_not_once_per_run` and `test_a_check_with_no_verdict_is_never_invalidated`. The two earlier repairs still hold their ground: `_withdrawn` returning `True` unconditionally fails the two toolchain tests, and returning `False` for a vanished declaration fails `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list`.

**Round three's finding 3 reproduces exactly, every figure.** Driving the rule's own predicates over `git archive f5ca55b`: **56** owed, **51** terminal, **5** non-terminal, `30 done / 8 merged / 4 implemented / 9 fixed`, earliest `review_date` **2026-07-30** on **eight** notes — `CHG-20260730-Two-Features-Closed`, `FEAT-0045`, `ISS-0037`, `ISS-0057`, `ISS-0068`, `ISS-0069`, `PHASE-011`, `PHASE-013`. All 8 `merged` findings are `CHG-*`. The rule reports 51 at HEAD.

**Suite, validator, CI step set, all observed rather than reported.** `2063 passed, 3 skipped` in 269s; `validate-docs: OK`; `--as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `9a75f11`.


## Independent review — fifth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `9a75f11..991838e`, widened to `f5ca55b..991838e`; no memory of authoring any of this and no access to the author's reasoning trace. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]). **This supersedes the fourth pass's verdict on this note.**

**Verdict: approved.** The declaration convention is unchanged in `9a75f11..991838e` and holds under everything I put to it. Scanning this repo returns **7 declarations over 3 checks** (`TST-0069` ×5, `TST-0075`, `TST-0076`), each resolving to a real acceptance note, and all three still resolve against a real `--junitxml` run of the declaring files. The `tokenize`/`ast` path still refuses a marker that is a `#` inside a string. The bare-name property this task's fourth-pass section correctly parked as *"a property of the consumer"* is now a **basename** property of the consumer, and is filed against [[FEAT-0138]] / [[TASK-0543]] where it belongs, not here.

**Suite, validator, CI step set — observed.** **2066 passed, 3 skipped** in 269s; `validate-docs: OK`; `--as-committed` reports *"HEAD passes the full CI step set"*. Working tree clean at `991838e`. The phase itself is `changes-requested` at this pass on two findings that do not touch this note — see [[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]].



## Independent review — sixth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `991838e..c4413e3`, widened to `f5ca55b..c4413e3` for the did-anything-break question; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all five earlier passes, and `reviewed_by` records that as provenance rather than as a compliance token. **This supersedes the fifth pass's verdict on this note.**

**Verdict: approved.** Unchanged in `991838e..c4413e3` beyond the appended fifth-pass section. The declaration mechanism this task delivered is exercised by the round-five repair rather than altered by it: `coverage-declarations.py` still finds all seven declarations across three checks, and driving the emitter over a real pytest report resolves every one of them through tier 1.

**Suite, validator, CI step set — observed, not reported.** **2072 passed, 3 skipped** in 272s; `validate-docs: OK`, zero errors and 344 warnings; `--as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `c4413e3`.


## Independent review — seventh pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `c4413e3..9784205`, widened to `f5ca55b..9784205` for the did-anything-break question; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all six earlier passes, and `reviewed_by` records that as provenance rather than as a compliance token. Every figure below was produced by running the code, mutating it, rendering it or counting the tree; none of it by reading a docstring and agreeing with it. **This confirms the sixth pass's verdict on this note rather than superseding it** — the sixth pass approved it, and I re-ran its evidence rather than inheriting it.

**Verdict: approved.** Untouched in `c4413e3..9784205`. The declaration convention is exercised by this round rather than altered by it: the two new tier tests drive `_resolve` over declarations this scanner produced, and both mutants they catch are consumer-side. Nothing in the round-six repair reaches this note's subject.

**Suite, validator, CI step set — observed, not reported.** `.venv/bin/python -m pytest -q` → **2076 passed, 3 skipped** in 271s. `bash tools/scripts/validate-docs.sh` → `validate-docs: OK`, **zero errors** and 344 warnings. `--as-committed` → *"HEAD passes the full CI step set"*: validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `9784205`.
