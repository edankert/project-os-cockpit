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
review_verdict: changes-requested
review_response: "2026-08-21: the emitter's invalidation set keyed on `--by`, so renaming the CI job stranded every prior verdict - covered_by's rot for a second time in one tool. The filter is `method: automated` alone now, guarded by test_renaming_the_ci_job_does_not_strand_prior_verdicts. The failing branch deliberately invalidates any standing verdict and the docstring says so. || Second pass 2026-08-21: finding B was the sharpest - removing the --by filter made absence-in-this-run the trigger, so a .py run and a .kt run on one platform retracted each other every cycle. The rule is now 'is the declaration gone', with skipped kept separate from absent; four mutants constructed and each fails its named test."
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
