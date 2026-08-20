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
priority: high
scope: "lifecycle"
implements: "[[FEAT-0132-Acceptance-Tests-Are-Scaffolded-By-Rule]]"
acceptance:
  - "[x] The feature scaffold emits an acceptance test note. A feature created through the documented path is never uncovered. — feature-scaffold SKILL.md step 9 emits plan/tests/TST-####-*.md as an Output rather than a conditional step; tests/test_feature_uncovered.py::test_the_scaffold_emits_a_check_by_rule_not_by_judgement"
  - "[x] The validator reports a feature at a terminal status with no test naming it in `covers:` — one finding, on the feature, at close-out. — FEATURE-UNCOVERED; tests/test_feature_uncovered.py::test_it_fires_on_a_done_feature_nothing_covers and ::test_it_is_silent_while_the_feature_is_unfinished. It WARNS rather than errors, deliberately and undated (ADR-0011 clause 3, 134 outstanding in suite-bearing repos)"
  - "[x] No per-check obligation is created and no badge counts checks (ADR-0027, ADR-0030). — one warning per FEATURE at its terminal status; ::test_a_non_acceptance_test_is_not_coverage constructs the only per-check surface and the rule still reports on the feature"
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
- [x] No per-check obligation, no check-counting badge. — one finding, on the feature, at its terminal status. `::test_it_warns_and_never_errors` also asserts the rule is absent from `PROMOTIONS`.
- [x] A permanent, once-only exception field. — `acceptance_exception:`, empty in both feature templates and now documented in both `SCHEMAS.md`; `::test_an_exception_silences_it`, `::test_the_feature_template_carries_the_escape`, `::test_the_scaffold_and_the_validator_ask_one_question`.
- [x] Upstream, for every repo. — [[TASK-0523]], 2026-08-20. Four tests **execute** upstream's validator instead of grepping it, the six-case domain is enumerated rather than sampled, and four mutants each fail exactly one test. **Caveat below.**

## Criterion 2 is satisfied by a warning, and that is on the record rather than glossed

The criterion says *"one error"*. `FEATURE-UNCOVERED` **warns**. That is not a shortfall — [[project-os-dev#ADR-0011]] clause 3 forbids promoting a rule over existing debt, and the debt is **134** terminal-and-uncovered features across the three fleet repos that hold a suite, **93** in this repo alone as of 2026-08-20. A date would either fail every build the day it arrived or be moved when it did.

The rule is deliberately absent from `PROMOTIONS`, and `::test_it_warns_and_never_errors` fails if anybody adds it. It earns a date when the number is small enough that one is a promise.

## Criterion 5 is met and carries one exposure

The rule and its escape are in `~/Dev/repos/project-os` — the validator, the feature template and `SCHEMAS.md` — and `tools/scripts/` is `template`-owned in the sync manifest, so a fleet repo still on the baseline receives it and this repo's 720-line-ahead copy is skipped for hand-merge rather than clobbered.

**The exposure: the upstream edit is in a working tree and in no commit.** That is the `kind:` failure mode the surface-template task named — *"three passes because six repos held the edit on disk and in no commit"* — and [[TASK-0514]] and [[TASK-0522]] already carry it for the surface template and the scaffold skill. Nothing in this repo can close it; it needs a commit in `project-os`.
