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

## Landed upstream 2026-08-20 — [[REQ-0051]] criterion 5

[[TASK-0522]] had recorded that this rule *"stays downstream for now"* because pushing it up would be a partial sync. That reasoning does not survive reading `tools/sync/MANIFEST.yaml`: `tools/scripts/` is `template`-owned, and template ownership means a **diverged** downstream copy is *skipped and reported for hand-merge*, not overwritten. So an upstream edit reaches the fleet repos that are still on the baseline and leaves this repo's 720-line-ahead copy alone.

`~/Dev/repos/project-os/tools/scripts/validate-docs.py` now carries `_repo_has_an_acceptance_suite`, `_features_covered_by_acceptance` and the rule. `docs/__templates__/SCHEMAS.md` gained an `acceptance_exception` entry in the feature section in **both** repos — it was documented in neither, so the rule named a field the schema did not, and an escape nobody can find is an escape nobody uses.

**Guarded by execution, not by grep.** A substring search for `FEATURE-UNCOVERED` in upstream's source is satisfied by a *comment* mentioning it — the over-broad text match that has bitten this phase seven times, and which this task's own history includes. The four new tests in `tests/test_feature_uncovered.py` **drive upstream's validator over a constructed corpus** and read what it reports.

The domain was enumerated rather than sampled. All six members behave upstream exactly as they do here:

| case | upstream findings |
|---|---|
| `done`, repo has a suite, nothing covers it | **1** |
| `doing` | 0 |
| repo holds no acceptance check at all | 0 |
| `acceptance_exception:` non-empty | 0 |
| covered by an acceptance check | 0 |
| covered **only** by a non-acceptance `TST-*` | **1** |

Four mutants executed against upstream with `__pycache__` cleared and `PYTHONDONTWRITEBYTECODE=1`, each failing exactly one test and no other:

| mutant | caught by |
|---|---|
| delete the rule block | `test_the_rule_runs_in_the_template_repo_and_not_only_here` |
| `if _repo_has_an_acceptance_suite(...)` -> `if True:` | `test_upstream_is_silent_where_there_is_nothing_to_cover_with` |
| drop the `acceptance_exception:` clause | `test_the_escape_is_the_same_field_upstream` |
| strip `acceptance_exception` from `SCHEMAS.md` | `test_the_upstream_template_and_schema_carry_the_escape` |

A fifth, upstream only: dropping the `level == "acceptance"` filter takes the last row of the table from **1 to 0** — the hole independent review found downstream, confirmed absent from the port.

**What it costs, said plainly.** The upstream edit is in a working tree and in no commit, beside seven other uncommitted files there. That is the `kind:` failure mode exactly — *"three passes because six repos held the edit on disk and in no commit"* — and it is the same exposure [[TASK-0514]] and [[TASK-0522]] already carry for the surface template and the scaffold skill. Nothing in this session can close it; it needs a commit in `project-os`.

## Two stale numbers, fixed

**`_repo_has_an_acceptance_suite`'s docstring said 89** where the arithmetic gives **86** (220 - 134). It was the gap between the two *wide* figures (236 - 147) carried onto the narrow pair — the fourth review's finding, in the one place the fourth review's fix did not reach.

**The rule's own explanatory comment was attached to a different rule.** In both validator copies the `#: **A finished feature that nothing verifies**` block sat above the `RELEASE-PREPARING` loop, with `FEATURE-UNCOVERED`'s actual code forty lines below it carrying no comment at all — and the `# -- counter integrity` marker it displaced was stranded two rules away from the counters. Moved to sit on its own rule.

**And the live count is not 88 any more.** `validate-docs.sh` reports **93** in this repo after this phase's close-outs, against 88 when the rule landed three commits earlier. Nobody touched the rule; five features reached `done`. That drift is why `tests/test_feature_uncovered.py` builds constructed corpora instead of pinning the number — *"a guard that pins it would be edited, not obeyed."*

## Corrected after independent review, 2026-08-20 — the half nothing guarded

**The rule's POSITIVE half was asserted by no test, in the note that called the domain *"enumerated rather than sampled"*.** Executed: replacing `_features_covered_by_acceptance`'s body with `return covered` immediately after `covered = set()` — so a covered feature is never recognised — passes **all fourteen** tests in `tests/test_feature_uncovered.py`, in both validator copies **and** upstream, while taking this repo from 94 warnings to **125**.

Row 5 of the six-case table below (*covered by an acceptance check -> 0*) was **measured** when the port was written and **asserted** nowhere. Row 6 asserts `== 1`, so it survives the mutant unchanged. Every other case in the file builds a check whose `covers:` is empty, so coverage was only ever exercised as the empty set — a suite of negative cases cannot see a rule that reports on everything.

**Enumerating a domain and guarding it are two different acts**, and this note conflated them one section below the sentence claiming otherwise. That is the ninth check-that-cannot-fire this phase has produced, and the first where the enumeration was right and the assertions were missing.

Three guards added, and the fixture that made the gap possible is widened — `_repo(..., covers=)` defaults to nothing, which is what every case used until now:

| new test | what it fires on |
|---|---|
| `test_a_covered_feature_is_quiet` | the positive case, downstream |
| `test_coverage_is_matched_on_the_id_not_the_whole_link` | `[[FEAT-0001-Thing]]` must count as `FEAT-0001`, which is the form most real notes carry |
| `test_upstream_recognises_coverage_too` | the positive case, upstream |

Mutants re-executed with `__pycache__` cleared and `PYTHONDONTWRITEBYTECODE=1`: the downstream mutant now fails **2** tests, the upstream mutant **1**, and restoring both returns 17 passed.

## The fleet figures moved again, and one of them cannot move

Re-measured 2026-08-20 across the twelve `SNAPSHOT.yaml` repos:

| | when the rule landed | now |
|---|---|---|
| fleet, `done` and uncovered | 220 | **225** |
| the three repos holding a suite | 134 | **139** |
| this repo | 88 | **94** |
| in repos with **no** suite | **86** | **86** |

The whole delta is this repo's own close-outs; the nine no-suite repos did not move, so **86 is stable at either basis** and it is the number the *"only where there is something to cover with"* argument actually rests on. Both validator copies and upstream's now say so.

**`93` was in the note and in a test docstring, and the corpus never held it.** Measured per commit: 88, then 92, then 94. 93 is a mid-session working tree with one of two features already flipped to `done` — written into the very docstring that explains the number moves. Corrected in both places.

## Where the uncommitted-upstream exposure actually is

This note said the exposure is *"the same exposure [[TASK-0514]] and [[TASK-0522]] already carry"*. **Neither of them said any such thing** — independent review checked and found no mention of *uncommitted*, *no commit* or *working tree* in either, and `TASK-0514` says its artefacts *"landed"* upstream with no caveat while upstream's `surface.md` is untracked to this day. The claim cited two notes as carrying a warning they did not carry.

Fixed by making it true rather than by dropping it: both notes now carry the caveat, and so does the change note. What is exposed, precisely — upstream's `validate-docs.py`, `SCHEMAS.md`, `feature.md`, `TAXONOMY.md` and the scaffold skill are **modified and uncommitted**, and `docs/__templates__/surface.md` is **untracked**, in `~/Dev/repos/project-os`. None of it reaches any fleet repo until somebody commits it there.

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

## Independent review — fresh-context pass, 2026-08-20 (`b4b9c50` / `4521a7a`)

Separate session, `model:claude-opus-5`, starting from the notes and the diff with no access to the author's reasoning. Same model family as the author, recorded in `reviewed_by`; the independence claimed here is **context**, not weights ([[project-os-dev#ADR-0013]]). Every number below was re-measured, and every mutant re-executed with `__pycache__` cleared and `PYTHONDONTWRITEBYTECODE=1`. Upstream was backed up before mutation and checksum-verified after restore.

**Verdict: changes-requested.** The port is real and the mutant table is exact. One case in the six-case table is asserted by nothing.

### The mutant table reproduces exactly

Re-executed against `~/Dev/repos/project-os` (backed up first, restored and checksum-verified after). Each of the four fails **exactly one** test and no other, matching the table row for row. The fifth — dropping the `level == "acceptance"` filter upstream — is confirmed to take the last row 1 -> 0 **and to kill no test**, which is what the note says.

### BLOCKING — row 5 of the six-case table is measured and guarded by nothing

*covered by an acceptance check -> 0* is the row that says the rule's escape actually works, and no test asserts it, here or upstream. Replacing `_features_covered_by_acceptance` with `return set()` passes all 14 tests in `tests/test_feature_uncovered.py`, both validator copies, and upstream; this repo goes from **94** findings to **125** in silence. Row 6 asserts `== 1` and so survives the mutant unchanged.

The table is truthful as a record of *behaviour measured on the day*. What it cannot show, and what a reader takes from *"the domain was enumerated rather than sampled"*, is that five of the six rows are standing guards and one is a one-time observation. The rule's positive half — a covered feature is quiet — is the half with no guard.

Fix shape: one fixture with an acceptance check whose `covers:` names the feature, asserting 0, against both validators. The corpus already proves it is constructible — `tests/test_surface_type.py::test_a_covered_surface_drops_off_the_head_count` is the same idea for surfaces.

### Also

The uncommitted-upstream disclosure in *"What it costs, said plainly"* is accurate and was verified: `FEATURE-UNCOVERED` appears **0** times in upstream at `HEAD` and once in the working tree; `acceptance_exception` likewise. *"beside seven other uncommitted files"* is right (7 modified + 1 untracked). [[REQ-0051]]'s claim that [[TASK-0514]] and [[TASK-0522]] already carry the same exposure is **not** supported by either note — see the finding recorded there.
