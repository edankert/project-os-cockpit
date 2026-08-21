---
type: "[[change]]"
id: CHG-20260821-Coverage-Is-Observed-Not-Declared
review_verdict: changes-requested
review_response: "2026-08-21: the impact list was short by two files (TAXONOMY.md, migrate-acceptance-checks.py) and both are now corrected and listed; the emitter's `--by` filter is removed. || Second pass 2026-08-21: finding D fixed - the impact table stated the retired scoping and was appended to rather than corrected. It now has five rows, including the one the whole feature turns on: a declaring test simply absent from a run's report changes nothing. || Third pass 2026-08-21: finding 4 fixed - the impact list said 'two files stranded' and the set was not closed; it is four, and the migrate script's recorded reason was itself wrong. The emitter's event table gains the skipped-sibling case."
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
