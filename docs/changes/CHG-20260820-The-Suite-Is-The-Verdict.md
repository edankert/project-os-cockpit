---
type: "[[change]]"
id: CHG-20260820
aliases: ["CHG-20260820"]
title: "An automated test records no verdict, `tier:` is gone, and the Tests view is six derived sections"
status: active
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
related: ["[[ADR-0038-The-Suite-Is-The-Verdict]]", "[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[FEAT-0139-The-Suite-Is-The-Verdict]]", "[[FEAT-0140-Sections-Are-Derived-Not-Filed]]", "[[FEAT-0141-The-Contract-Says-It-Upstream]]", "[[ISS-0237-An-Automated-Check-Still-Blocks-The-Manual-Walk]]", "[[ISS-0238-There-Is-Nowhere-To-Put-An-Automated-Check]]", "[[ISS-0239-The-Runner-Stamps-Failing-On-A-Missing-Device]]"]
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
tags: [change, testing, schema]
---

# The suite is the verdict

## What changed

**A test note that declares a `command:` records that a machine executes it, and nothing about whether it passed.** CI is the verdict. A manual test is unchanged and still records one, because nothing else knows how a person's check went.

**`tier:` is read by no code path.** A check's section is computed: a non-empty `command:` is *Automated tests*, else a `covers:` naming an `ISS-*` is *Regression tests*, else *Feature tests*.

**The Tests view is six sections**, every one derived: `Needs you`, `Feature tests`, `Regression tests`, `Automated tests`, `Broken command`, `Retired`. The eight verdict-state groups are gone.

## Behaviour a reader will notice

| | before | after |
| --- | --- | --- |
| `your-trainer` release gate | see the correction below | **62 → 68 at `HEAD`**; 68 → 59 in its working tree |
| This repo's automated tests | 37 in one collapsed `Verified` group | `Automated tests`, with their commands |
| An automated check on the generated page | a checkbox and a completed fraction | the command, and *"executed by CI"* |
| A regression check after an overlapping change | re-opened | **completed once, and stays completed** |
| `run-tests.py --write` | wrote `status`, `last_run`, `exit_code`, `updated` | writes nothing; `--write` is accepted and inert |
| Recording a run from the cockpit on an automated note | stamped it | **refused**, with the reason |

## Paths and contracts

- **`tools/instructions/TESTING.md` and `STATUSES.md` are rewritten upstream** in `~/Dev/repos/project-os` and synced to all 12 project-os repos. Instruction files only; no downstream note was migrated by that commit.
- **New validator codes**: `TEST-AUTOMATED-EVIDENCE` (error, zero violations at landing) and `CHECK-SUBJECT` (warning, cutover **2026-11-18**, 44 findings all in `your-trainer`).
- **`ACCEPTANCE-STATUS` widens** from `level: acceptance` to `command:` non-empty — 89 notes to 139.
- **New module** `command_targets.py`, mirrored inside the bundled validator because that file ships stdlib-only to every repo. A parity test asserts the copies agree, and that the two validator files stay byte-identical — which nothing had ever enforced.
- **38 notes in this repo** lost `status: passing`, `last_run:` and `exit_code:`; `tools/scripts/migrate-automated-verdicts.py` is re-runnable per repo and refuses to report success unless its after-census is clean.

## What did not change

- The 582 ledger-tracked acceptance checks: [[ADR-0037]] already moved their verdicts.
- Manual tests, and the staleness clock on them.
- `tier:` in the notes. It stops being read; **removing it from 671 notes is a later, separate migration**, so a bad derivation stays recoverable.
- `run` in the documents. Edwin, 2026-08-19: leave it there, keep it out of the UI.

## Known gaps, stated rather than discovered

- **67 checks still read `area: "Moved from Tier 1 / Tier 2 — Fully Automated"`** — a heading from a deleted document. [[ISS-0238]] stays open for it.
- **`Broken command` has no members anywhere** — 134 of 139 commands resolve, 5 name nothing checkable, none are broken. Proved on constructed input, with the mutant executed, because the corpus cannot prove it.
- **Invalidation narrowing is equally unprovable from the corpus**: zero checks in the fleet carry an invalidation. Same treatment.
- **[[ISS-0209]] is untouched**: the acceptance gate executes in no repo holding a check, so *"CI is green"* guarantees nothing in `your-trainer`, and none of this should be read as evidence that its 91 automated tests pass.

## Independent review 2026-08-20 — `changes-requested`

Reviewed by `model:claude-opus-5` from the notes and the diff (`264e7e1..936eb64`, plus `project-os@89b5bde` and the fleet-sync commits), in a session that had never seen the authoring reasoning. Same model family as the author, different context and different session — which is the gate ([[project-os-dev#ADR-0013]]), and it is recorded here so a reader can judge the independence rather than infer it.

Baseline before any mutation: **1854 passed, 4 skipped**.

**What held.** Five source mutations were applied and executed. `command_targets._exists` forced to `True` → 7 failures. The invalidation narrowing (`section_of(self) != SECTION_FEATURE`) deleted → 3 failures in `tests/test_invalidation_scope.py`. A status write sneaked back into `run-tests.py` through `open().write()`, evading the `"write_text" not in SCRIPT` string guard → 3 failures on byte-identity. `section_of`'s unclassifiable default flipped to `automated` → 26 failures. `_FILE_SHAPE_SECTIONS[3]` flipped to `feature` → 15 failures including `test_tier_three_never_gates`. The fail-safe direction is guarded, the runner guard is structural *and* behavioural, and the fleet sync is real — all 12 repos carry byte-identical `TESTING.md` and `STATUSES.md`, all committed.

**Finding 1 — `Broken command` is unguarded in the product.** Replacing `cockpit.py:4178-4181` with an unconditional `buckets["automated"].append(record)` — deleting the section entirely — passes the whole suite: **1854 passed, 4 skipped**. `tests/test_command_targets.py` guards `command_targets.resolve` in isolation; nothing asserts the navigator ever routes a broken command anywhere. The wiring does work (a constructed two-note corpus yields `broken-command | Broken command | ['TST-0002'] | needs_human=True`), so this is a missing guard rather than a broken feature — but the exit criterion *"deleting a covering test puts its check back on the list — proved on constructed input"* is not met by what was written. What is proved is that a function returns `BROKEN`. The validator's use at `validate_docs_bundled.py:2264` is unguarded the same way.

**Finding 2 — the gate delta was measured against uncommitted state in another repo, and the committed record moves the other way.** `68 → 59` reproduces *exactly*, same nine ids, against `your-trainer`'s **working tree**. Against `your-trainer`'s **committed `HEAD`** (`git archive HEAD docs`) the same code gives **62 → 68**: nothing leaves, and six checks *enter* — `TST-0592`…`TST-0597`. **Zero acceptance checks carry a `command:` at `HEAD`**; the nine automated checks the whole [[ISS-0237]] argument rests on live only in 588 uncommitted files under `your-trainer/docs/tests`, which the close-out commit itself describes as *"none of them mine"*. The six entrants are precisely the case `acceptance.blocking()`'s own comment says was tried on 2026-08-18 and **reverted**, because *"blocking them is not failing closed — it is a NEW and tighter gate, which is a decision for a person and not a tidy-up at the end of a session."* This change enacts that tightening, unmeasured and unreported. Either the basis of the measurement is stated in this note and in [[PHASE-039]], or the delta is re-measured against the committed record and the `+6` is put to Edwin.

**Finding 3 — the comment that recorded the constraint is now false.** `acceptance.blocking()` (`src/project_os_cockpit/acceptance.py:625-660`) still describes a tier filter — *"`tier` survives as the answer to how long is this test expected to live"*, *"The tier filter above runs BEFORE the fail-closed clause below"*, *"Measured: 74 of `your-trainer`'s 83 unattributed checks are Tier 3"*. There is no tier filter. It was the only written record of [[ISS-0208]]'s blind spot, and it now tells an auditor the blind spot is still in place when the change removed it.

**Finding 4 — *"`tier:` is read by no code path"* is false, and the deferred migration is not safe.** Three live readers of `Item.tier` on note-shape items: `acceptance.sort_items` (`acceptance.py:999-1001`) — canonical suite order is `(tier, note_id)`; `acceptance._delta_key` (`acceptance.py:1236`) — the release delta's row identity; and `migrate-acceptance-checks.py`'s `_gated` (`and i.tier != 3`). Simulated the announced follow-up by stripping `tier:` from `your-trainer`'s 582 check notes: **74 rows change suite position** and **232 of 579 delta keys change identity**, so those rows would read as removed-and-new across a release tag — the exact "a migration showing up as regressions" failure `test_the_delta_reads_both_shapes_at_their_own_refs` exists to prevent. "Left in place and ignored, so a bad derivation is recoverable" is true of the derivation and not of the ordering.

**Finding 5 — the vocabulary guard is vacuous over the two labels this phase introduced.** Changing `("needs-you", "Needs you")` to `("needs-you", "Needs a run")` at `cockpit.py:4196` passes `tests/test_ui_vocabulary.py` (6 passed). Both `needs-you` and `broken-command` are empty in this repo, empty groups are dropped, and neither label ever reaches a payload — so `test_the_group_that_asks_is_called_needs_you` asserts over a set that cannot contain the string it forbids. [[ADR-0039]] decision 5, the one rename the decision makes, is unguarded. The parametrized test's vacuity guard is per-payload; it needs to be per-group, or the corpus needs a fixture holding both.

**Finding 6 — the resolver parity test misses five of the six extensions it claims.** Dropping `swift` from `_CMD_SOURCE_PATH` in **both** validator copies while leaving `command_targets._SOURCE_PATH` alone passes `tests/test_command_target_parity.py` (5 passed): `CASES` covers only `.py` and JVM classes, and no fleet command names a `.ts/.tsx/.js/.mjs/.swift` path, so the corpus half cannot reach them either. Latent rather than live — the byte-identity assertion catches the one-sided edit, which is the likelier accident — but the guard is narrower than its docstring claims.

**Finding 7 — `test_the_tiers_render_in_the_tests_view` was left half-converted.** `tests/test_tests_view.py:726` is dead code (`extra = [...] if False else []`), and `:728` `assert present is bool(checks) or present` cannot fail when `present` is true, so the biconditional its own comment states — *"A section is on the view when it HOLDS something"* — is not asserted; the residual bite duplicates the two lines below it. No live defect: `test_an_empty_group_is_absent_rather_than_zero` still covers the property.

**Minor, not blocking.** `_FILE_SHAPE_SECTIONS.get(item.tier, SECTION_FEATURE)` — `_TIER_HEADING_RE` accepts any single digit, so a `# Tier 4` heading reaches the default. The direction is the safe one (it blocks) and nothing asserts it; a one-line parametrize would close it.

**Not stamped individually:** the 38 `TST-*` notes that lost `status`/`last_run`/`exit_code`. Their change is a field removal executed by a re-runnable migration whose after-census is asserted; the reviewable claim is [[REQ-0058]]'s, and it is stamped there. Recording a separate verdict on each would be provenance theatre.

## Corrected 2026-08-20 after independent review

**The gate delta was measured against `your-trainer`'s WORKING TREE, and the committed record moves the other way.**

| measured against | before | after |
| --- | --- | --- |
| working tree (588 uncommitted files) | 68 | **59** — the nine automated checks leave |
| `HEAD`, i.e. what a fresh clone has | 62 | **68** — six Tier 3 checks *enter* |

**At `HEAD`, zero acceptance checks in `your-trainer` carry a `command:`.** All 89 live only in uncommitted work, so nothing leaves the gate there today. What does happen is the other half of the same rule: `TST-0592`..`TST-0597` are Tier 3, carry no command, and are therefore manual and owed — exactly what [[ADR-0039]] decides, and exactly what `blocking()`'s own comment described on 2026-08-18 as *"a NEW and tighter gate, which is a decision for a person"*. It is that person's decision now; the comment has been corrected to say so.

Both numbers are true of what they measure. Only one of them is true of what ships.
