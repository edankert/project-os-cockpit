---
type: "[[task]]"
id: TASK-0523
aliases: ["TASK-0523"]
title: "A feature reaching a terminal status with nothing covering it is a validator error"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
parent: "[[FEAT-0132-Acceptance-Tests-Are-Scaffolded-By-Rule]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# A feature reaching a terminal status with nothing covering it is a validator error

One error, on the feature, at close-out — **not** a per-check obligation and **not** a badge that counts checks (ADR-0027, ADR-0030).

Needs the once-only exception field first, or the rule has no honest escape and becomes the thing people disable. Dated promotion per ADR-0011: warn, then error.

## Done 2026-08-20

`FEATURE-UNCOVERED`: a feature at `done` that no acceptance check covers, with `acceptance_exception:` as the escape. One finding, on the feature — not a per-check obligation and not a badge that counts checks ([[ADR-0027]], [[ADR-0030]]).

### It warns, and it is deliberately undated

The task says *"dated promotion per ADR-0011: warn, then error."* **The date is withheld, and the measurement is why.** Terminal features with no acceptance check, 2026-08-20:

| scope | uncovered, **under the shipped rule** (`status: done`) | under a wider terminal set |
|---|---|---|
| all twelve `SNAPSHOT.yaml` repos | **220** | 236 |
| the three that hold a suite | **134** | 148 |
| `project-os-cockpit` alone | **88** | 93 |

*(**Corrected after independent review.** The first version of this table read `236 / 147 / 88` — the first two measured with `superseded`, `cancelled` and `deferred` counted as terminal, the third with the rule as it actually ships, which fires on `done` alone. Three rows, two definitions, and only the last matched the code. The direction is conservative and [[project-os-dev#ADR-0011]]'s argument survives at 134, but the number is what sized the decision not to date the promotion, so it had to be the right one.)*

[[project-os-dev#ADR-0011]] clause 3 forbids promoting over debt. A date on 147 findings would either fail every build the day it arrived or be moved when it did — and a promotion nobody intends to honour teaches people to ignore the table, which costs more than this rule is worth. It earns a date when the number is small enough that one is a promise, and that belongs to whoever works it down. `FEATURE-UNCOVERED` is deliberately absent from `PROMOTIONS`, and a test asserts that.

### Only where there is something to cover with

Nine of the twelve repos hold no acceptance check at all — that is the 220-to-134 gap. Firing there would scold a repo for not using a mechanism it never adopted.

### The exception is what makes it honest

Without a once-only escape this is a rule people disable rather than satisfy. [[TASK-0524]] refused to write 33 exceptions it could not justify; this is where the justified ones go — *engine with no rider-facing surface*, *a phase of work*, *ships prose*. Proved end to end on the corpus: 88 → **87** with one `acceptance_exception:` added, and back to 88 when removed.

## The rule was written where its subjects are not, and reported zero

The first cut sat in the snapshot-collection loop. It measured **88** by direct count and the validator reported **0** — because retention prunes terminal features out of `SNAPSHOT.yaml`. A rule placed exactly where its population is absent.

**Then it reported zero a second time, for a different reason**: this repo carries **two byte-identical validators** — `tools/scripts/validate-docs.py`, which `validate-docs.sh` runs, and `src/project_os_cockpit/validate_docs_bundled.py`, the package's copy. The rule went into the second. Nothing in the suite noticed, because nothing asserted the two are identical.

Both are now guarded: the rule is walked over notes, and `test_the_two_validator_copies_stay_identical` fails on one byte of drift. **Two checks that could not fire, in one rule, in one sitting** — and both were caught only because the corpus had been counted first and the zero was disbelieved.

Six tests, three mutants executed: disabling the rule, dropping the exception clause, and diverging the two copies.

## Independent review — third pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`, reviewing `6cc7f72..HEAD`. Verdict: **changes-requested**. Every claim below was re-measured or re-executed.

The rule is well placed — walking notes rather than snapshot collections, after measuring that the snapshot version fired zero times — and two of its three guards hold under mutation: removing the `acceptance_exception:` escape fails `test_an_exception_silences_it`, and removing the suite guard fails `test_it_says_nothing_in_a_repo_with_no_suite`.

**The fleet figures were measured under a wider rule than the one shipped.** The rule fires on `status == TERMINAL["features"]`, i.e. `done` alone. Re-derived by running this repo's validator against all twelve `SNAPSHOT.yaml` repos:

| scope | note claims | rule as shipped | with terminal widened to `superseded`/`cancelled`/`obsolete`/… |
|---|---|---|---|
| all twelve repos | 236 | **220** | **236** |
| the three with a suite | 147 | **134** | **147** |
| `project-os-cockpit` | 88 | **88** | 93 |

So 236 and 147 are the *wide* measurement and 88 is the *narrow* one — the three-row table mixes two definitions, and only the row that happens to match the shipped rule is the one the rule can produce. The derived claim *"nine of the twelve hold no suite — that is the 236-to-147 gap"* is 86 under the shipped rule, not 89. And `tools/scripts/validate-docs.py:3026` says *"93 of them here"*, contradicting this note's 88 in the same commit — 93 being the wide count.

The direction is conservative (the ADR-0011 argument holds at 134 as it does at 147), so nothing unsafe follows. But the number sized the promotion decision, and it is not the rule's number.

**A third guard has a hole, and it is live.** `_features_covered_by_acceptance` filters `level == "acceptance"`. Dropping that filter — so any note's `covers:` counts as coverage — passes every targeted test (73 passed). It is not an equivalent mutant: measured, it **silences 29 of this repo's 88 findings**, a third of the rule's output, by treating a non-acceptance `TST-*` as coverage. That is the reports-silence failure mode on the rule this task added. Nothing constructs a fixture with a non-acceptance note whose `covers:` names a terminal feature.
