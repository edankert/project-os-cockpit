---
type: "[[requirement]]"
id: REQ-0051
aliases: ["REQ-0051"]
title: "Acceptance coverage is produced by a rule at creation and gated at close-out, never by asking a person to remember"
status: implemented
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
priority: high
scope: "lifecycle"
implements: "[[FEAT-0132-Acceptance-Tests-Are-Scaffolded-By-Rule]]"
acceptance:
  - "[x] The feature scaffold emits an acceptance test note. A feature created through the documented path is never uncovered. — feature-scaffold SKILL.md step 9 emits plan/tests/TST-####-*.md as an Output rather than a conditional step; tests/test_feature_uncovered.py::test_the_scaffold_emits_a_check_by_rule_not_by_judgement"
  - "[x] The validator reports a feature at a terminal status with no test naming it in `covers:` — one finding, on the feature, at close-out. — FEATURE-UNCOVERED; tests/test_feature_uncovered.py::test_it_fires_on_a_done_feature_nothing_covers and ::test_it_is_silent_while_the_feature_is_unfinished. It WARNS rather than errors, deliberately and undated (ADR-0011 clause 3, 134 outstanding in suite-bearing repos)"
  - "[x] No per-check obligation is created and no badge counts checks (ADR-0027, ADR-0030). — one warning per FEATURE at its terminal status, and no code path emits per check; ::test_it_warns_and_never_errors additionally fails if the rule is ever added to PROMOTIONS. STATED NARROWLY: this is a property of the rule's shape, evidenced by the code and by every fixture reporting exactly one finding per uncovered feature, not by a test that constructs many checks and counts zero findings from them"
  - "[x] A feature that legitimately needs no acceptance test can say so once, in a field, and be quiet permanently. — acceptance_exception: on the feature, shipped empty in both feature templates and documented in both SCHEMAS.md; ::test_an_exception_silences_it, ::test_the_feature_template_carries_the_escape"
  - "[x] The rule lands upstream in project-os, not only here — it is a lifecycle rule for every repo. — landed 2026-08-20 in ~/Dev/repos/project-os; four tests DRIVE upstream's validator rather than grepping it, six-case domain enumerated, four mutants executed (TASK-0523). CAVEAT: the upstream edit is uncommitted, the same exposure TASK-0514 and TASK-0522 carry"
covers: []
related: ["[[ADR-0036-The-Sweep-Is-Withdrawn]]", "[[ADR-0027]]", "[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]"]
tags: [requirement]
---

# A rule, measured against the thing it replaces

**Criterion 4 is the lesson the sweep already taught**, and it is why this is not simply the sweep with a different trigger. The sweep's three-state `acceptance_impact:` existed precisely so *"nothing to do"* could be said once — and it was still withdrawn, because being asked at all was the cost. So the exception here must be a **field on the feature**, not a prompt: a value the scaffold can leave empty and a person fills once.

**Criterion 2 puts the gate at close-out rather than during the work.** A feature under construction legitimately has no test yet. The moment the claim changes from *"I am building this"* to *"this is done"* is the moment coverage becomes a statement about truth.

**Criterion 5 is where the sweep went wrong structurally.** It was built in `project-os-cockpit` and nowhere else, so it governed one repo's features and the other eleven carried on uncovered. `your-trainer` reached **75 of 102 features with no acceptance check** while the mechanism existed.

## Acceptance criteria

- [x] The scaffold emits a test. — `feature-scaffold` SKILL.md step 9, an **Output** rather than a conditional step; `tests/test_feature_uncovered.py::test_the_scaffold_emits_a_check_by_rule_not_by_judgement`.
- [x] The validator gates terminal features. — `FEATURE-UNCOVERED`, walked over the notes because the snapshot loop fired zero; `::test_it_fires_on_a_done_feature_nothing_covers`, with `::test_it_is_silent_while_the_feature_is_unfinished` and `::test_a_non_acceptance_test_is_not_coverage` pinning both edges. **It warns and does not error** — see below.
- [x] No per-check obligation, no check-counting badge. — one finding, on the feature, at its terminal status; `::test_it_warns_and_never_errors` also asserts the rule is absent from `PROMOTIONS`. **Stated narrowly**: the rule emits from one `report.warn` inside a loop over *features*, and no fixture produces more than one finding per uncovered feature — but no test constructs a repo with many checks and asserts zero findings *from the checks*, so this criterion rests on the code's shape rather than on a guard. The weakest of the five.
- [x] A permanent, once-only exception field. — `acceptance_exception:`, empty in both feature templates and now documented in both `SCHEMAS.md`; `::test_an_exception_silences_it`, `::test_the_feature_template_carries_the_escape`, `::test_the_scaffold_and_the_validator_ask_one_question`.
- [x] Upstream, for every repo. — [[TASK-0523]], 2026-08-20. Four tests **execute** upstream's validator instead of grepping it, the six-case domain is enumerated rather than sampled, and four mutants each fail exactly one test. **Caveat below.**

## Criterion 2 is satisfied by a warning, and that is on the record rather than glossed

The criterion says *"one error"*. `FEATURE-UNCOVERED` **warns**. That is not a shortfall — [[project-os-dev#ADR-0011]] clause 3 forbids promoting a rule over existing debt, and the debt is **139** terminal-and-uncovered features across the three fleet repos that hold a suite, **94** in this repo alone as of 2026-08-20.

*(**The figures moved and one of them was never real.** They were 220 fleet / 134 suite / 88 here when the rule landed, and are 225 / 139 / 94 now — the whole delta is this repo's own close-outs. This paragraph said **93**, which is a number the corpus has never held: measured per commit it goes 88, 92, 94, and 93 is a mid-session working tree with one of two features already flipped. Caught by independent review. **86 is the figure the argument actually rests on** — the findings that would fire in repos with no suite at all — and it does not move at either basis, because those nine repos are not changing.)* A date would either fail every build the day it arrived or be moved when it did.

The rule is deliberately absent from `PROMOTIONS`, and `::test_it_warns_and_never_errors` fails if anybody adds it. It earns a date when the number is small enough that one is a promise.

## Criterion 2's guard had a hole, and it was the positive half

Found by independent review, 2026-08-20. **Replacing `_features_covered_by_acceptance`'s body so coverage is never recognised passed all fourteen tests** — in both validator copies and upstream — while taking this repo from 94 findings to **125**. The case *"a feature covered by an acceptance check is quiet"* was measured when the rule was ported and asserted by nothing; every fixture built a check whose `covers:` was empty.

A rule that reports on everything is as useless as one that reports on nothing, and a suite made only of negative cases cannot tell them apart. Three guards added (`test_a_covered_feature_is_quiet`, `test_coverage_is_matched_on_the_id_not_the_whole_link`, `test_upstream_recognises_coverage_too`); the mutant now fails 2 downstream and 1 upstream. [[TASK-0523]] carries the detail.

## Criterion 5 is met and carries one exposure

The rule and its escape are in `~/Dev/repos/project-os` — the validator, the feature template and `SCHEMAS.md` — and `tools/scripts/` is `template`-owned in the sync manifest, so a fleet repo still on the baseline receives it and this repo's 720-line-ahead copy is skipped for hand-merge rather than clobbered.

**The exposure: the upstream edit is in a working tree and in no commit.** In `~/Dev/repos/project-os`, `validate-docs.py`, `SCHEMAS.md`, `feature.md`, `test.md`, `acceptance-tests.md`, `TAXONOMY.md` and the scaffold skill are **modified and uncommitted**, and `docs/__templates__/surface.md` is **untracked**. `sync-project-os.sh` copies from a checkout, so none of it reaches a fleet repo until somebody commits it there. That is the `kind:` failure mode the surface-template task named — *"three passes because six repos held the edit on disk and in no commit"*.

*(**This paragraph claimed [[TASK-0514]] and [[TASK-0522]] "already carry it". They did not** — independent review found no such caveat in either, and `TASK-0514` said its artefacts *"landed"* upstream while `surface.md` was untracked. Citing two notes as carrying a warning they do not carry is the same defect as citing a test that does not assert the property. Made true rather than dropped: both notes carry it now, and so does the change note.)*

## Independent review — fresh-context pass, 2026-08-20 (`b4b9c50` / `4521a7a`)

Separate session, `model:claude-opus-5`, starting from the notes and the diff with no access to the author's reasoning. Same model family as the author, recorded in `reviewed_by`; the independence claimed here is **context**, not weights ([[project-os-dev#ADR-0013]]). Every number below was re-measured, and every mutant re-executed with `__pycache__` cleared and `PYTHONDONTWRITEBYTECODE=1`. Upstream was backed up before mutation and checksum-verified after restore.

**Verdict: changes-requested.** Four findings. Criteria 1-4 and the whole upstream port hold up under attack; what does not is a number, a basis, and one unguarded case.

### 1. BLOCKING — the coverage half of the rule is guarded by nothing

`_features_covered_by_acceptance` can be replaced by `return set()` — coverage never counts — and **all 14 tests in `tests/test_feature_uncovered.py` pass**, in this repo's validator, in the bundled copy, and upstream. `tests/test_tests_view.py` (101 tests) passes too. This repo's finding count goes **94 to 125** in silence.

The reason is that case 5 of the six-case domain — *covered by an acceptance check -> 0* — is asserted by **no test anywhere**. Every other case has one: `::test_it_fires_on_a_done_feature_nothing_covers` (case 1), `::test_it_is_silent_while_the_feature_is_unfinished` (2), `::test_it_says_nothing_in_a_repo_with_no_suite` (3), `::test_an_exception_silences_it` (4), `::test_a_non_acceptance_test_is_not_coverage` (6). Case 6 asserts `== 1`, so it survives the mutant unchanged.

This is the shape the phase keeps naming: the rule's *positive* behaviour — that a properly covered feature is quiet — is measured in [[TASK-0523]]'s table and pinned by nothing. Criterion 2 cites two tests that both survive it.

### 2. BLOCKING — `93` is a number this corpus never held

*"**93** in this repo alone as of 2026-08-20"* (above), and `tests/test_feature_uncovered.py`'s module docstring: *"It was 88 when this rule landed and is **93** three commits later."* Measured per commit by materialising each with `git archive` and running that commit's own validator:

| commit | `FEATURE-UNCOVERED` |
|---|---|
| `cc90468` (rule lands) through `b41c5be` | **88**, then **92** from `c697546` |
| `b4b9c50` (this commit) | **94** |
| `4521a7a` (HEAD) | **94** |

`b4b9c50` itself moves it 92 -> 94, because it sets [[FEAT-0130]] and [[FEAT-0132]] to `done` and neither is covered or excepted. 93 sits between the two and is what a mid-session working tree reads with one of the two already flipped — a working-tree figure reported as the repo's state, which is [[ISS-0240]]'s subject.

### 3. The fleet pair 220/134 is correct against a stale basis, and the basis is not stated

Re-measured across the twelve `SNAPSHOT.yaml`-bearing repos: **225** fleet-wide and **139** in the three suite-bearing repos, against the 220/134 stated. The pair reconstructs *exactly* with this repo at **88** and `your-trainer` at **33** — both figures already superseded when the commit was written (this repo was 92, `your-trainer` 32 at its own HEAD).

**The `86` correction is right and survives the drift**, which is worth saying plainly: it is the nine no-suite repos summed (1+7+3+0+20+0+17+33+5), and they did not move. 220-134 = 86 and 225-139 = 86. The corrected docstring figure is basis-independent even though the endpoints it is derived from are not.

Confirmed unchanged: **three** repos hold a suite, **nine** hold none.

### 4. The two notes cited as already carrying the uncommitted exposure do not carry it

*"[[TASK-0514]] and [[TASK-0522]] already carry it for the surface template and the scaffold skill."* [[TASK-0522]] contains no occurrence of *uncommitted*, *no commit*, *working tree* or *untracked*. [[TASK-0514]] quotes the `kind:` lesson (*"six repos held the edit on disk and in no commit"*) as a reason for its ordering, then states that its own artefacts *"landed in `~/Dev/repos/project-os`"* — with no caveat. Upstream's `docs/__templates__/surface.md` is in fact **untracked**.

So the exposure is disclosed in exactly two places — here and on [[TASK-0523]] — and the sentence that spreads the responsibility to two other notes is not supported by them.

### What survived every attempt to refute it

- **All four upstream mutants fire, each failing exactly one test and no other**, precisely as [[TASK-0523]]'s table claims: delete the rule -> `::test_the_rule_runs_in_the_template_repo_and_not_only_here`; `if True:` -> `::test_upstream_is_silent_where_there_is_nothing_to_cover_with`; drop the exception clause -> `::test_the_escape_is_the_same_field_upstream`; strip the field from `SCHEMAS.md` -> `::test_the_upstream_template_and_schema_carry_the_escape`.
- **The six-case domain behaves identically upstream and downstream.** Enumerated independently against both validators: 1/0/0/0/0/1 on both. The fifth mutant (dropping the `level` filter upstream) kills **no** test, as the note says — it is a measurement, not a guard.
- Criterion 5's *"landed upstream"* is exercised by execution rather than grep, and the disclosure of the uncommitted state is prominent and honest.
- The `template`-ownership argument that reversed [[TASK-0522]] is quoted verbatim from `tools/sync/MANIFEST.yaml` and is correct.
- Both validator copies are byte-identical (`46bccd54…`), at HEAD and in the working tree.
- `feature-scaffold/SKILL.md` is byte-identical upstream; the `SCHEMAS.md` entry is identical in both repos.
