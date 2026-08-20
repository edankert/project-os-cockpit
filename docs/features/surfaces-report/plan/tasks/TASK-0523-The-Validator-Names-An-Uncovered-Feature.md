---
type: "[[task]]"
id: TASK-0523
aliases: ["TASK-0523"]
title: "A feature reaching a terminal status with nothing covering it is a validator error"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
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

| scope | uncovered |
|---|---|
| all twelve `SNAPSHOT.yaml` repos | **236** |
| the three that actually hold a suite | **147** |
| `project-os-cockpit` alone | **88** |

[[project-os-dev#ADR-0011]] clause 3 forbids promoting over debt. A date on 147 findings would either fail every build the day it arrived or be moved when it did — and a promotion nobody intends to honour teaches people to ignore the table, which costs more than this rule is worth. It earns a date when the number is small enough that one is a promise, and that belongs to whoever works it down. `FEATURE-UNCOVERED` is deliberately absent from `PROMOTIONS`, and a test asserts that.

### Only where there is something to cover with

Nine of the twelve repos hold no acceptance check at all — that is the 236-to-147 gap. Firing there would scold a repo for not using a mechanism it never adopted.

### The exception is what makes it honest

Without a once-only escape this is a rule people disable rather than satisfy. [[TASK-0524]] refused to write 33 exceptions it could not justify; this is where the justified ones go — *engine with no rider-facing surface*, *a phase of work*, *ships prose*. Proved end to end on the corpus: 88 → **87** with one `acceptance_exception:` added, and back to 88 when removed.

## The rule was written where its subjects are not, and reported zero

The first cut sat in the snapshot-collection loop. It measured **88** by direct count and the validator reported **0** — because retention prunes terminal features out of `SNAPSHOT.yaml`. A rule placed exactly where its population is absent.

**Then it reported zero a second time, for a different reason**: this repo carries **two byte-identical validators** — `tools/scripts/validate-docs.py`, which `validate-docs.sh` runs, and `src/project_os_cockpit/validate_docs_bundled.py`, the package's copy. The rule went into the second. Nothing in the suite noticed, because nothing asserted the two are identical.

Both are now guarded: the rule is walked over notes, and `test_the_two_validator_copies_stay_identical` fails on one byte of drift. **Two checks that could not fire, in one rule, in one sitting** — and both were caught only because the corpus had been counted first and the zero was disbelieved.

Six tests, three mutants executed: disabling the rule, dropping the exception clause, and diverging the two copies.
