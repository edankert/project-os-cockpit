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

| scope | **shipped rule** (`done`) | wide, no `deferred` | wide, with `deferred` |
|---|---|---|---|
| all twelve `SNAPSHOT.yaml` repos | **220** | 236 | 237 |
| the three that hold a suite | **134** | 147 | 148 |
| `project-os-cockpit` alone | **88** | 93 | 93 |

*(**Corrected twice.** The original read `236 / 147 / 88` — two rows measured with a wider terminal set than the rule uses, one with the rule itself, and only the last matching the code. The first correction then paired **236** with **148**, which is one row from each *wide* variant: 236 goes with 147, and 237 with 148. Three columns now, each internally consistent, with the shipped rule bolded because it is the only one the code produces. [[project-os-dev#ADR-0011]]'s argument survives at **134** — but the number is what sized the decision not to date the promotion, so it had to be right, and it took two passes to make it so.)*

[[project-os-dev#ADR-0011]] clause 3 forbids promoting over debt. A date on 134 findings would either fail every build the day it arrived or be moved when it did — and a promotion nobody intends to honour teaches people to ignore the table, which costs more than this rule is worth. It earns a date when the number is small enough that one is a promise, and that belongs to whoever works it down. `FEATURE-UNCOVERED` is deliberately absent from `PROMOTIONS`, and a test asserts that.

### Only where there is something to cover with

Nine of the twelve repos hold no acceptance check at all — that is the 220-to-134 gap under the shipped rule. Firing there would scold a repo for not using a mechanism it never adopted.

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

## Independent review — fourth pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`. Verdict: **changes-requested** (supersedes the third-pass verdict above). Re-measured or re-executed, not read.

The mixing is now named, the narrow column is primary, and the *"220-to-134 gap"* sentence is corrected. `test_a_non_acceptance_test_is_not_coverage` is a real guard: my level-filter mutant **and** a weaker variant both fail it, applied to both validator copies.

**Two things remain.**

**The wide column is internally inconsistent by one, and your 148 versus my 147 has a definite answer: neither, as paired.** Re-measured across all twelve repos:

| wide set | fleet | three suite repos |
|---|---|---|
| `superseded`/`cancelled`/… **without** `deferred` | **236** | **147** |
| …**with** `deferred` | **237** | **148** |

The table pairs **236** with **148**, which is one row from each variant. The note's own parenthetical says the wide measurement counted *"`superseded`, `cancelled` and `deferred`"* — and under that definition the fleet number is 237, not 236. So the internally consistent wide triple is `236/147/93` or `237/148/93`.

Related: line 40 still sizes the `ADR-0011` argument on *"a date on 147 findings"* while the table above it now says 148, and the number the argument should use is the narrow **134** — three figures for one quantity inside one note.

**The code comment was not corrected.** `tools/scripts/validate-docs.py:3025-3026` and its bundled twin still read *"236 … 147 … 93 of them here"*, and line 389 still says *"236 terminal features"*. That is the uncorrected wide triple sitting in the rule's own source, contradicting this note's now-primary 88.
