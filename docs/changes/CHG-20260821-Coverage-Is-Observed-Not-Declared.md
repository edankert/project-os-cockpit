---
type: "[[change]]"
id: CHG-20260821-Coverage-Is-Observed-Not-Declared
review_verdict: approved
review_response: "2026-08-21: the impact list was short by two files (TAXONOMY.md, migrate-acceptance-checks.py) and both are now corrected and listed; the emitter's `--by` filter is removed. || Second pass 2026-08-21: finding D fixed - the impact table stated the retired scoping and was appended to rather than corrected. It now has five rows, including the one the whole feature turns on: a declaring test simply absent from a run's report changes nothing. || Third pass 2026-08-21: finding 4 fixed - the impact list said 'two files stranded' and the set was not closed; it is four, and the migrate script's recorded reason was itself wrong. The emitter's event table gains the skipped-sibling case. || Fourth pass 2026-08-21: the stranded-file list was still short - TESTING-MODEL.md's implemented-today section. Corrected there rather than by widening this list again. || Fifth pass 2026-08-21: the resolution rule is three tiers and the impact list gains nothing - TESTING-MODEL.md's remaining sections were corrected in place rather than by widening this list a third time."
review_response_date: 2026-08-21
review_date: 2026-08-21
reviewed_by: model:claude-opus-5
aliases: ["CHG-20260821-Coverage-Is-Observed-Not-Declared"]
title: "A test declares the check it covers and the run emits the verdict — `covered_by:` and `cover_check` are removed, and deleting a covering test puts its check back on the run list"
status: merged
owner: user:edwin
created: 2026-08-21
updated: "2026-08-21"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[FEAT-0138-Coverage-Is-Observed-Not-Declared]]", "[[REQ-0057-Coverage-Is-Observed-From-A-Run]]", "[[REQ-0039-A-Covering-Test-Settles-The-Check]]", "[[TASK-0542-The-Test-Declares-The-Check]]", "[[TASK-0543-The-CI-Emitter-Writes-Into-The-Working-Ledger]]", "[[ISS-0249-Two-Check-Write-Paths-Reach-No-Front-Door]]", "[[ISS-0198-Automation-And-Covered-By-Are-Empty-On-All-669-Checks]]", "[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]", "[[ADR-0037-A-Verdict-Is-An-Event]]"]
tags: [change, acceptance, ledger]
---

# Coverage is observed, not declared

## What changed

**A test declares the check it covers, in its own source.**

```python
def test_every_guarded_endpoint_refuses_a_remote_peer(remote_server):
    # Covers: TST-0076
```

One comment prefix per language (`.py`, `.kt`, `.java`, `.swift`), findable by `grep -rn "Covers: TST-" .`, and no annotation library in either toolchain.

**A run emits the verdict.** `tools/scripts/emit-coverage.py` reads the run's **JUnit XML** — pytest writes it with `--junitxml`, gradle writes it natively — and appends to the working ledger for its platform:

| what the run saw | what it appends |
|---|---|
| every declaring test passed | `mark: pass`, `method: automated`, `by:` naming the tests |
| a declaring test **failed** | an **invalidation** — of whatever verdict was standing, because the run observed the behaviour break |
| a declaring test **ran and was skipped** (`@Ignore`) | an **invalidation** of a `method: automated` verdict |
| a machine-covered check that **no test declares any more** | an **invalidation** of a `method: automated` verdict |
| a declaring test simply **not in this run's report** | **nothing** — a partial run is not evidence of absence |

*(The first version of this table said *"a check this emitter covered, not observed at all"*, and it was wrong twice over. It scoped the retraction to the emitter's own `by:` — so renaming the CI job stranded every prior verdict — and once that scoping was removed it made absence-in-this-run the trigger, so a `.py` run and a `.kt` run on one platform **retracted each other on every cycle**. Both found by independent review; the rule is now *"is the declaration gone"*, which is what the criterion was always about.)*

**`covered_by:` is gone**, from `acceptance.Item`, from `Item.settled`, from the loader, and from `note_writes` — `cover_check` is deleted. [[REQ-0039]] is `superseded` by [[REQ-0057]].

**New:** `tools/scripts/coverage-declarations.py` (`--scan` / `--check`) and `.github/workflows/observed-coverage.yml`.

**Four files were stranded by the removal and are corrected.** *(Two were found by the first review pass and this list said "two"; a third pass swept `src/` and found two more, so the closed set was not closed.)*

- `tools/instructions/TAXONOMY.md` still stated *"a `passing` test named in another's `covered_by:` settles it"* — false the moment `_resolve_coverage` was deleted. It is template-owned, so the correction is owed upstream and is made here because a reference describing a removed mechanism is worse than a sync divergence.
- `tools/scripts/migrate-acceptance-checks.py` still wrote `covered_by: []` into every note it produced. **The reason recorded for removing it was itself wrong** and is corrected in the file: *"the validator refuses it"* proves too much, since ten more refused fields are still written there on purpose — that rule fires only in a ledger-keeping repo, and migrating a repo that is not one is the script's whole job. `covered_by:` differs in kind: it left the schema outright.
- `src/project_os_cockpit/ledger.py` described `cover_check`'s guard in the present tense, for a function that no longer exists.
- `src/project_os_cockpit/cockpit.py` placed `automation:` *"beside `covered_by:`"*.

## Why

`covered_by:` was a **standing claim** and it rotted silently: rename, delete or `@Ignore` the covering test and the note kept asserting coverage while the check left the run list **permanently, with no signal**. That is worse than a stale verdict, because a stale verdict still asks.

It had also never worked. The field held nothing on **671 of 671** checks fleet-wide ([[ISS-0198]]), and the one function that could have filled it was reachable from no front door ([[ISS-0249]]) — so the mechanism was correct, tested, and had never settled a single check anywhere.

## The failing-test decision, made rather than defaulted

[[TASK-0543]] named two options and the answer is a third.

`mark: fail` is a **walk** verdict in the blocking vocabulary, so emitting it would put a machine-driven population straight into the release gate — the change [[ADR-0031]] recorded as a risk rather than discovering later. Emitting **nothing** leaves the last green run's `pass` standing over a test that now fails, which is the stale-verdict shape this phase exists to remove.

An **invalidation** says what is true: the evidence no longer holds. `ledger.resolve` already clears a standing verdict on one, so no vocabulary was added.

## Behaviour a caller can see

- `note_writes.cover_check` **no longer exists**. A caller gets `AttributeError`.
- `note_writes.retire_check` lost its `promote` parameter, and writes its reason into the note **body** rather than into `verdict_reason:` — a field this repo's validator refuses.
- A hand-written `covered_by:` no longer settles a check on any surface.
- Two new scripts and one new workflow; neither script pushes anything.

## Limits, stated

[[ISS-0209]] is unresolved: **the acceptance gate runs in no repo that holds a check.** The emitter runs in `project-os-cockpit` and nowhere the fleet's data lives, so *"deleting a covering test puts its check back on the run list"* is proved **here** and the fleet is not covered. The workflow's own header says so.

Three checks are declared today — [[TST-0069]], [[TST-0075]], [[TST-0076]] — each mapped by reading the check against the test. The other 31 are person-facing walks and are deliberately undeclared: an undeclared check stays on the run list, which is the conservative direction.

## Independent review — 2026-08-21

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `f5ca55b..07602db`; the author's reasoning trace was not available to it. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — same model as the author, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant rather than read.


**Verdict: changes-requested.** The inversion is the right design, the removal of `covered_by:` is safe and honestly measured, and the headline criterion is genuinely proved. Two defects remain in the emitter, one of them the same class of silent rot this feature exists to end.

### What survived refutation

- **The `covered_by:` removal is safe.** Re-measured across all 12 `SNAPSHOT.yaml`-bearing repos under `~/Dev/repos/`, against `git archive HEAD` as well as the working tree: **671 acceptance checks at HEAD**, of which 635 carry the key and **every single value is the literal `[]`**. Zero non-empty values anywhere, in either tree. No `.base` view, no `.ts`/`.js`, and no script *reads* the field — the only code touching the name refuses it (`LEDGER_MOVED_FIELDS`) or strips it. Removing it changes no repo's gate, exactly as claimed.
- **The headline criterion is proved, not asserted.** `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list` settles a check by a run, deletes the test file, runs again, and asserts the check is blocking. That is a real construction.
- **A `manual` walk survives the stale path.** Constructed: a `method: manual` verdict, then the covering test deleted. The emitter printed *"nothing changed"* and the verdict stood.

### Finding 1 (medium) — the invalidation set is keyed on `--by`, so renaming the CI job makes every prior verdict permanently un-invalidatable

`plan()` computes:

```python
stale = sorted(check for check, verdict in current.items()
               if verdict.method == "automated" and verdict.by == by
               and check not in passing and check not in failing)
```

`by` comes from `--by`, and `.github/workflows/observed-coverage.yml` passes the literal `"ci:observed-coverage"` — a string tied to the workflow's name.

Constructed and executed: settle a check with `--by ci:test`; delete the covering test; run again with `--by ci:renamed-job`. Output was *"nothing changed (0 check(s) observed passing)"* and the check stayed **settled and non-blocking**, with no covering test in the repo.

This note already records catching this class once — *"the invalidation set was computed from the declarations, so deleting the test … removed the check from the set that could be invalidated"*. Keying on `by` is the same defect through a different field: the set that can be invalidated depends on something that can change independently of the evidence. Renaming a CI job is an ordinary edit, and the failure is silent and permanent.

### Finding 2 (medium) — *"Only this emitter's own verdicts"* is false on the failing branch

`plan()`'s docstring states: *"**Only this emitter's own verdicts.** A person's `manual` walk and a `migration` backfill are not the emitter's to overturn."* The `failing` loop in `main()` carries no `method`/`by` filter at all:

```python
for check, tests in sorted(failing.items()):
    if check not in current:
        continue
    ... _ledger.append(..., invalidated_by=run, ...)
```

Constructed: a `method: manual`, `by: user:edwin` verdict, then a run in which a declaring test fails. The emitter invalidated the person's hand walk and the check became blocking.

The *behaviour* is defensible — the evidence is contradicted, and invalidating is the conservative move. The **documented claim is not**, and nothing tests it: `tests/test_observed_coverage.py` never constructs a `manual` or `migration` verdict. Either narrow the code to match the docstring or narrow the docstring to match the code, and add the case.

### Finding 3 (low) — the documentation impact list is short by two files

The `CHG` note's impact list names neither:

- `tools/instructions/TAXONOMY.md:61`, which still states *"a `passing` test named in another's `covered_by:` settles it"*. This commit deleted `_resolve_coverage`, so that sentence is now false. It is template-owned and present in four fleet repos, so the fix belongs upstream — but it should be *named*.
- `tools/scripts/migrate-acceptance-checks.py:149`, which still writes `covered_by: []` into every note it emits while `LEDGER_MOVED_FIELDS` refuses the field in any ledger-keeping repo. Pre-existing rather than introduced here, but this change is what strands it, and eight of twelve repos have not migrated.

## Independent review — second pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `07602db..b635c39` — the first pass's findings and the author's reasoning trace were not available to it, only the seven claims as the notes state them. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]): same model as the author and as the first reviewer, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant.

**This supersedes the first-pass verdict. The `review_response:` above is accurate as far as it goes** — `tools/instructions/TAXONOMY.md` and `tools/scripts/migrate-acceptance-checks.py` are both corrected and both listed, and the emitter's `--by` filter is gone from the invalidation set. Two of the three claims were verified by construction rather than read. But the note itself was **appended to and never corrected**, and the emitter fix opened a hole the note does not know about.

**Finding B (high) — removing the `by` key from the invalidation set opened a new silent-rot hole, and it recurs every run.** `plan`'s `stale` set is now every `method: automated` verdict not re-observed in *this* run. Two runs on one platform that observe different subsets — the two toolchains this tool's own docstring puts in scope — therefore retract each other's verdicts forever. Constructed: a temp repo with `TST-0001` declared by a `.py` test and `TST-0002` by a `.kt` test, one platform, alternating pytest/gradle JUnit reports. At `b635c39`: run 1 `pass TST-0001`; run 2 `pass TST-0002` **+ `invalidate TST-0001 (no covering test observed)`**; run 3 `pass TST-0001` **+ `invalidate TST-0002`**; run 4 `pass TST-0002` + `invalidate TST-0001`. Seven ledger entries after four runs, growing by two per run, and at every instant one of the two checks reads as uncovered although a run observed it passing minutes earlier. The identical script against `07602db` gives **two** entries and `nothing changed` from run 3 onward. So the `by` filter was doing real work, and the fix removed it wholesale instead of separating *which machine wrote it* (correctly irrelevant) from *what this run's scope was* (load-bearing). The bug it fixed — a CI-job rename — happens once; the one it created happens on every run. `.github/workflows/observed-coverage.yml` has a single `observe` job today, so this repo does not trigger it: latent, undetected, in the flattering direction, which is the exact shape of the rot the feature exists to end.

**Finding D (medium) — this note's own impact table still states the behaviour the fix removed.** `git diff --numstat 07602db..b635c39` on this file is `61  0`: sixty-one lines added, **nothing edited**. The table under *What changed* still reads *"a check **this emitter covered**, not observed at all → an invalidation"*, which is precisely the scoping the first pass found false and the fix deleted from the code. The correction lives in a new section thirty lines below. A reader landing on the table — the summary a change note exists to be — gets the retired contract. This is the standard [[ISS-0213]] was held to in `4628aff`, and correctly: *a heading is a landing target, and a reader arriving by link or scroll never sees a warning further up.*

**Finding E (medium) — `migrate-acceptance-checks.py` had one of eleven refused fields removed, and the recorded reason proves too much.** The new comment justifies deleting `covered_by: []` because *"this repo's validator refuses it (`LEDGER-MOVED-FIELD`)"*. Measured against `LEDGER_MOVED_FIELDS` (`validate-docs.py:1930`), the same function still emits **ten more** members of that tuple: `mark`, `verdict_date`, `verdict_reason`, `invalidated_by`, `automation`, `burden`, `evidence`, `section`, `ordinal`, `migrated_from`. If the stated reason were the operative one, ten more lines would have to go with it. The reason that actually distinguishes `covered_by` — it was removed from the schema outright by [[FEAT-0138]], while the other ten are refused *only in a repo that keeps ledgers*, as that constant's own docstring says — is not written down anywhere. A reader applying the recorded reason consistently breaks the migration for the eight fleet repos that have not migrated.

### What survived refutation

- **The `covered_by:` sweep is otherwise complete.** `grep -rn` for `covered_by` / `automation:` / `cover_check` across `src/`, `tools/`, `desktop/`, `docs/`, `tests/` and `.claude/` turns up no other live reader or writer. `docs/references/TESTING-MODEL.md` still describes the old mechanism at length but is **properly quarantined** — the superseded banner is in the section's own first line, naming [[REQ-0057]] and [[FEAT-0138]] — so it is not stranded. `strip-verdict-fields.py` and `LEDGER_MOVED_FIELDS` name the field in order to refuse it, which is correct.
- **The failing/stale asymmetry is sound and is now guarded.** A run that observed the covering test fail has evidence about the check; a run that observed nothing does not. Both directions fire: making the `failing` branch skip non-automated verdicts fails `test_a_failing_test_invalidates_a_persons_walk_too`, and dropping `method == "automated"` from `stale` fails `test_a_run_that_observed_nothing_does_not_retract_a_persons_walk`.
- **`validate-docs.sh` is OK and `--as-committed` passes the full CI step set** (validator + `sync-snapshot --check` + `generate-adapters: all 36 artifacts current`).

## Independent review — third pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `b635c39..c9d6a82`; neither the author's reasoning trace nor either earlier reviewer's working was available to me beyond what these notes themselves record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran both earlier passes, recorded in `reviewed_by` as provenance. Every count below was re-measured from the tree and every guard re-executed against a constructed mutant. **This verdict supersedes the second pass's on this note.**

**Verdict: changes-requested.** Finding D is fixed properly — the impact table was corrected rather than appended to, and I checked all five rows against the code by running the emitter rather than by reading it. Four are exactly right, including the one the feature turns on: a declaring test simply absent from a run's report changes nothing (constructed — a verdict, then three partial runs naming an unrelated test, ledger unchanged at one entry). The fifth row is where the table and the code part company.

**The `@Ignore` row is true only when a verdict is standing.** It reads *"a declaring test **ran and was skipped** (`@Ignore`) → an **invalidation** of a `method: automated` verdict"*. Constructed against a repo where no verdict has ever been recorded: three skipped runs write **three invalidations**, of nothing. And where a verdict *is* standing, the row understates by omitting that it fires again on every subsequent run — see Finding 1.

**Finding 1 (high) — the fix for B closed absence and reopened the same unbounded growth one branch over, and it writes invalidations about nothing.** Two constructions, both against `c9d6a82`:

*The loop that grows.* A temp repo, one acceptance check `TST-0001`, one declaring `.py` test. Run 1 reports it passing → one `mark: pass` entry. Runs 2–5 report the same test as `<skipped/>` → **`invalidate TST-0001` on every single run**, four in a row, ledger at five entries and growing by one per run forever. `@Ignore` is not a one-off like a CI-job rename: it sits in a codebase for weeks while CI runs on every push, so this recurs in exactly the way finding B said the absence rule recurred. The module's own stated invariant — *"## It appends only when the answer CHANGES"* — is false for this branch.

*The events about nothing.* The same repo with **no verdict ever recorded**, three skipped runs: **three invalidations**, of a check the ledger has never heard of. The `failing` branch guards precisely this (`if check not in current: continue`) and `test_a_check_the_ledger_never_heard_of_is_not_invalidated` states the principle in as many words — *"There is no standing verdict to overtake, and appending an invalidation would be an event about nothing"* — but it only exercises the *absent* case, so the new branch walks straight past it.

The cause is structural rather than a slip. The declaration-gone half of `stale` is derived from `current`, so an invalidation removes the check from `current` and the branch cannot re-fire; the skipped half iterates `declared` and consults neither `current` nor what it has already written. It needs the same two guards the other two branches carry.

**Finding 2 (medium) — a skipped declaring test is laundered into a `pass` by any sibling that passes.** Constructed: `TST-0001` declared by `test_one` and `test_two`; one report in which `test_one` passes and `test_two` is `<skipped/>`. Output: `emit-coverage: pass TST-0001 (test_one)`, one `mark: pass` entry, no invalidation. `plan`'s docstring says *"A check is **observed passing** only when every test declaring it ran and passed"*, and this commit's new comment says *"**Skipped is observed, and it is not a pass.**"* Neither holds: `seen = [t for t in tests if t in results]` still treats a skipped test as absent, and the new loop can never reach the mixed case because `check in passing` short-circuits it. `test_every_declaring_test_must_pass` exercises only the *failing* sibling, which is why nothing catches it. The consequence is the escape hatch the feature exists to close — add one trivially-passing declaring test and an `@Ignore` on the real one stops being visible anywhere.

**Finding 4 (low) — the `covered_by:` removal stranded a third reference and the note says there were two.** `src/project_os_cockpit/ledger.py:318` (`orphan_evidence`) still reads *"The same guard `cover_check` applies to `covered_by:` and for the same reason"* — present tense about a function this change deleted and a field that left the schema — and `src/project_os_cockpit/cockpit.py:2721` still describes `automation:` as sitting *"beside `covered_by:`"*. Neither is load-bearing. The finding is that the note asserts a closed set (*"**Two files were stranded by the removal and are corrected**"*) produced by a sweep that did not cover `src/`.

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

**Verdict: changes-requested — on one sentence in the impact list.** The event table is right, including the two rows this range corrected: I ran the emitter rather than read it and the `@Ignore` row now fires **once** and only against a standing verdict, and the skipped-sibling row is real. What is still wrong is the claim of closure.

### The headline question: did fixing round three break anything

**No.** Test functions were extracted by name, file by file, at `f5ca55b`, `c9d6a82` and `9a75f11` and the sets diffed. `c9d6a82..9a75f11` **removes nothing**: three functions are added to `tests/test_observed_coverage.py` and no other file changes its set, 1835 → **1838**. Across the whole phase range `f5ca55b..9a75f11` the only removals anywhere are the seven `covered_by:`/promotion tests in `tests/test_checks_view.py`, each replaced in the same file by one guarding the mechanism's absence — that file's count is unchanged at 22 — so 1761 → 1838 with a net `+77` accounted for entirely by five new files (6 + 31 + 17 + 13 + 10).

**The emitter was run in loops rather than read.** Twelve scenarios against a temporary repo, counting ledger entries: `pass` then four `<skipped/>` runs → **2** entries (one `pass`, one invalidation); three skipped runs with no standing verdict → **0**; `pass`, skip, then three passing runs → **3**; declaration deleted, four runs → **2**; declaration moved to another file under the same name, four runs → **1**; moved *and* renamed, four runs → **1**; a `.kt`-declared check across five `.py` runs → never invalidated; `pass` then five failing runs → **2**; a passing sibling with a skipped sibling, four runs → **2**; a `manual` verdict under four skipped runs → **1** (untouched); a `manual` verdict under four failing runs → **2**. Every one is bounded, and the bound is structural: `resolve()` pops an invalidated check out of `verdicts()`, so both the `stale` and the `failing` branch leave the set by construction on the next run. Round three's finding 1 is genuinely closed.

**The three new tests are not passengers.** Reverting `elif seen and not held` to `elif seen` fails `test_a_skipped_sibling_is_not_laundered_into_a_pass` and nothing else. Restoring the round-two `stale` rule verbatim fails `test_a_skipped_test_invalidates_once_not_once_per_run` and `test_a_check_with_no_verdict_is_never_invalidated`. The two earlier repairs still hold their ground: `_withdrawn` returning `True` unconditionally fails the two toolchain tests, and returning `False` for a vanished declaration fails `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list`.

**Round three's finding 3 reproduces exactly, every figure.** Driving the rule's own predicates over `git archive f5ca55b`: **56** owed, **51** terminal, **5** non-terminal, `30 done / 8 merged / 4 implemented / 9 fixed`, earliest `review_date` **2026-07-30** on **eight** notes — `CHG-20260730-Two-Features-Closed`, `FEAT-0045`, `ISS-0037`, `ISS-0057`, `ISS-0068`, `ISS-0069`, `PHASE-011`, `PHASE-013`. All 8 `merged` findings are `CHG-*`. The rule reports 51 at HEAD.

**Suite, validator, CI step set, all observed rather than reported.** `2063 passed, 3 skipped` in 269s; `validate-docs: OK`; `--as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `9a75f11`.

### Finding — *"Four files were stranded by the removal and are corrected"* is a closed set for the third time and is still open

The correction is honest about the first miss (*"a third pass swept `src/` and found two more, so the closed set was not closed"*), and the sweep still stops short of `docs/`. `docs/references/TESTING-MODEL.md:110` tells a reader, **under the heading "## What the cockpit implements today"**, that the cockpit's writes include *Covered by* — a write `note_writes.cover_check`'s deletion removed. Line 107 lists a live filter over `automation`. Lines 130, 133 and 137, under *"### Verified against the code, unchanged"*, assert in the present tense that `_resolve_coverage`'s three properties *"all hold"* and describe `cover_check`'s refusals. This note's second-pass section states the opposite — *"the sweep is otherwise complete … `docs/references/TESTING-MODEL.md` … is **properly quarantined** — the superseded banner is in the section's own first line"* — but that banner is on **"## The automation path"** alone, and its own sentence is the argument against leaving three other headings bare.

Two options and either closes it: put the same first-line banner on the other headings, or stop asserting a closed set and say which directories were swept.

**Finding A (medium) — `junit_results` keys on the bare test name and ANDs across modules, and the collision is live in this repo today.** `test_it_does_not_push` is defined twice: `tests/test_close_out_commit.py:114`, which declares `# Covers: TST-0069`, and `tests/test_observed_coverage.py:510`, which declares nothing. `.github/workflows/observed-coverage.yml` runs the whole suite into one `junit.xml`, so both land under one key and `out[base] = out.get(base, True) and ok` folds them together. Constructed against a temporary repo with exactly that shape: the **non-declaring** twin failing invalidates the standing verdict, output `invalidate TST-0001 (failing: test_it_does_not_push)` — naming a test that covers nothing — and the non-declaring twin being `<skipped/>` blocks the check from ever being observed passing. The reverse direction is the overclaiming one: if the declaring test is absent from a report while its same-named twin passes, the check is reported `pass` on the strength of a test that never declared it. Nothing detects this — `coverage-declarations.py --check` refuses only a marker outside a test and a check id that does not resolve, and there are three duplicated bare names among 1838 test functions in this repo. `junit_results`' docstring states the keying as a design choice (*"which is what the declaration scanner knows"*) and names no hazard; `classname` is in the XML and is not read.

**Finding B (medium) — the one guard that keeps a single run from writing two invalidations for one check is pinned by nothing.** `_withdrawn`'s `if check in passing or check in failing: return False` is load-bearing for the mixed cell: a check declared by two tests, one failing and one `<skipped/>`, is in `failing` *and* satisfies the skipped predicate. Constructed both ways — at HEAD, `pass` then a failing/skipped run gives **2** ledger entries; with those two lines replaced by `if False:`, the same run gives **3**, printing `invalidate` twice for one check, once as *"failing: test_a"* and once as *"no covering test declares it"*. The mutant passes the **entire** `tests/test_observed_coverage.py` — 34 passed. Nothing is wrong with the code today; what is missing is the pin, and duplicated ledger writes are the exact defect round three spent itself removing one line away.

*(Two conservative gaps, recorded and not requested, because both are consistent with what `_withdrawn`'s docstring actually says. A check declared in two toolchains whose `.py` test is `@Ignore`d while the `.kt` test is absent from the report never withdraws — constructed, four runs, the standing `pass` survives — which is the silent-rot direction for the two-toolchain case the feature was built for. And a parametrised declaring test with one param `<skipped/>` invalidates a standing verdict and can then never be observed passing again, because `base` lands in `results` and `skipped` at once. Neither refutes a criterion: REQ-0057's fourth criterion is *"a deleted covering test re-arms its check"*, which is proved.)*


## Independent review — fifth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `9a75f11..991838e`, widened to `f5ca55b..991838e` for the did-anything-break question; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all four earlier passes, and `reviewed_by` records that as provenance rather than as a compliance token. Every claim below was established by running the code, mutating it, or counting the tree. **This supersedes the fourth pass's verdict on this note.**

**Verdict: changes-requested.** The fourth pass's two findings on this note are fixed as stated and each is now guarded by a test that fails when the fix is reverted — I mutated all five paths and every mutant was caught. What changed underneath them is the rule itself: the new resolution step introduces a third outcome the design has no branch for, and routes it into the one branch that means *do nothing*. This note is at terminal status carrying it.

### What the fourth pass asked for, verified by mutation rather than by reading

- **`classname` is read and the duplicate is renamed.** `test_it_does_not_push` now exists only in `tests/test_close_out_commit.py`; the twin is `test_the_emitter_does_not_push`. Two duplicated bare names remain among 1841 test functions (`test_the_entrypoint_runs_as_a_subprocess`, `test_the_mutant_is_caught`) and neither declares a check, and no two test files in this repo share a basename.
- **The three checks this repo declares all still resolve against a real run.** Ran the declaring files with `--junitxml` and drove `emit-coverage.py --dry-run` over the report: `pass TST-0069` (all five declaring tests), `pass TST-0075`, `pass TST-0076`. pytest writes `classname="tests.test_close_out_commit"` and `cls == dotted` matches.
- **Dropping the bare-name fallback is guarded.** Re-adding a fallback to `_resolve`, and reducing `_resolve` to bare-name matching, each fail `test_two_tests_with_one_name_are_not_the_same_test` and `test_a_report_that_does_not_name_the_file_emits_nothing`. Ignoring `classname` in `junit_results` fails 14 tests.
- **`_withdrawn`'s guard is no longer pinned by nothing.** Mutating `if check in passing or check in failing:` to `if False:` fails `test_one_check_gets_at_most_one_invalidation_per_run` and that test alone.
- **The earlier repairs still hold.** Ledger entries counted over loops: `pass` then four skipped runs → 2; three skipped runs with no standing verdict → 0; declaration deleted, four runs → 2; `pass` then five failing runs → 2; a `.kt`-declared check across five `.py`-only runs → 1, never invalidated; the declaring test renamed inside its own file, four runs → 1.

### Finding 1 (high) — the resolution rule reintroduces silent rot: a declaration that stops resolving neither emits nor invalidates

`_resolve` matches a declaration's file against the report's `classname` by `cls == dotted`, `cls.endswith("." + stem)` or `cls == stem`, and returns `None` otherwise. `None` is then folded into the same bucket as *absent from this run*: `_withdrawn` sees a non-empty `keys` list, `any(k in skipped …)` is `False`, and it returns `False`. So a check carrying a standing `method: automated` `pass` whose declaring test becomes unmatchable is **never invalidated, never re-observed, and never reported** — the emitter prints *"nothing changed (0 check(s) observed passing)"* on every run thereafter.

**Measured, both sides of the fix.** A declaring test wrapped in a class — pytest then writes `classname="tests.test_thing.TestGroup"` — emitted `pass TST-0001` at `9a75f11` and emits nothing at `991838e`. Sequenced: observe a `pass`, wrap the same test in a class, run four more times → ledger still holds exactly one entry, and `ledger.verdicts()` still returns `mark='pass', method='automated'`. The scanner still finds the declaration, `coverage-declarations.py --check` still reports OK, and nothing anywhere says the check stopped being observed. That is `covered_by:`'s silent rot — *"the note keeps asserting coverage while the check drops out of the run list permanently, with no signal"* — reproduced for the third time inside the tool built to end it, and this time by the repair rather than by the original.

**The emitter's own distinction is the fix it did not apply to itself.** It argues at length that *skipped* and *absent* are different facts and must not share a branch. Round four created a third state — **present in the report and not attributable** — and routed it into *absent* without a word. *Absent* means *this run was not about that test*; *unattributable* means *this run may well have run it and the tool cannot tell*, which is not evidence of a partial run and should not be treated as one.

**Two of the three claimed toolchain shapes do not hold either.** The docstring says *"a JVM one in `.../com/x/FooTest.kt` matches `com.x.FooTest`; an XCTest one matches its class."* It matches only when the class name equals the **file stem**. Constructed: `src/test/kotlin/com/x/FooTest.kt` containing `class BarTest`, report `classname='com.x.BarTest'` → nothing emitted; the same file containing `class FooTest` → `pass TST-0001`. Java enforces the equality for public classes; Kotlin does not, JUnit 5 `@Nested` produces `com.x.OuterTest$Inner`, and Swift/XCTest routinely puts several classes in one file. This repo has no class-based tests today, so nothing is live here — but the mechanism is the one [[TASK-0542]] scopes to pytest **and JVM**, aimed at a repo with an iOS half.

### Finding 2 (medium) — the collision is narrowed to a basename collision, and the answer now depends on XML ordering

`stem` is the file's **basename**, and `cls.endswith("." + stem)` matches any module or class with that name in any package. When two candidates both match, `_resolve` returns the first in `list(results) + sorted(skipped)` — report order. Constructed in Python, this repo's own toolchain: `tests/test_thing.py` declaring `TST-0001` and `integration/test_thing.py` declaring nothing, both defining `test_the_thing`. Report listing the non-declaring twin first, failing → `invalidate TST-0001 (failing: test_the_thing)`. The **same two entries in the opposite order** → *"nothing changed"*. Identical inputs, opposite verdicts. The Kotlin equivalent (`com.a.FooTest` / `com.b.FooTest` for a declaration in `com/a/FooTest.kt`) reproduces the same way.

`test_a_report_that_does_not_name_the_file_emits_nothing` covers only the case where **neither** candidate matches, and its docstring's *"rather than picking whichever sorted first"* is exactly what the two-match case does. Nothing detects the shape: `--check` refuses a marker outside a test and an unresolvable id, and says nothing about ambiguity. Not live in this repo — no two test files here share a basename — but neither was the bare-name collision until somebody looked.

**Suite, validator, CI step set — observed, not reported.** **2066 passed, 3 skipped** in 269s; `validate-docs: OK` (warnings only); `--as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `991838e`.



## Independent review — sixth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `991838e..c4413e3`, widened to `f5ca55b..c4413e3` for the did-anything-break question; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all five earlier passes, and `reviewed_by` records that as provenance rather than as a compliance token. **This supersedes the fifth pass's verdict on this note.**

**Verdict: approved.** The fifth pass's findings on the emitter are fixed — the class-nesting trigger is gone, the round-four resolver reinstated as a mutant fails three named tests, and the three checks this repo declares all resolve against a real pytest report (`pass TST-0069`, `pass TST-0075`, `pass TST-0076`). The change note's impact list matches what `991838e..c4413e3` actually did. Four residual findings are recorded on [[FEAT-0138]] / [[REQ-0057]] / [[TASK-0543]] — two unguarded rules in `_resolve`, a `NOT ATTRIBUTED` notice that reaches stdout and nothing else, and a `plan()` docstring falsified by its own commit — and none of them blocks this note.

**Suite, validator, CI step set — observed, not reported.** **2072 passed, 3 skipped** in 272s; `validate-docs: OK`, zero errors and 344 warnings; `--as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `c4413e3`.


## Independent review — seventh pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `c4413e3..9784205`, widened to `f5ca55b..9784205` for the did-anything-break question; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all six earlier passes, and `reviewed_by` records that as provenance rather than as a compliance token. Every figure below was produced by running the code, mutating it, rendering it or counting the tree; none of it by reading a docstring and agreeing with it. **This confirms the sixth pass's verdict on this note rather than superseding it** — the sixth pass approved it, and I re-ran its evidence rather than inheriting it.

**Verdict: approved.** The impact list matches what `c4413e3..9784205` actually did to the emitter — a docstring corrected to five return values and a second stream for the one notice that had only stdout — and neither is an impact a caller sees, which is why this note correctly gained no sixth `review_response:` segment: the sixth pass approved it with no findings, so nothing was owed.

**Suite, validator, CI step set — observed, not reported.** `.venv/bin/python -m pytest -q` → **2076 passed, 3 skipped** in 271s. `bash tools/scripts/validate-docs.sh` → `validate-docs: OK`, **zero errors** and 344 warnings. `--as-committed` → *"HEAD passes the full CI step set"*: validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `9784205`.
