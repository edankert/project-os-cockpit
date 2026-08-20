---
type: "[[feature]]"
id: FEAT-0132
aliases: ["FEAT-0132"]
title: "A feature gets its acceptance tests by rule, not by being asked — scaffolded at creation and gated at close-out"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
requirements: ["[[REQ-0051-Coverage-Is-A-Rule-Not-A-Request]]"]
tasks: ["[[TASK-0522-Scaffold-Acceptance-Tests-With-The-Feature]]", "[[TASK-0523-The-Validator-Names-An-Uncovered-Feature]]", "[[TASK-0524-Backfill-Your-Trainers-Seventy-Five]]"]
related: ["[[ADR-0036-The-Sweep-Is-Withdrawn]]", "[[DES-0012-Tests-In-Two-Flows]]", "[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]"]
tags: [feature]
---

# The rule, not the request

Edwin, correcting the withdrawal: *"On the sweep … I expected you to automate creating acceptance tests for each feature, a project-os rule, not a manual step."*

**I read the instruction too narrowly.** [[ADR-0036]] withdrew the *asking* — an obligation that nagged a feature to describe its own impact — and that withdrawal stands. What it did not do is supply the thing that should have been there instead. Removing the ask without adding the rule leaves coverage to whoever remembers.

## The measurement that settles it

`your-trainer`: **75 of 102 features carry no acceptance check at all.** The sweep existed for eighteen months of project time and coverage reached 27%. A mechanism that asks a person at close-out is a mechanism that produces the coverage of whoever was paying attention that day.

## The shape

**At creation** — `feature-scaffold` emits a Tier 1 acceptance test alongside `FEAT-*` and `PLAN.md`, the way it already emits the plan. A feature arrives with the question *"how would somebody tell this works?"* already having a home, rather than a hole nobody sees.

**At close-out** — the validator names a feature reaching a terminal status with no test covering it. Not a nag while it is being built; a gate at the moment the claim *"this is done"* is made.

**Not a badge.** [[ADR-0027]] and [[ADR-0030]] both bear here: this must not become a per-check obligation, and it must not count checks. One error at one moment, on the feature.

## Where the tier fits

The scaffolded test is **Tier 1** by construction — TESTING.md: *"created when a feature is first implemented … one or more tests per feature."* That is the tier's own definition being performed rather than described.

## Acceptance

- [x] Creating a feature creates at least one acceptance test note for it. — [[TASK-0522]]; `feature-scaffold` SKILL.md step 9 emits `plan/tests/TST-####-*.md` as an **Output**, not a conditional step, and the skill is byte-identical upstream. `tests/test_feature_uncovered.py::test_the_scaffold_emits_a_check_by_rule_not_by_judgement`.
- [x] A feature cannot reach a terminal status with nothing covering it, or the departure is recorded. — [[TASK-0523]]; `FEATURE-UNCOVERED` warns on a `done` feature with no acceptance check, and the departure is `acceptance_exception:`. `tests/test_feature_uncovered.py::test_it_fires_on_a_done_feature_nothing_covers`, `::test_an_exception_silences_it`. **It warns rather than errors** — [[REQ-0051]] carries why, and the debt that sized it.
- [x] No per-check obligation and no badge counts checks. — one finding, on the feature, at its terminal status. `::test_it_warns_and_never_errors` also fails if the rule is ever added to `PROMOTIONS`; `::test_a_non_acceptance_test_is_not_coverage` proves the rule reads acceptance coverage rather than counting tests.
- [~] `your-trainer`'s 75 uncovered features are backfilled or explicitly excepted. — **Reconciled: 43 of the 76 are excepted by rule and 33 are named as owed, because no true exception exists for them.** See below. The 33 are a judgement only Edwin can make.

## Closed 2026-08-20 — the rule exists in both places it has to

The two ends now ask one question. The scaffold **emits or excepts** at creation, when whoever is making the feature knows why; `FEATURE-UNCOVERED` warns at close-out for anything that is neither. A test asserts they name the same field, because a skill and a validator disagreeing about it is the shape [[REQ-0059]] had across two artefacts.

**And it is a lifecycle rule rather than this repo's habit.** Both halves are in `~/Dev/repos/project-os` as of 2026-08-20 — the scaffold skill, the feature template, `SCHEMAS.md`, and the validator rule itself. [[TASK-0522]]'s reason for keeping the rule downstream (*"pushing one rule up would be a partial sync"*) did not survive reading the sync manifest: `template` ownership **skips** a diverged downstream copy rather than clobbering it. Both notes carry the correction.

### Criterion 4, reconciled — and refusing to write the exceptions was the point

[[TASK-0524]] measured `your-trainer` at HEAD: **103** features, **27** covered, **76** uncovered — not 75.

**43 need no per-note exception**, because their status already says why: 29 `backlog`, 7 `superseded`, 4 `doing`, 1 `cancelled`, 1 `deferred`, 1 `planned`. Writing *"no acceptance test — not built yet"* onto a `backlog` feature restates `status: backlog` in a second place, which is exactly what [[ADR-0009]] makes the tool's job.

**The other 33 are `done` and covered by nothing at all** — no acceptance check and, measured rather than assumed, **zero of 33** covered by a non-acceptance `TST-*` either. There is no true reason available to write: *"covered by unit tests"* is contradicted by the record, and *"internal, no rider surface"* is a judgement about code nobody here has read. So they are **named as owed** on [[TASK-0524]], as a list to argue with rather than a list to accept.

**Excepting them would have been the exact defect this phase exists to remove** — a false assurance written to silence a check, the same move as `89 executed by CI` over checks with no recorded result. The criterion offered *"backfilled or explicitly excepted"* and the honest third answer is *visible and unexplained*, which is why this is `[~]` and not `[x]`. Backfilling instead would have taken that repo's gate from **68 blocking to roughly 143 on day one**, every one of them a check nobody wrote.
