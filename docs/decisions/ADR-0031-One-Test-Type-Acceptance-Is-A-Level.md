---
type: "[[adr]]"
id: ADR-0031
aliases: ["ADR-0031"]
title: "One test type — an acceptance check is a `[[test]]` at `level: acceptance`, and the automation path is the reason"
status: accepted
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
decision_date: 2026-08-18
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
supersedes: "[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]"
superseded: ""
related: ["[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0028-Work-Has-Three-Phases]]", "[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]", "[[ADR-0032-The-Verification-Link-Has-One-Direction]]", "[[ISS-0195-Two-Types-Carry-One-Act]]", "[[ISS-0178-A-Test-Cannot-Be-Retired]]", "[[FEAT-0118-The-Test-Type-Absorbs-The-Check]]"]
tags: [acceptance, conventions, schema, testing]
---

# One test type, and acceptance is a level

## Status

**Accepted 2026-08-18.** The gate held for exactly as long as it was meant to: the whole phase — two ADRs, four features, seventeen tasks, four requirements — was documented and committed while this read `proposed`, and nothing migrated. Edwin's instruction is the acceptance: *"implement, test and independently review the full PHASE-035 functionality."* Given against a phase whose exit criteria name this decision, and against the measured price below, the second migration of the same corpus in two weeks included.

This is the same shape [[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]] used one day earlier, and deliberately so: an acceptance should be about something concrete and fully costed.

## Context

[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]] was accepted on 2026-08-17 and made acceptance checks first-class notes of a **sibling** type — `[[check]]`, `CHK-*` — deliberately outside every test gate. That decision was right about granularity and it delivered: 669 checks across three repos, a generated view, a sweep, and a release that can be finished.

It considered reusing the test type and rejected it by measurement, naming five collisions. **One input was not in its frame, and it is the one that matters in use.**

Edwin, 2026-08-18: *"the issue I have with the 2 different types / manual checks and automated tests is that it becomes very difficult to move a CHK to an automated test."*

Measured, the asymmetry is total and one-directional:

- **A manual `TST-*` automates in place.** Add `command:` and `tools/scripts/run-tests.py` executes it and stamps its status from the exit code ([[project-os-dev#ADR-0010]]). Same id, same inbound references, same gates, no migration. `your-trainer`'s TST-0018 documents itself taking that route.
- **A `CHK-*` cannot, at four levels.** No `command:` in `check.md`. The runner filters on `^TST-\d+` (`run-tests.py:79`), so a check is invisible to it by construction. `Suite.blocking()` is `tier in GATING_TIERS and not settled`, and `settled` is `checked or reconciled or excepted` — **`automation:` and `covered_by:` are not in the predicate**, so a check a machine fully covers still blocks until a human ticks it. And nothing writes `automation:`, `covered_by:`, `tier:` or `status: retired`; `sweep.py:346` hard-codes `covered_by: []`.

**What that costs, measured: 15 of the 60 checks currently blocking `your-trainer`'s release say in their own bodies that a machine already covers them.** A quarter of the blocking set. `CHK-0505` reads *"Difficult to reproduce on real hardware without a misbehaving trainer. Exercised via `TrainerCompatibilityTestFailureModesTest.silentMode_…` (automated.)"* — and blocks a release anyway, waiting for a person to do by hand the thing its own text says is hard to do by hand and is already automated.

A three-round independent review ([[ISS-0195-Two-Types-Carry-One-Act]]) used this same asymmetry as the **argument for** keeping the types apart. It is the defect, not the justification.

## Decision

**One type. An acceptance check is a `[[test]]` note with `level: acceptance`.**

1. **`level: acceptance` is the discriminator, and it already exists** — TAXONOMY.md has carried it since the template was written (*"`acceptance` marks user-level acceptance checks that gate releases"*). No new axis is invented; the one that was always there starts carrying the distinction.
2. **`status:` is lifecycle, `mark:` is verdict — unchanged from [[ADR-0030]] decision 2.** The test status vocabulary gains `active` and `retired`; an acceptance test rests at `active` and its verdict lives in `mark:`. Ticking never touches status.
3. **`command:` is reachable from an acceptance test, and that is the point.** Set it and the runner owns the status. `Item.settled` gains one clause — settled if the mark is settled **or** the status is `passing` — so automating a check discharges it instead of buying nothing.
4. **Ids renumber to `TST-*`.** Measured: **zero inbound `[[CHK-*]]` references exist anywhere in the fleet**, so the renumber breaks nothing. `your-trainer`'s counter goes 18 → ~597. What is lost is the prose-level tell — `TST-0400` no longer says at a glance whether it is a pytest module or a hand-walk — and `level:` is what answers that from now on. *Edwin's call, 2026-08-18, against the alternative of keeping `CHK-*` ids on the test type.*
5. **[[ADR-0030]] decisions 4, 5 and 6 are carried forward unchanged** and are **not** superseded in substance: the suite is a generated view and not a document; the frozen per-release suites never migrate; and template-owned surfaces land upstream before any note changes downstream.

## Why the five collisions dissolve

[[ADR-0030]]'s objection was not that the collisions existed — it was that avoiding them would take **exemption logic** where a sibling type avoided them **by construction**. The validator says so on the line that carries it: *"the runner-only rule and the review gate — both keyed on a status this type cannot hold — never engage. That is by construction, not by exemption logic."*

The same construction survives the merge, because an acceptance test rests at `active`:

| collision | why it does not engage |
|---|---|
| **review gate on `passing`** | `REVIEW_SETTLED_STATUSES = {"tests": ("passing",)}`. An acceptance test at `active` never reaches it. Construction, not exemption |
| **runner-only statuses ([[project-os-dev#ADR-0010]])** | `passing`/`failing` stay runner-written. An acceptance test that gains a `command:` *should* take its status from the runner — **the collision becomes the feature** |
| **status vocabulary** | 3 values → 5. `active` and `retired` both already exist elsewhere in the vocabulary, the bar `check` itself was held to — and `retired` closes [[ISS-0178-A-Test-Cannot-Be-Retired]], deferred since there was no way to retire a test |
| **the Run obligation admitting the self-re-arming population** | `_is_owed` requires `status in ("ready",)`. `active` is not in it, so 669 notes never reach a badge. [[ADR-0027]] holds untouched |
| **upstream blast radius** | Real, unchanged in kind, and handled the way [[ADR-0030]] decision 6 established: upstream first, no permanent divergence |

**The one place construction does not cover it** is the VERIFY gate, which reads a feature's `tests:` list and demands each linked test be `passing`. An acceptance test at `active` named there would fire. Today that cannot happen because features do not list checks. It is prevented by [[ADR-0032-The-Verification-Link-Has-One-Direction]], which removes that list — the two decisions are independent in principle and coupled in practice, and this is the coupling.

## Consequences

**This is the second migration of the same corpus in two weeks, and the record says so plainly.** ADR-0030 cost ~9.5 days; this is estimated at 6–8. Nobody should read this note without that sentence in it.

`git` blame does not survive a second time; provenance is preserved the same way ADR-0030 preserved it, by the record — `migrated_from:` is retained verbatim and a new `merged_from:` carries the `CHK-*` id and the pre-merge sha.

**What is bought:** a check can be automated by adding one field; a covering automated test discharges the check it covers; `retired` finally exists for both populations; one type means one schema, one template, one set of gates and one mental model, and 173 `check` sites in the renderer and seven cockpit modules stop maintaining a parallel vocabulary.

**What is risked, stated rather than discovered:** a *failing* covering test un-settles the check it covers, which puts a machine-driven population into the release gate. That is the gate and not a badge, so [[ADR-0027]] is untouched — but it is a real behaviour change and it is decided here rather than found later.

## Alternatives considered

- **Leave it (ADR-0030 as it stands).** Rejected on the measurement above: 15 blocking checks a machine already covers, and no path for any of them.
- **Give the check type its own automation path** — `command:` on checks, the runner learning a second prefix, `covered_by:` reaching the gate. Considered seriously and it is the smaller change. Rejected because it ends with two types that both have a runner, both have marks and statuses, and both gate releases — the duplication ISS-0195 measured, with the last difference removed and the two names kept.
- **Keep `CHK-*` ids on `type: test`.** Cheaper and preserves the prose-level tell. Rejected by Edwin, 2026-08-18: one type should have one id space.

## Decision record

> [!note] Accept — 2026-08-18 (user:edwin)
> *"implement, test and independently review the full PHASE-035 functionality."* — given after the phase, both ADRs and the ~6–8 day estimate were on the record. What is accepted is the whole of it: the reversal of [[ADR-0030]]'s first three decisions one day after they were accepted, the renumber into the `TST-*` space, and the behaviour change in which a failing covering test un-settles the check it covers.
