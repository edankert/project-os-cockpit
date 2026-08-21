---
type: "[[requirement]]"
id: REQ-0057
review_verdict: changes-requested
review_response: "2026-08-21: same two emitter findings as FEAT-0138, fixed and guarded. Criterion 1's blast radius was also short by two files: TAXONOMY.md still described `covered_by:` settling a check, and migrate-acceptance-checks.py still wrote the field; both corrected. || Second pass 2026-08-21: findings B, C and E fixed. E is the sharpest of those - the migrate script's comment justified dropping covered_by: by the validator refusing it, which proves too much, since ten more refused fields are still written on purpose. The real distinction (covered_by left the schema; the ten are refused only in a ledger-keeping repo) is written down now. || Third pass 2026-08-21: findings 1, 2 and 4 fixed. The stranded-file set the change note called closed was not - ledger.py and cockpit.py both described cover_check in the present tense."
review_response_date: 2026-08-21
review_date: 2026-08-21
reviewed_by: model:claude-opus-5
aliases: ["REQ-0057"]
title: "Coverage is observed from a run and never declared on a note — a deleted covering test puts its check back on the run list"
status: implemented
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-21"
priority: medium
scope: "automation coverage"
implements: "[[FEAT-0138-Coverage-Is-Observed-Not-Declared]]"
acceptance:
  - "[x] No note declares that a machine covers it — `covered_by:` removed from `Item`, from `settled`, from the loader and from the write path; refused by `LEDGER-MOVED-FIELD` in any ledger-keeping repo (`test_a_note_can_no_longer_declare_that_a_machine_covers_it`)."
  - "[x] A test declares the check it covers, in a form one grep finds — `# Covers: TST-####`, [[TASK-0542]] (`test_one_grep_finds_every_declaration`)."
  - "[x] A CI run appends observed-coverage entries to the working ledger for its platform — `.github/workflows/observed-coverage.yml` + `tools/scripts/emit-coverage.py`, [[TASK-0543]]."
  - "[x] Deleting or disabling a covering test puts its check back on the run list, proved — `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list` and `test_disabling_the_covering_test_does_the_same`. **In this repo only**; [[ISS-0209]] is unresolved and that limit is restated below."
  - "[x] The 203 automation annotations are extracted and recorded before `automation:` is removed — [[TASK-0541]], `docs/features/verdict-ledger/plan/coverage-seed-your-trainer.json`, 278 checks naming 81 JVM classes, committed."
covers: []
supersedes: "[[REQ-0039-A-Covering-Test-Settles-The-Check]]"
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ISS-0198-Automation-And-Covered-By-Are-Empty-On-All-669-Checks]]", "[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]", "[[DES-0012-Tests-In-Two-Flows]]"]
tags: [requirement]
---

# Observed, not declared

## Statement

A claim that a machine covers an acceptance check **shall** be produced by a run that observed it, and **shall not** be asserted in any note's frontmatter.

## Why the inversion, and why it is available only now

A standing `covered_by:` rots **silently**: the covering test is renamed, deleted or `@Ignore`d, the note keeps asserting coverage, and the check leaves the run list permanently with no signal. A stale verdict is better than that, because a stale verdict still asks.

[[ISS-0198]] measured the standing claim and closed with the field deliberately empty on all 669 checks: the 203 annotated bodies name **54 JVM classes and no `TST-*` id**, and the guard correctly refuses a link to something no runner can execute. **That population is precisely the one observed coverage handles** — each class declares its check in its own source, the run emits, and nothing invents a note for an unrunnable command.

The inversion is only available because automation moved into the ledger. It could not have been proposed against a note field.

## The limit, carried from the ADR

[[ISS-0209]]: the acceptance gate runs in **no repo that holds a check**. Until that is resolved the emitter runs here and nowhere the data lives, and criterion 4 is proved in this repo only. That is a stated limit, not a satisfied criterion.

## Acceptance criteria

- [x] Nothing declares coverage in a note.
- [x] The test declares the check, greppably.
- [x] CI emits into the working ledger.
- [x] A deleted covering test re-arms its check, proved.
- [x] The 203 annotations survive the removal.

## Implemented 2026-08-21

All five met. The two that carry the most weight:

**Criterion 1 was not satisfied by the corpus being clean.** `covered_by:` held nothing on 671 of 671 notes ([[ISS-0198]]), so *"nothing declares coverage in a note"* was already true as a description — and the mechanism that permitted it was intact. It is gone now: the field is off `Item`, out of `settled`, out of the loader, and `note_writes.cover_check` is deleted ([[ISS-0249]]). A hand-written `covered_by:` no longer settles anything, which is what `test_a_note_can_no_longer_declare_that_a_machine_covers_it` asserts — on the mechanism, not on the corpus.

That supersedes [[REQ-0039]], whose whole subject was the standing claim.

**Criterion 4 is proved here and nowhere else.** [[ISS-0209]] is unresolved: the acceptance gate runs in no repo that holds a check. The emitter runs in `project-os-cockpit` and nowhere the fleet's data lives. That is a stated limit, exactly as this note's own *"The limit, carried from the ADR"* section says, and the criterion is ticked against what was proved rather than against what was hoped.

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

**This supersedes the first-pass verdict. The `review_response:` above is accurate** — the two emitter findings are addressed and criterion 1's blast radius really was short by two files, both now corrected and listed. **The emitter fix is over-wide, half of it is unguarded, and the blast-radius correction is itself short.**

**Finding B (high) — removing the `by` key from the invalidation set opened a new silent-rot hole, and it recurs every run.** `plan`'s `stale` set is now every `method: automated` verdict not re-observed in *this* run. Two runs on one platform that observe different subsets — the two toolchains this tool's own docstring puts in scope — therefore retract each other's verdicts forever. Constructed: a temp repo with `TST-0001` declared by a `.py` test and `TST-0002` by a `.kt` test, one platform, alternating pytest/gradle JUnit reports. At `b635c39`: run 1 `pass TST-0001`; run 2 `pass TST-0002` **+ `invalidate TST-0001 (no covering test observed)`**; run 3 `pass TST-0001` **+ `invalidate TST-0002`**; run 4 `pass TST-0002` + `invalidate TST-0001`. Seven ledger entries after four runs, growing by two per run, and at every instant one of the two checks reads as uncovered although a run observed it passing minutes earlier. The identical script against `07602db` gives **two** entries and `nothing changed` from run 3 onward. So the `by` filter was doing real work, and the fix removed it wholesale instead of separating *which machine wrote it* (correctly irrelevant) from *what this run's scope was* (load-bearing). The bug it fixed — a CI-job rename — happens once; the one it created happens on every run. `.github/workflows/observed-coverage.yml` has a single `observe` job today, so this repo does not trigger it: latent, undetected, in the flattering direction, which is the exact shape of the rot the feature exists to end.

**Finding C (medium) — the other half of the `by` removal is guarded by nothing.** The pass-dedup in `main` dropped `and standing.by == args.by` and carries a comment asserting the consequence (*"Keying on it appended one entry per CI-job rename"*). I restored that clause in a clean worktree at `b635c39` and ran the **full** suite: 2051 passed, 5 skipped, and the only two failures are worktree-path artefacts (`test_the_project_id_is_the_directory_name_by_default`, `test_the_header_measures_from_the_instant_not_the_day`). No emitter test noticed. Three of the four behaviour changes in this file are pinned — mutants restoring `verdict.by == by` in `stale`, making the `failing` branch skip non-automated verdicts, and dropping `method == "automated"` from `stale` each fail their named test — and this one is not.

**Finding E (medium) — the blast-radius correction removed one of eleven refused fields from `migrate-acceptance-checks.py`, under a reason that applies to all eleven.** The comment justifies the removal by *"this repo's validator refuses it (`LEDGER-MOVED-FIELD`)"*. The same function still emits `mark`, `verdict_date`, `verdict_reason`, `invalidated_by`, `automation`, `burden`, `evidence`, `section`, `ordinal` and `migrated_from` — ten more members of `LEDGER_MOVED_FIELDS`. What actually distinguishes `covered_by` is that this requirement removed it from the schema outright, while the other ten are refused *only in a repo that keeps ledgers* (that constant's own docstring), and that distinction is written down nowhere. A reader applying the recorded reason consistently breaks the migration for the eight un-migrated fleet repos.

### What survived refutation

- **Criterion 1 — nothing declares coverage in a note — holds.** Swept `covered_by` / `automation:` / `cover_check` across `src/`, `tools/`, `desktop/`, `docs/`, `tests/` and `.claude/`: no live reader or writer remains. Every surviving mention either refuses the field (`LEDGER_MOVED_FIELDS`), strips it (`strip-verdict-fields.py`), or is historical record. `docs/references/TESTING-MODEL.md` still documents the old mechanism at length but is properly quarantined — banner in the section's own first line, naming this requirement.
- **The observed-coverage inversion itself is correct** and the headline property is genuinely proved by execution, not argued.
- **`validate-docs.sh` is OK; `--as-committed` passes the full CI step set.** Suite here: **2055 passed, 3 skipped** against the reported 2054/4 — same 2058 collected, one environment-conditional skip differing, so the reported figure is not reproducible as stated.

## Independent review — third pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `b635c39..c9d6a82`; neither the author's reasoning trace nor either earlier reviewer's working was available to me beyond what these notes themselves record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran both earlier passes, recorded in `reviewed_by` as provenance. Every count below was re-measured from the tree and every guard re-executed against a constructed mutant. **This verdict supersedes the second pass's on this note.**

**Verdict: changes-requested.** Finding E is fixed and the claim it rests on is true: `validate_moved_verdict_fields` returns early unless `docs/releases/ledgers/` exists and holds a `*.json`, so the twelve `LEDGER_MOVED_FIELDS` really are refused only in a ledger-keeping repo, all ten fields the comment enumerates really are written by `note_text`, and `covered_by` really is the one that left the schema. The arity is right and `merged_from` is correctly in neither list. What remains is the emitter, which is this requirement's mechanism.

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
