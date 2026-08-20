---
type: "[[feature]]"
id: FEAT-0132
aliases: ["FEAT-0132"]
title: "A feature gets its acceptance tests by rule, not by being asked — scaffolded at creation and gated at close-out"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
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

[[TASK-0524]] measured `your-trainer`: **103** features, **27** covered, **76** uncovered — *"not 75"*.

*(**Re-measured at `your-trainer`'s real HEAD `0dad8104`, 2026-08-20, after independent review flagged the basis: 102 / 28 / 74, with 32 `done`-and-uncovered.** So the emphatic *"not 75"* now resolves to *not 74* — and the **103** reproduces at no basis I can build: `git ls-tree` counts **102** feature notes at `49cf2ce9`, at `0dad8104` and in the working tree, with no duplicate ids and no id/filename mismatch. The 27 -> 28 and 76 -> 74 movement is explained — `0dad8104` is titled *"name the feature each check covers"* and adds `covers:` links. The 103 is **not explained**, and it is recorded as unreconciled rather than quietly replaced, because it is the figure that was reviewed and approved twice. The split below moves with it: 42 excepted by rule, 32 owed.)*

**43 need no per-note exception** (42 at today's HEAD), because their status already says why: 29 `backlog`, 7 `superseded`, 4 `doing`, 1 `cancelled`, 1 `deferred`, 1 `planned`. Writing *"no acceptance test — not built yet"* onto a `backlog` feature restates `status: backlog` in a second place, which is exactly what [[ADR-0009]] makes the tool's job.

**The other 33 — 32 at today's HEAD — are `done` and covered by nothing at all** — no acceptance check and, measured rather than assumed, **zero of 33** covered by a non-acceptance `TST-*` either. There is no true reason available to write: *"covered by unit tests"* is contradicted by the record, and *"internal, no rider surface"* is a judgement about code nobody here has read. So they are **named as owed** on [[TASK-0524]], as a list to argue with rather than a list to accept.

**Excepting them would have been the exact defect this phase exists to remove** — a false assurance written to silence a check, the same move as `89 executed by CI` over checks with no recorded result. The criterion offered *"backfilled or explicitly excepted"* and the honest third answer is *visible and unexplained*, which is why this is `[~]` and not `[x]`. Backfilling instead would have taken that repo's gate from **68 blocking to roughly 143 on day one**, every one of them a check nobody wrote.

## Independent review — fresh-context pass, 2026-08-20 (`b4b9c50` / `4521a7a`)

Separate session, `model:claude-opus-5`, starting from the notes and the diff with no access to the author's reasoning. Same model family as the author, recorded in `reviewed_by`; the independence claimed here is **context**, not weights ([[project-os-dev#ADR-0013]]).

**Verdict: changes-requested.** Criteria 1-3 verified by mutation. The `[~]` on criterion 4 is legitimate and well-argued. The measurement behind it is against a stale basis.

### The 43/33 split reproduces exactly — at `49cf2ce9`, not at `HEAD`

Re-derived independently over `your-trainer`, counting features and acceptance `covers:` from the commit tree:

| basis | features | covered | uncovered | `done` + uncovered | of those, covered by a non-acceptance `TST-*` |
|---|---|---|---|---|---|
| `49cf2ce9` (what the note reproduces) | 103 | 27 | **76** | **33** | **0** |
| `0dad8104` (the real `HEAD` at this commit) | 103 | 28 | **75** | **32** | 0 |

The by-status breakdown is exact at `49cf2ce9`: 29 `backlog`, 7 `superseded`, 4 `doing`, 1 `cancelled`, 1 `deferred`, 1 `planned` = **43**. And *"zero of 33"* is confirmed — no non-acceptance `TST-*` covers any of them, so *"covered by unit tests"* really would have been a false exception.

`your-trainer`'s `HEAD` was `0dad8104` (2026-08-20 20:57), fifteen minutes before this commit. So *"measured `your-trainer` at HEAD: 103 features, 27 covered, 76 uncovered — **not 75**"* is emphatic about a correction that, at the actual `HEAD`, resolves back to 75 by a different route. The numbers are right; the basis label is wrong. [[TASK-0515]] carries the same defect and the detail.

### Criterion 4's `[~]` is judged legitimate, not closure by fiat

The criterion offered *"backfilled or explicitly excepted"* and the note takes neither, on the ground that no true exception exists for the 33. That is supported by the measurement above rather than asserted: the only candidate reason a person would write is contradicted by the record. Refusing to write 33 exceptions that are not true, and naming them as owed instead, is the right call and the `[~]` states it honestly.

### Verified

- Criterion 1: `feature-scaffold/SKILL.md` is **byte-identical** upstream and downstream.
- Criterion 2: the escape mutant fails exactly `::test_an_exception_silences_it` upstream and `::test_the_escape_is_the_same_field_upstream`.
- Criterion 3: `::test_it_warns_and_never_errors` does fail if the rule is added to `PROMOTIONS`.
- One gap sits behind criterion 2, recorded on [[TASK-0523]]: *covered by an acceptance check -> 0* is asserted by no test, so `_features_covered_by_acceptance` returning the empty set passes the whole suite.
