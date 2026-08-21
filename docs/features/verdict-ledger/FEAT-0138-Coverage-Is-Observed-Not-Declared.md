---
type: "[[feature]]"
id: FEAT-0138
aliases: ["FEAT-0138"]
title: "Coverage is observed, not declared — the test names the check it covers, CI emits the entry, and a deleted test simply stops emitting"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-21"
reviewed_by: model:claude-opus-5
review_date: 2026-08-21
review_verdict: approved
review_response: "2026-08-21: the emitter's invalidation set keyed on `--by`, so renaming the CI job stranded every prior verdict - covered_by's rot for a second time in one tool. The filter is `method: automated` alone now, guarded by test_renaming_the_ci_job_does_not_strand_prior_verdicts. The failing branch deliberately invalidates any standing verdict and the docstring says so. || Second pass 2026-08-21: finding B was the sharpest - removing the --by filter made absence-in-this-run the trigger, so a .py run and a .kt run on one platform retracted each other every cycle. The rule is now 'is the declaration gone', with skipped kept separate from absent; four mutants constructed and each fails its named test. || Third pass 2026-08-21: findings 1, 2, 4 and 5 fixed. The invalidation set is read off the ledger for both sub-cases now, so an @Ignore invalidates once rather than once per run and a check with no verdict is never invalidated; a skipped sibling no longer launders a check into a pass; two more src/ comments described the deleted cover_check. || Fourth pass 2026-08-21: findings 1, 2 and 5 fixed. The emitter identified a test by its bare name and the collision was LIVE in this repo - test_it_does_not_push in two modules, one declaring TST-0069 and one declaring nothing. classname is read now, with no bare-name fallback, and the duplicate is renamed. || Fifth pass 2026-08-21: F2 and F3 fixed. Round four's classname matching silently stopped emitting for any test inside a class (pytest writes tests.mod.TestGroup) and folded present-and-unattributable into absent-from-this-run. Resolution is three tiers now - module or nested in it, then file stem, then nothing - tier 1 exhausted before tier 2, a tie is a refusal, and an unattributable test is REPORTED rather than guessed. Three mutants including the pre-fix resolver each fail a named test. || Sixth pass 2026-08-21: approved with four guard gaps recorded; THREE are closed. The fourth - an unattributable run reaching stderr - now prints there, but the run still exits 0 with the stale verdict standing and 'nothing changed' beside it. The headline closed, the finding did not, and saying 'all four' was the overclaim this phase exists to remove. Tier precedence and tier-1 tie-refusal were guarded by nothing - swapping the tiers passed 43 tests and the whole suite while turning a pass into silence - and NOT ATTRIBUTED reached stdout only."
review_response_date: 2026-08-21
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
goal: "A claim that a machine covers a check is produced by a run rather than asserted in frontmatter, so deleting or disabling the covering test puts the check back on the run list on its own."
requirements: ["[[REQ-0057-Coverage-Is-Observed-From-A-Run]]"]
tasks: ["[[TASK-0541-Seed-The-Mapping-Before-Deleting-The-Field]]", "[[TASK-0542-The-Test-Declares-The-Check]]", "[[TASK-0543-The-CI-Emitter-Writes-Into-The-Working-Ledger]]"]
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ISS-0198-Automation-And-Covered-By-Are-Empty-On-All-669-Checks]]", "[[DES-0012-Tests-In-Two-Flows]]"]
tags: [feature]
---

# The dependency inverts

## Goal

`covered_by:` on the check is a **standing claim** and it rots silently: rename, delete or `@Ignore` the covering test and the note keeps asserting coverage while the check drops out of the run list permanently, with no signal. That is worse than a stale verdict, because a stale verdict still asks.

Invert it. **The test declares the check** — `@Covers("TST-0028")`, or a comment-and-grep convention for v1 — and the CI run emits `method: automated` entries into the working ledger. A deleted test stops emitting and the check reappears on its own.

## Why this is the version that works, measured

[[ISS-0198]] tried the standing claim and closed with the field **deliberately empty**: `your-trainer`'s 203 annotated bodies name **54 JVM test classes and not one `TST-*` id**, and `cover_check` correctly refuses a link to something no runner can execute. Filling it would have meant inventing 54 unrunnable notes.

Under observed coverage that population is exactly the one that works. The 54 classes each declare the check they cover in their own source, the gradle run emits, and nothing has to invent a note for a command nobody can execute.

## Scope

- **Seed before deleting.** `covered_by:` holds nothing anywhere, so the real seed is the 203 prose annotations. Extract them before [[FEAT-0134]] removes `automation:`.
- The declaration convention, per language. Comment-and-grep for v1 — this repo is pytest, `your-trainer` is JVM, and a v1 that needs a shared annotation library ships nowhere.
- The emitter: a CI run appends `method: automated` entries for what it observed.

## Out of scope

- **Making CI run in the fleet repos.** [[ISS-0209]]: the acceptance gate runs in no repo holding a check. Until that is resolved, the emitter runs here and nowhere the data lives, and this feature must not claim otherwise.

## Acceptance

- [x] The 203 annotations are extracted and recorded before `automation:` is removed — [[TASK-0541]], 278 checks naming 81 JVM classes, committed.
- [x] A test declares the check it covers, in a form one grep finds — [[TASK-0542]].
- [x] A CI run appends observed-coverage entries to the working ledger for its platform — [[TASK-0543]].
- [x] Deleting a covering test puts its check back on the run list, proved — **in this repo only**; [[ISS-0209]] is unresolved and the limit below is unchanged.
- [x] Nothing declares coverage in a note — `covered_by:` is out of the reader, the writer and the schema; [[REQ-0039]] is superseded by [[REQ-0057]].

## Re-homed out of PHASE-038, 2026-08-19

**Stage 2 is a body of work, not a leftover.** [[PHASE-038]] closed on the thing it was opened for — a verdict is an event, and the ledger is the only place one lives — and its nine exit criteria are met. Observed coverage is the *next* argument, and holding a finished phase open for it would make the phase's status say something false about the work that is done.

The seed it depends on is safe: [[TASK-0541]] extracted **278 checks naming 81 JVM classes** before [[TASK-0530]] removed the field they lived in, and that file is committed.

What it still needs before anybody starts it: a declaration convention that works in pytest *and* JVM without a shared library, and [[ISS-0209]] — the acceptance gate runs in no repo that holds a check, so an emitter would run here and nowhere the data lives.

## The tasks came too, 2026-08-20 — they had not

Re-homing this feature into [[PHASE-037]] on 2026-08-20 moved the **feature** and left [[TASK-0542]] and [[TASK-0543]] pointing at [[PHASE-999]]. `PHASE-CHILDREN` gates a phase on notes naming it in `phase:`, so both were invisible to the gate on the phase that owns their work — and invisible to every other gate too, because `PHASE-999` is never closed. A child in a parking lot cannot hold anything open.

Same shape as the miss the phase's own widening note records one level up: *"FEAT-0138 also pointed at PHASE-999 without ever being listed in it, which is why nothing flagged it."*

Both now name `PHASE-037`, in the notes and in `SNAPSHOT.yaml` — `sync-snapshot.py` propagates status but **not** `phase`, so that second edit is by hand. [[TASK-0541]] keeps `PHASE-038`: it is `done`, and a finished task records where the work actually happened.

**The consequence is deliberate and it is not small.** `PHASE-037` cannot close while either is unresolved, and neither can start: this feature's own note says what they wait on — a declaration convention that works in pytest *and* JVM without a shared library, and [[ISS-0209]], which is why an emitter would run here and nowhere the data lives.

## Independent review — fresh-context pass, 2026-08-20 (`4521a7a`)

Separate session, `model:claude-opus-5`, starting from the notes and the diff with no access to the author's reasoning. Same model family as the author, recorded in `reviewed_by`; the independence claimed here is **context**, not weights ([[project-os-dev#ADR-0013]]).

**Verdict: approved.** The re-homing claim was verified by construction, not by reading.

Forcing `PHASE-037` to `done` in a scratch copy of `HEAD` (in the phase note **and** in `SNAPSHOT.yaml` — `PHASE-CHILDREN` resolves the phase's status through `effective_status`, which reads the snapshot) produces an error naming **`TASK-0542 (backlog)`** and **`TASK-0543 (backlog)`** among fourteen unresolved children. Before the re-homing both named `PHASE-999`, whose status is `planned` and therefore outside `CLOSED_PHASE_STATUSES` — so *"invisible to every gate"* is literally right.

`sync-snapshot.py` propagates `status` and not `phase`, so the hand edit to `SNAPSHOT.yaml` was required rather than belt-and-braces. Both entries carry `PHASE-037` there.

Nothing in this note claims the feature is started, and nothing in the diff starts it. `status: backlog` is unchanged and correct.


## Done 2026-08-21 — the inversion is built, and the limit is unchanged

Three pieces, and each is small:

- **The declaration.** `# Covers: TST-0044` inside the test, one comment prefix per language, findable by `grep -rn "Covers: TST-" .`. No annotation, no library, works in pytest and JVM today ([[TASK-0542]]).
- **The observation.** JUnit XML from the run — pytest writes it with `--junitxml`, gradle writes it natively — so the toolchain-portability requirement is met by the *report format* rather than by a shared dependency ([[TASK-0543]]).
- **The emission.** `pass` for a check every declaring test observed passing; an **invalidation** for one whose covering test failed, and for one this emitter previously covered and did not observe at all.

### The third event is the feature

*Delete the covering test and the check reappears on the run list, by itself.* Under the standing claim the note kept asserting coverage and the check left the run list **permanently, with no signal**. Under observed coverage the run stops seeing it and says so.

That is proved by construction and not argued: `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list` settles a check by a run, deletes the test, runs again, and requires the check back in `blocking()`.

**It failed on its first execution**, and the reason is worth keeping: the invalidation set was computed as *declared but not observed*, and deleting the test deletes the declaration too — so the check left the set that could be invalidated and stayed settled forever. `covered_by:`'s silent rot, reproduced inside the tool built to end it. It is read from the **ledger** now.

### `covered_by:` is gone, and it had never worked

Criterion 5 was already true as a description of the corpus — the field held nothing on **671 of 671** checks ([[ISS-0198]]) — and the mechanism that permitted it was intact. Removing it took nothing away and closed the gap:

- `Item.covered_by`, `Item.covered_by_status`, `covered_by_passing` and `_resolve_coverage` are deleted; `settled` is `checked or reconciled or excepted`.
- `note_writes.cover_check` is deleted ([[ISS-0249]] option 3, on the condition that issue named — [[FEAT-0131]] closed `done` without ever needing it).
- [[REQ-0039]] is `superseded` by [[REQ-0057]]. Its direction survives and is now **structural**: a machine's exit code can discharge a person's checkbox and never the reverse, because only a run emits `method: automated`.

### What is declared today

Three checks — [[TST-0069]], [[TST-0075]], [[TST-0076]] — each mapped by reading the check against the test. The other 31 are person-facing walks and are **deliberately undeclared**: inventing a mapping for them would be the assertion this feature exists to remove, and an undeclared check stays on the run list, which is the conservative direction.

### The limit, restated because it did not move

[[ISS-0209]]: the acceptance gate runs in **no repo that holds a check**. The emitter runs here and nowhere the fleet's data lives. Criterion 4 is proved in `project-os-cockpit` and the fleet is not covered — the workflow says so in its own header, and nothing in this note claims otherwise.

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

**This supersedes the first-pass verdict. The `review_response:` above is accurate on both claims** — the `--by` filter is gone from the invalidation set, `test_renaming_the_ci_job_does_not_strand_prior_verdicts` genuinely guards it (restoring `verdict.by == by` in `plan` fails that test and nothing else), and the failing branch's asymmetry is now documented as the decision it is and is guarded in both directions. **But the fix traded a one-off failure for a recurring one, and the trade is not recorded anywhere.**

**Finding B (high) — removing the `by` key from the invalidation set opened a new silent-rot hole, and it recurs every run.** `plan`'s `stale` set is now every `method: automated` verdict not re-observed in *this* run. Two runs on one platform that observe different subsets — the two toolchains this tool's own docstring puts in scope — therefore retract each other's verdicts forever. Constructed: a temp repo with `TST-0001` declared by a `.py` test and `TST-0002` by a `.kt` test, one platform, alternating pytest/gradle JUnit reports. At `b635c39`: run 1 `pass TST-0001`; run 2 `pass TST-0002` **+ `invalidate TST-0001 (no covering test observed)`**; run 3 `pass TST-0001` **+ `invalidate TST-0002`**; run 4 `pass TST-0002` + `invalidate TST-0001`. Seven ledger entries after four runs, growing by two per run, and at every instant one of the two checks reads as uncovered although a run observed it passing minutes earlier. The identical script against `07602db` gives **two** entries and `nothing changed` from run 3 onward. So the `by` filter was doing real work, and the fix removed it wholesale instead of separating *which machine wrote it* (correctly irrelevant) from *what this run's scope was* (load-bearing). The bug it fixed — a CI-job rename — happens once; the one it created happens on every run. `.github/workflows/observed-coverage.yml` has a single `observe` job today, so this repo does not trigger it: latent, undetected, in the flattering direction, which is the exact shape of the rot the feature exists to end.

**Finding C (medium) — the other half of the `by` removal is guarded by nothing.** The pass-dedup in `main` dropped `and standing.by == args.by` and carries a comment asserting the consequence (*"Keying on it appended one entry per CI-job rename"*). I restored that clause in a clean worktree at `b635c39` and ran the **full** suite: 2051 passed, 5 skipped, and the only two failures are worktree-path artefacts (`test_the_project_id_is_the_directory_name_by_default`, `test_the_header_measures_from_the_instant_not_the_day`). No emitter test noticed. Three of the four behaviour changes in this file are pinned — mutants restoring `verdict.by == by` in `stale`, making the `failing` branch skip non-automated verdicts, and dropping `method == "automated"` from `stale` each fail their named test — and this one is not.

### What survived refutation

- **The asymmetry argument is sound.** *The run observed the covering test fail, which is evidence about the check; a run that observed nothing has nothing to say about a person's walk.* Both branches fire against their mutants: skipping non-automated verdicts in the `failing` loop fails `test_a_failing_test_invalidates_a_persons_walk_too`; dropping `method == "automated"` from `stale` fails `test_a_run_that_observed_nothing_does_not_retract_a_persons_walk`. The one cost the argument does not price is a **flake**: a flaky declaring test now destroys a person's walk from March, and the only recovery is another walk. Worth a sentence, not a redesign.
- **The `covered_by:` removal is clean.** No live reader or writer of `covered_by` / `cover_check` remains outside code that refuses or strips the field; `docs/references/TESTING-MODEL.md` is properly quarantined with the banner in the section's own first line.

## Independent review — third pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `b635c39..c9d6a82`; neither the author's reasoning trace nor either earlier reviewer's working was available to me beyond what these notes themselves record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran both earlier passes, recorded in `reviewed_by` as provenance. Every count below was re-measured from the tree and every guard re-executed against a constructed mutant. **This verdict supersedes the second pass's on this note.**

**Verdict: changes-requested.** Finding B's stated fix is the right rule — *is the declaration gone*, not *did this run see it* — and I confirmed it by building the alternating-toolchain loop myself: three full `.py`/`.kt` cycles on one platform produce **two** ledger entries, both `pass`, no retraction. The `--by` removal, the failing-branch asymmetry and the skipped/absent distinction are all guarded by tests that fail against constructed mutants. But the branch added to carry the `@Ignore` case reintroduces the defect finding B was about, and the response's claim that the two are now separated does not survive execution.

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

**Verdict: changes-requested — two properties of the emitter, neither introduced by round three, neither refuting a criterion.** The inversion works, the loops are bounded, and the three new tests all kill their mutants. What I found is one live misattribution hazard that has been in `junit_results` since the first cut and has a concrete instance in this repo today, and one load-bearing guard that no test pins.

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

**Verdict: approved.** The fifth pass's two findings on this note are fixed, and the fix is real rather than reworded — I established every claim by running the emitter and counting, never by reading the docstring.

- **The class-nesting trigger is gone and the round-four resolver is now a caught mutant.** Reinstating round four's `_resolve` verbatim fails three named tests: `test_a_test_inside_a_class_still_resolves`, `test_two_files_with_one_stem_are_not_order_dependent` and `test_a_test_it_cannot_place_is_reported_not_guessed`.
- **The three checks this repo declares still resolve on a real run.** Ran the declaring files with `--junitxml` and drove `emit-coverage.py --dry-run` over the report: `pass TST-0069` (all five declaring tests), `pass TST-0075`, `pass TST-0076`. pytest writes `classname="tests.test_close_out_commit"` and tier 1 matches exactly.
- **The tier shapes hold against real report shapes.** A test nested in a class (`tests.test_thing.TestGroup`) resolves through tier 1's prefix; `com.x.FooTest`, bare `FooTest` and `src.test.kotlin.com.x.FooTest` resolve through tier 2; `junit_results` strips `test_x[param]` to the function name before keying, so a parametrised declaring test is not silently dropped.
- **No unbounded growth in any loop.** Six identical passing runs → one append then stable; four consecutive failing runs → one invalidation then stable; `pass` → `fail` → `pass` → `pass` → three transitions, three entries.

### Finding 1 (medium) — the bold tier-precedence claim is guarded by nothing, and reversing it changes answers

`_resolve`'s docstring says *"**Tier 1 must be exhausted before tier 2 is consulted.**"* Swapping the two blocks passes **all 43** tests in `tests/test_observed_coverage.py` and the whole 2072-test suite. It is not a cosmetic ordering: for a declaration nested in a class with a same-named test elsewhere that **failed**, the shipped order emits `pass TST-0001` and the reversed order emits nothing — and against a standing verdict it would invalidate off the wrong file's failure. `test_two_files_with_one_stem_are_not_order_dependent` cannot reach this, because its twin pair **ties in tier 2** and falls through to tier 1 either way round; it demonstrates the tie rule and is silent about precedence.

### Finding 2 (medium) — the tie-refusal is guarded in tier 2 and unguarded in tier 1

Mutating `if exact: return None` to `return exact[0]` passes the entire suite. Constructed: `tests/test_thing.py` declaring `TST-0001`, the report holding `tests.test_thing.TestA` (passed) and `tests.test_thing.TestB` (failed) — two classes in one module, an ordinary pytest shape. As shipped, both orders refuse and print `NOT ATTRIBUTED`, which is right. With the mutant, `pass TST-0001` in one order and *"nothing changed"* in the other: identical inputs, opposite verdicts, decided by XML ordering — the sentence the fifth pass's finding was filed under, now true of the tier the fix left unpinned. Two adjacent rules are unguarded the same way: dropping the dot from tier 1's prefix test (so `tests/test_a.py` matches `classname="tests.test_abc"`) and loosening tier 2 from *last component* to `endswith` (so `com.x.MyFooTest` matches a declaration in `FooTest.kt`) both pass everything.

### Finding 3 (medium) — `NOT ATTRIBUTED` reaches stdout and nothing else

Measured: a check observed `pass`, then six consecutive runs in which its declaring test is present but unattributable. Every run prints the notice, every run **also** prints *"nothing changed (0 check(s) observed passing)"*, the exit code stays **0**, the ledger stays at one entry, and `verdicts()` keeps returning `mark='pass', method='automated'`. Nothing in the record, and nothing on any surface, can tell a reader the check stopped being observed. The note claims only that the state is *reported rather than guessed*, which is true — so this is a residual rather than an overclaim, but it is the half of the fix this phase's own thesis says has to exist.

### Finding 4 (low) — one docstring was falsified by its own commit

`tools/scripts/emit-coverage.py:121` still says `plan` returns `(passing, failing, stale, current)`; this commit changed it to return five values.

**None of these four blocks the note.** The behaviour is correct in every construction I could build; what is missing is a guard on two rules the code asserts in bold, and a record for a state the run now announces.

**Suite, validator, CI step set — observed, not reported.** **2072 passed, 3 skipped** in 272s; `validate-docs: OK`, zero errors and 344 warnings; `--as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `c4413e3`.


## Independent review — seventh pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `c4413e3..9784205`, widened to `f5ca55b..9784205` for the did-anything-break question; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all six earlier passes, and `reviewed_by` records that as provenance rather than as a compliance token. Every figure below was produced by running the code, mutating it, rendering it or counting the tree; none of it by reading a docstring and agreeing with it. **This confirms the sixth pass's verdict on this note rather than superseding it** — the sixth pass approved it, and I re-ran its evidence rather than inheriting it.

**Verdict: approved.** The sixth pass's four findings are answered and three are fully closed, each verified by mutant rather than by reading: swapping the two tiers in `_resolve` fails **exactly** `test_the_declarations_own_module_beats_a_bare_stem_match`; `if exact: return exact[0]` fails **exactly** `test_two_classes_in_the_declarations_module_are_a_refusal`; deleting the stderr line fails `test_an_unattributable_run_says_so_on_stderr_too`; and `plan()`'s docstring now names all five return values. The emitter was run in loops with entries counted — 6×pass → 1, 4×fail → 0, pass/fail/pass/pass → 3, pass then 5×skipped → 2, pass then 5×absent → 1 — and grows only on a transition.

**One sentence in this note's own `review_response:` is wider than what happened.** *"All four now closed"* — three are. The third finding's body was *"nothing in the record, and nothing on any surface, can tell a reader the check stopped being observed"*, and after six consecutive unattributable runs the verdict is still `mark='pass', method='automated'`, the exit code still 0, the ledger still one entry, stdout still ending *"nothing changed"*. The headline closed; the finding did not. [[TASK-0543]]'s entry for the same edit says *"NOT ATTRIBUTED on stderr"* and is exactly right.

Two rules named by the sixth pass and never claimed as fixed remain unguarded, confirmed here: dropping the dot from tier 1's prefix test, and loosening tier 2 from *last component* to `endswith`, each still pass the whole file.

**Suite, validator, CI step set — observed, not reported.** `.venv/bin/python -m pytest -q` → **2076 passed, 3 skipped** in 271s. `bash tools/scripts/validate-docs.sh` → `validate-docs: OK`, **zero errors** and 344 warnings. `--as-committed` → *"HEAD passes the full CI step set"*: validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `9784205`.
