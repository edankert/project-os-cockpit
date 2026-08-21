---
type: "[[task]]"
id: TASK-0543
aliases: ["TASK-0543"]
title: "The CI emitter appends observed-coverage entries into the working ledger for its platform"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-21"
reviewed_by: model:claude-opus-5
review_date: 2026-08-21
review_verdict: changes-requested
review_response: "2026-08-21: the `--by` filter is gone from the invalidation set and the failing branch's asymmetry is documented as the decision it is, with tests constructing a `manual` and a `migration` verdict for both directions. || Second pass 2026-08-21: findings B and C fixed. The pass-dedup's --by removal was guarded by nothing (restoring it failed no test); test_a_second_machine_saying_pass_adds_nothing guards it now. || Third pass 2026-08-21: findings 1, 2 and 5 fixed, with three mutants constructed and each failing its named test. The emitter has now had three separate defects of one shape - what counts as evidence of absence - and every one was found by running it in a loop and counting ledger entries rather than by reading it. || Fourth pass 2026-08-21: findings 1 and 2 fixed, both by construction. The bare-name collision and the double invalidation in one run were each mutated and each now fails a named test. The emitter has had five distinct defects, every one found by running it and counting, never by reading it."
review_response_date: 2026-08-21
parent: "[[FEAT-0138-Coverage-Is-Observed-Not-Declared]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# The emitter

## Definition of Done

- [x] A green CI run appends one `method: automated` entry per covered check, with `by:` naming the test and `date:` the run — `.github/workflows/observed-coverage.yml`, `test_a_green_run_appends_one_automated_entry_per_covered_check`.
- [x] A failing test emits `mark: fail` with the failure as the reason, or emits nothing — **decided, and neither**: it emits an **invalidation**. The reasoning is below; `test_a_failing_covering_test_invalidates_rather_than_emitting_fail`.
- [x] The platform comes from the run's target — the observing job runs on `macos-latest` and emits `--platform macos`, because this repo's ledger is `WORKING-macos.json` and emitting macos verdicts from a linux runner would be a false statement about where the evidence came from.
- [x] **Deleting a covering test puts its check back on the run list — proved**, in this repo, by construction: `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list`. [[ISS-0209]]'s limit stands and is stated below.

## Notes

Criterion 4 is the whole point of Stage 2 and the one thing a standing field could not do.

**The limit, and it must not be papered over:** [[ISS-0209]] — the acceptance gate runs in **no repo that holds a check**. Until that is resolved this emitter runs here and nowhere the data lives, so criterion 4 is proved in `project-os-cockpit` only. State that; do not report the fleet as covered.

The failing-test decision matters more than it looks. Emitting `fail` puts a machine-driven population into the release gate — the behaviour change [[ADR-0031]] recorded as a risk rather than discovering later. Same call, same place to record it.

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

`tools/scripts/emit-coverage.py`, reading the declarations and the run's **JUnit XML** — which pytest writes with `--junitxml` and gradle writes natively, so the two toolchains [[TASK-0542]] names need no shared library here either.

### The failing-test decision, made rather than defaulted

This task named two options and the answer is a third, so the reasoning is recorded rather than the choice.

**`mark: fail` is wrong.** `fail` is a *walk* verdict in the blocking vocabulary, so emitting it would put a machine-driven population straight into the release gate — the behaviour change [[ADR-0031]] recorded as a risk rather than discovering later.

**Emitting nothing is wrong too.** It leaves the last green run's `pass` standing over a test that now fails, which is the stale-verdict shape this whole phase exists to remove.

**An invalidation says exactly what is true**: the evidence for that verdict no longer holds. The check goes back on the run list without anybody asserting a walk that never happened. `ledger.resolve` already clears a standing verdict on an invalidation, so no new vocabulary was needed — [[ADR-0037]] decision 6's `invalidated_by` is precisely this event.

### The defect that would have made the whole feature a no-op

The first cut computed the invalidation set as *declared but not observed*. **Deleting the test deletes the declaration too** — so the check left the set that could be invalidated and stayed settled forever. That is `covered_by:`'s silent rot reproduced exactly, inside the tool built to end it.

It is read from the **ledger** now: *this emitter said a machine covered it — did a machine cover it this time?* Caught by `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list`, which **failed on its first run**, which is the only reason it is not still there.

### Three properties worth naming

- **Only this emitter's own verdicts are invalidated.** A person's `manual` walk and a `migration` backfill are not the emitter's to overturn: it observes runs, and it has observed nothing about those.
- **Every declaring test must pass.** A check covered by five tests is covered by all five; reporting it as passing because four did is the overclaiming this phase spent itself removing.
- **It appends only when the answer changes.** The ledger is an event log and an event is a change; an identical re-append on every green run would grow the file and record nothing.
- **A skipped test is not observed.** `@Ignore` is the case [[FEAT-0138]] names beside delete and rename, and it produces an invalidation, not a pass.

### The limit, stated and not papered over

[[ISS-0209]]: the acceptance gate runs in **no repo that holds a check**. The emitter runs here and nowhere the fleet's data lives, so criterion 4 is proved in `project-os-cockpit` **only**. The fleet is not covered and nothing in this task or its workflow claims it is.

### It does not push

The emitter writes the working ledger and stops; the workflow prints the diff and never commits. A commit is local and reversible; a push is publishing, and in this project publishing is a person clicking something. `test_it_does_not_push` and `test_ci_does_not_push_the_ledger`.

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

**This supersedes the first-pass verdict. The `review_response:` above is accurate** — the `--by` filter is gone from the invalidation set and the failing branch's asymmetry is documented and guarded, both confirmed by mutants rather than by reading. **The `--by` removal is nonetheless over-wide, and one half of it is unguarded.**

**Finding B (high) — removing the `by` key from the invalidation set opened a new silent-rot hole, and it recurs every run.** `plan`'s `stale` set is now every `method: automated` verdict not re-observed in *this* run. Two runs on one platform that observe different subsets — the two toolchains this tool's own docstring puts in scope — therefore retract each other's verdicts forever. Constructed: a temp repo with `TST-0001` declared by a `.py` test and `TST-0002` by a `.kt` test, one platform, alternating pytest/gradle JUnit reports. At `b635c39`: run 1 `pass TST-0001`; run 2 `pass TST-0002` **+ `invalidate TST-0001 (no covering test observed)`**; run 3 `pass TST-0001` **+ `invalidate TST-0002`**; run 4 `pass TST-0002` + `invalidate TST-0001`. Seven ledger entries after four runs, growing by two per run, and at every instant one of the two checks reads as uncovered although a run observed it passing minutes earlier. The identical script against `07602db` gives **two** entries and `nothing changed` from run 3 onward. So the `by` filter was doing real work, and the fix removed it wholesale instead of separating *which machine wrote it* (correctly irrelevant) from *what this run's scope was* (load-bearing). The bug it fixed — a CI-job rename — happens once; the one it created happens on every run. `.github/workflows/observed-coverage.yml` has a single `observe` job today, so this repo does not trigger it: latent, undetected, in the flattering direction, which is the exact shape of the rot the feature exists to end.

**Finding C (medium) — the other half of the `by` removal is guarded by nothing.** The pass-dedup in `main` dropped `and standing.by == args.by` and carries a comment asserting the consequence (*"Keying on it appended one entry per CI-job rename"*). I restored that clause in a clean worktree at `b635c39` and ran the **full** suite: 2051 passed, 5 skipped, and the only two failures are worktree-path artefacts (`test_the_project_id_is_the_directory_name_by_default`, `test_the_header_measures_from_the_instant_not_the_day`). No emitter test noticed. Three of the four behaviour changes in this file are pinned — mutants restoring `verdict.by == by` in `stale`, making the `failing` branch skip non-automated verdicts, and dropping `method == "automated"` from `stale` each fail their named test — and this one is not.

### What survived refutation

- Three of the four emitter behaviours are honestly pinned; each named mutant fails exactly its named test and no other.
- `junit_results` handling of a skipped case (absent from the map rather than present-and-true) is unchanged and remains correct for the `@Ignore` case the inversion exists to catch.

## Independent review — third pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `b635c39..c9d6a82`; neither the author's reasoning trace nor either earlier reviewer's working was available to me beyond what these notes themselves record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran both earlier passes, recorded in `reviewed_by` as provenance. Every count below was re-measured from the tree and every guard re-executed against a constructed mutant. **This verdict supersedes the second pass's on this note.**

**Verdict: changes-requested.** Finding C is genuinely fixed: restoring `and standing.by == args.by` in the pass-dedup fails `test_a_second_machine_saying_pass_adds_nothing` and nothing else, so the mutant the response describes does now die. Finding B's rule is right and I reproduced it independently. The new skipped branch is where this task's fourth criterion now leaks.

**Finding 1 (high) — the fix for B closed absence and reopened the same unbounded growth one branch over, and it writes invalidations about nothing.** Two constructions, both against `c9d6a82`:

*The loop that grows.* A temp repo, one acceptance check `TST-0001`, one declaring `.py` test. Run 1 reports it passing → one `mark: pass` entry. Runs 2–5 report the same test as `<skipped/>` → **`invalidate TST-0001` on every single run**, four in a row, ledger at five entries and growing by one per run forever. `@Ignore` is not a one-off like a CI-job rename: it sits in a codebase for weeks while CI runs on every push, so this recurs in exactly the way finding B said the absence rule recurred. The module's own stated invariant — *"## It appends only when the answer CHANGES"* — is false for this branch.

*The events about nothing.* The same repo with **no verdict ever recorded**, three skipped runs: **three invalidations**, of a check the ledger has never heard of. The `failing` branch guards precisely this (`if check not in current: continue`) and `test_a_check_the_ledger_never_heard_of_is_not_invalidated` states the principle in as many words — *"There is no standing verdict to overtake, and appending an invalidation would be an event about nothing"* — but it only exercises the *absent* case, so the new branch walks straight past it.

The cause is structural rather than a slip. The declaration-gone half of `stale` is derived from `current`, so an invalidation removes the check from `current` and the branch cannot re-fire; the skipped half iterates `declared` and consults neither `current` nor what it has already written. It needs the same two guards the other two branches carry.

**Finding 2 (medium) — a skipped declaring test is laundered into a `pass` by any sibling that passes.** Constructed: `TST-0001` declared by `test_one` and `test_two`; one report in which `test_one` passes and `test_two` is `<skipped/>`. Output: `emit-coverage: pass TST-0001 (test_one)`, one `mark: pass` entry, no invalidation. `plan`'s docstring says *"A check is **observed passing** only when every test declaring it ran and passed"*, and this commit's new comment says *"**Skipped is observed, and it is not a pass.**"* Neither holds: `seen = [t for t in tests if t in results]` still treats a skipped test as absent, and the new loop can never reach the mixed case because `check in passing` short-circuits it. `test_every_declaring_test_must_pass` exercises only the *failing* sibling, which is why nothing catches it. The consequence is the escape hatch the feature exists to close — add one trivially-passing declaring test and an `@Ignore` on the real one stops being visible anywhere.

**Finding 5 (low) — `junit_results` was given a second return value and kept its old signature.** `def junit_results(path: Path) -> dict[str, bool]:` returns `(out, skipped)`. Nothing type-checks this file in CI, so it is documentation rather than a defect, but it is documentation that is wrong at the one place a caller reads first.

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

**Verdict: changes-requested — same two emitter findings as [[FEAT-0138]].** The task's own claim that *"three mutants were constructed and each fails its named test"* is true; I built them independently and each kills exactly the tests named and no others. The response's summary of the shape — *"three separate defects of one shape … every one found by running it in a loop and counting ledger entries"* — is accurate, and finding B below is the fourth thing of that shape, sitting one line from the third.

### The headline question: did fixing round three break anything

**No.** Test functions were extracted by name, file by file, at `f5ca55b`, `c9d6a82` and `9a75f11` and the sets diffed. `c9d6a82..9a75f11` **removes nothing**: three functions are added to `tests/test_observed_coverage.py` and no other file changes its set, 1835 → **1838**. Across the whole phase range `f5ca55b..9a75f11` the only removals anywhere are the seven `covered_by:`/promotion tests in `tests/test_checks_view.py`, each replaced in the same file by one guarding the mechanism's absence — that file's count is unchanged at 22 — so 1761 → 1838 with a net `+77` accounted for entirely by five new files (6 + 31 + 17 + 13 + 10).

**The emitter was run in loops rather than read.** Twelve scenarios against a temporary repo, counting ledger entries: `pass` then four `<skipped/>` runs → **2** entries (one `pass`, one invalidation); three skipped runs with no standing verdict → **0**; `pass`, skip, then three passing runs → **3**; declaration deleted, four runs → **2**; declaration moved to another file under the same name, four runs → **1**; moved *and* renamed, four runs → **1**; a `.kt`-declared check across five `.py` runs → never invalidated; `pass` then five failing runs → **2**; a passing sibling with a skipped sibling, four runs → **2**; a `manual` verdict under four skipped runs → **1** (untouched); a `manual` verdict under four failing runs → **2**. Every one is bounded, and the bound is structural: `resolve()` pops an invalidated check out of `verdicts()`, so both the `stale` and the `failing` branch leave the set by construction on the next run. Round three's finding 1 is genuinely closed.

**The three new tests are not passengers.** Reverting `elif seen and not held` to `elif seen` fails `test_a_skipped_sibling_is_not_laundered_into_a_pass` and nothing else. Restoring the round-two `stale` rule verbatim fails `test_a_skipped_test_invalidates_once_not_once_per_run` and `test_a_check_with_no_verdict_is_never_invalidated`. The two earlier repairs still hold their ground: `_withdrawn` returning `True` unconditionally fails the two toolchain tests, and returning `False` for a vanished declaration fails `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list`.

**Round three's finding 3 reproduces exactly, every figure.** Driving the rule's own predicates over `git archive f5ca55b`: **56** owed, **51** terminal, **5** non-terminal, `30 done / 8 merged / 4 implemented / 9 fixed`, earliest `review_date` **2026-07-30** on **eight** notes — `CHG-20260730-Two-Features-Closed`, `FEAT-0045`, `ISS-0037`, `ISS-0057`, `ISS-0068`, `ISS-0069`, `PHASE-011`, `PHASE-013`. All 8 `merged` findings are `CHG-*`. The rule reports 51 at HEAD.

**Suite, validator, CI step set, all observed rather than reported.** `2063 passed, 3 skipped` in 269s; `validate-docs: OK`; `--as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `9a75f11`.

**Finding A (medium) — `junit_results` keys on the bare test name and ANDs across modules, and the collision is live in this repo today.** `test_it_does_not_push` is defined twice: `tests/test_close_out_commit.py:114`, which declares `# Covers: TST-0069`, and `tests/test_observed_coverage.py:510`, which declares nothing. `.github/workflows/observed-coverage.yml` runs the whole suite into one `junit.xml`, so both land under one key and `out[base] = out.get(base, True) and ok` folds them together. Constructed against a temporary repo with exactly that shape: the **non-declaring** twin failing invalidates the standing verdict, output `invalidate TST-0001 (failing: test_it_does_not_push)` — naming a test that covers nothing — and the non-declaring twin being `<skipped/>` blocks the check from ever being observed passing. The reverse direction is the overclaiming one: if the declaring test is absent from a report while its same-named twin passes, the check is reported `pass` on the strength of a test that never declared it. Nothing detects this — `coverage-declarations.py --check` refuses only a marker outside a test and a check id that does not resolve, and there are three duplicated bare names among 1838 test functions in this repo. `junit_results`' docstring states the keying as a design choice (*"which is what the declaration scanner knows"*) and names no hazard; `classname` is in the XML and is not read.

**Finding B (medium) — the one guard that keeps a single run from writing two invalidations for one check is pinned by nothing.** `_withdrawn`'s `if check in passing or check in failing: return False` is load-bearing for the mixed cell: a check declared by two tests, one failing and one `<skipped/>`, is in `failing` *and* satisfies the skipped predicate. Constructed both ways — at HEAD, `pass` then a failing/skipped run gives **2** ledger entries; with those two lines replaced by `if False:`, the same run gives **3**, printing `invalidate` twice for one check, once as *"failing: test_a"* and once as *"no covering test declares it"*. The mutant passes the **entire** `tests/test_observed_coverage.py` — 34 passed. Nothing is wrong with the code today; what is missing is the pin, and duplicated ledger writes are the exact defect round three spent itself removing one line away.

*(Two conservative gaps, recorded and not requested, because both are consistent with what `_withdrawn`'s docstring actually says. A check declared in two toolchains whose `.py` test is `@Ignore`d while the `.kt` test is absent from the report never withdraws — constructed, four runs, the standing `pass` survives — which is the silent-rot direction for the two-toolchain case the feature was built for. And a parametrised declaring test with one param `<skipped/>` invalidates a standing verdict and can then never be observed passing again, because `base` lands in `results` and `skipped` at once. Neither refutes a criterion: REQ-0057's fourth criterion is *"a deleted covering test re-arms its check"*, which is proved.)*

### What survived refutation on this note

- **The `stale` rule is correct and bounded in every loop I could build.** Twelve scenarios, counted rather than reasoned about; the list is in [[PHASE-037]]'s fourth-pass section. A declaration moved to a different file under the same test name changes nothing (four runs, one entry); moved *and* renamed also settles at one, because the rename withdraws the old claim and the new name re-emits. A `.kt`-declared check survives five `.py` runs untouched.
- **`method: automated` and nothing else**, in the `stale` direction, and the documented asymmetry with `failing` is real: a `manual` verdict survives four skipped runs and is invalidated by a failing one. Both directions constructed.
- **The `junit_results` annotation is correct** and the second element is genuinely a `set[str]`.
