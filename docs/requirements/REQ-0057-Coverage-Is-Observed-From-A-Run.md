---
type: "[[requirement]]"
id: REQ-0057
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
