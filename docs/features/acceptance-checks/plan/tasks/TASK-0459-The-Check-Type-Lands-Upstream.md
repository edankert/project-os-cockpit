---
type: "[[task]]"
id: TASK-0459
aliases: ["TASK-0459"]
title: "The check type lands upstream — five template-owned surfaces change in ~/Dev/repos/project-os and sync down before any CHK-* note exists"
status: done
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["[[FEAT-0113-The-Check-Type-And-The-Migration]]"]
parent: "[[FEAT-0113-The-Check-Type-And-The-Migration]]"
effort: M
depends: []
blocks: []
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]"]
tests: []
---

# The check type lands upstream

Gated on [[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]] being `accepted` — this task is the first thing that happens afterwards and everything else in the phase queues behind it, because nothing here carries permanent template divergence.

## The edits, all in `~/Dev/repos/project-os`

- **TAXONOMY.md** — the `check` type; the six-value `mark:` vocabulary; `automation:` values (`full`/`partial`/`manual`); optional `burden:`. Note explicitly that `level: acceptance` on a TST stays and means something different.
- **STATUSES.md** — a `[[check]]` section: allowed `draft`/`active`/`retired`, terminal `retired`, and the load-bearing sentence: **the verdict is `mark:`, not status** — so the runner-only rule and the review gate, both keyed on status, never engage.
- **QUALITY.md** — one sentence: a `CHK-*` is not a `TST-*` and does not trigger the independent-review gate; the review of a check is the walk.
- **SCHEMAS.md** — the check's field list as [[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]] fixes it.
- **`tools/scripts/validate-docs.py`** — `ALLOWED_STATUS`, `COLLECTION_TYPE`, `METRIC_PREFIX_TYPE`, `TERMINAL` gain `check`.

Then `sync-project-os.sh` down, and the local `obligations.py` declares `"check"` as owed-nothing — **forced**, because the completeness test asserts every type is declared; the machinery makes the exemption a statement rather than an omission.

## Done when

- [ ] A `CHK-*` note with a verdict and no status change validates in a synced repo, and fires no REVIEW warning, no runner-status complaint, no obligation row.
- [ ] The sync reports zero divergence on the five files afterwards.

## The sixth surface, found by being asked (2026-08-17)

This task listed **five** template-owned surfaces and they all landed. Edwin then asked whether upstream's acceptance tests were updated, and the honest answer was *the type is upstream and the contract is not*.

**`tools/instructions/TESTING.md` was the sixth**, and it is the load-bearing one: it is what every repo reads to learn what an acceptance suite *is*, and it was byte-identical in all four repos describing a single Markdown document — scaffolded from `acceptance-tests.md`, unchecked by hand, related to `TST-*` notes by a sentence naming a file two of those repos had just deleted. The five surfaces in the list are the ones the *validator* touches. The one that tells a person what to do was not on it.

Also stale, from the same omission: `release-prep/SKILL.md` (two references) and `release-verification/SKILL.md` (one), both instructing a reader to *"Read `docs/tests/ACCEPTANCE_TESTS.md`"* — an instruction that now fails in this repo and in `your-sudoku`.

Landed in the same shape as the other five: upstream first, byte-identical downstream, no new divergence. TESTING.md gains *"Where the acceptance suite lives"* (two shapes, split by time, never both), the invalidation half of rule 3 written as an action with `invalidated_by:` and the 54-of-54 measurement that explains why it needs one, and a relationship section naming `check`/`CHK-*` and why the type boundary is load-bearing rather than tidy. The old template says of itself that it is the older form.

**`your-trainer` is deliberately not patched.** Its TESTING.md still describes a single document and that is still true there — it is the repo that has not migrated. It picks this up with its migration, from the same sync.

*The lesson is [[ISS-0006]]'s, arriving again: a rule stated in several files, most of them corrected. What is new is only that the miss was in this task's own enumeration — five files chosen because a script reads them, and the document a person reads left off.*
