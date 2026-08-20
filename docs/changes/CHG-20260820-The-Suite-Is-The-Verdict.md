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
- **New validator codes**, all three warning-first with a cutover of **2026-11-18**: `TEST-AUTOMATED-STATUS`, `TEST-AUTOMATED-EVIDENCE` and `CHECK-SUBJECT`. *(Corrected: the first two landed as day-one errors on a count taken in this repo alone. Measured across the fleet, `your-trainer` at `HEAD` carries 2, 4 and 117 respectively — so the corpus was not clean and ADR-0011 clause 3 forbids promoting over unpaid debt.)*
- **`ACCEPTANCE-STATUS` keeps its day-one error over `level: acceptance`**, where the corpus really does hold zero. The command-bearing half is `TEST-AUTOMATED-STATUS`, dated — two codes, because the two halves carry different debt.
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

## Second independent review 2026-08-20 — `changes-requested` (verdict stands)

Second pass, `model:claude-opus-5`, from the notes and the diff (`5adcbc8..fde5471`) in a session that had seen neither the authoring reasoning nor the first reviewer's. Same model family as the author and as the first reviewer; different context and different session, which is the gate ([[project-os-dev#ADR-0013]]). Every mutant below was applied and executed by this session rather than taken on report. Baseline on a clean tree: **1860 passed, 3 skipped** (the fourth skip, `test_release.py:89`, fires whenever the tree is dirty, which is why a mutated run reports 1859/4).

### The seven, verified independently

| # | claim | verdict |
| --- | --- | --- |
| 1 | `Broken command` guarded at the navigator | **holds** — deleting the routing branch fails 3 tests |
| 2 | gate delta corrected to `62 → 68` | **numbers hold, correction incomplete** — see A |
| 3 | stale `blocking_for` comment rewritten | **half done** — see C |
| 4 | `tier:` criterion corrected, [[ISS-0240]] filed | **holds, but ISS-0240 repeats the error it records** — see D |
| 5 | vocabulary guard populated | **holds** — the rename fails it, and the `_BANNED` sweep is separately non-vacuous |
| 6 | parity compares the pattern sets | **holds one-sided; the behaviour is still unexercised** — see F |
| 7 | `test_the_tiers_render` a real biconditional | **holds** |

Finding 2 reproduces exactly: `git archive HEAD docs` from `your-trainer` (`30eafbbd`) gives **62 blocking before, 68 after**, entrants `TST-0592`..`TST-0597`, and **0 acceptance checks carrying a `command:`**.

### A. The correction fixed the finding, not the class — three more numbers in this note are working-tree-only

Measured with this repo's validator against `your-trainer` at `HEAD` and at its working tree:

| code | claimed here | at `HEAD` | working tree |
| --- | --- | --- | --- |
| `TEST-AUTOMATED-EVIDENCE` | *"zero violations at landing"* | **4 errors** (`TST-0016`, `TST-0017`) | **71 errors** |
| `ACCEPTANCE-STATUS` (widened) | zero, *"errors from day one"* | **2 errors** | **2 errors** |
| `CHECK-SUBJECT` | *"44 findings all in `your-trainer`"* | **117** | 44 |

`TEST-AUTOMATED-EVIDENCE` is zero in **neither** tree of `your-trainer`; it is zero in `project-os-cockpit` and `your-sudoku` only. The `ACCEPTANCE-STATUS` pair are **new**: the pre-change validator (`5adcbc8`) reports zero on the same corpus, so the widening from `level: acceptance` to `command:` non-empty introduced them. [[PHASE-039]] exit criterion 1 is ticked `[x]` on the *"the migration left zero violations"* reading, which is true of this repo and false of the fleet — and the very next clause in this note scopes `CHECK-SUBJECT` to *"all in `your-trainer`"*, which invites the fleet-wide reading of both.

**Not live today**: `your-trainer`'s own `tools/scripts/validate-docs.py` is a copy from 2026-08-18 carrying neither code. It goes red on the next validator sync, which is a bounded and foreseeable event rather than a surprise — but the record currently predicts it will not.

The 44 figure is repeated in [[REQ-0060]] criterion 2 and in the docstring of `tests/test_automated_test_holds_no_verdict.py:212`.

### B. `missing_issue_refs` was made structurally empty by this fix, and nothing can tell

`acceptance.py:670-686` moved off `tier(2)` onto `section_of(i) == SECTION_REGRESSION and not any(r.startswith("ISS-") …)`. For a note-shape item those two clauses are **contradictory**: `section_of` returns `SECTION_REGRESSION` exactly when some ref matches `^\bISS-\d+`, which implies that ref starts with `ISS-`. Enumerated over twelve ref shapes (bare, wikilinked, lower-case, `ISS-` with no digits, id-with-title, prefixed): **zero can ever be returned.** Only the file shape — a document that exists in no migrated repo — can still yield a row.

Measured on `your-trainer` at `HEAD`: **73 → 0**, and the 73 are exactly the Tier 2 checks that now derive to `feature`. Replacing the body with `return []` passes the **entire suite** (1859 passed, 4 skipped, isolated run) — and `tests/test_tests_view.py:620` `test_every_tier_two_item_names_the_issue_that_created_it`, whose docstring quotes the `TESTING.md` rule, is its only consumer and can no longer fail.

This undoes what [[ISS-0173]] and [[PHASE-034]] were for: that check went 158-of-158 false-positive → **73 of 158 honest**, recorded as *"the check working for the first time"*. It is back to reporting nothing, by a different mechanism. The new docstring's claim — *"the derived section is the same question over a field that is still written"* — is the opposite of true, and [[ISS-0240]] repeats it as *"`blocking_for`, `missing_issue_refs` and both front doors read `section_of` instead"*.

### C. Finding 3 was fixed in one comment block; four statements in the same function still assert the tier filter

The block at `acceptance.py:648-666` was rewritten. These were not, and each says the change did not happen:

- `acceptance.py:601` — `"""Unsettled Tier 1/2 items — what stops a release.`
- `acceptance.py:623-627` — *"83 of 579 covered nothing — **74 of them Tier 3, which does not gate**"*. Measured today: all 74 derive to `feature` and therefore gate.
- `acceptance.py:629-630` — *"`blocking` is now this function **with the tiers filtered**"*.
- `acceptance.py:634-645` — the *"Lifetime, not level"* block, sitting **directly above** the line that replaced the tier filter: *"`tier` survives as the answer to how long is this test expected to live … Tier 3 … cannot sensibly hold anything open … 74 of `your-trainer`'s 83 unattributed checks are Tier 3, i.e. already retired in practice."*

Same class elsewhere: `acceptance.py:45` is an orphaned `#: Tiers that block a release. Tier 3 is a verification aid, not a requirement` with no code under it, and `cockpit.py` carries ~14 orphaned `#:` lines before `CHECKS_VIEW_ROUTE` in which *"`tier:` itself is untouched — it is still the field, still the grouping"* sits immediately above *"**Gone with `tier:`** (ADR-0039)"*.

### D. [[ISS-0240]]'s `74 rows` is itself a working-tree number

Stripping `tier:` from every acceptance note and re-loading:

| measured against | rows changing suite position | delta keys changing identity |
| --- | ---: | ---: |
| `your-trainer` working tree | **74** | 232 of 580 |
| `your-trainer` `HEAD` | **0** | 232 of 580 |

Zero, because the migration allocated ids in document order and the document is ordered by tier, so `(tier, note_id)` and `(note_id)` agree on the committed record — which `sort_items`' own docstring predicts. The `_delta_key` half holds in both trees and is the real prerequisite; the `sort_items` half is a working-tree artefact. The note filed *in response to* "you measured the wrong tree" carries the same error.

### E. The six entrants land in `Feature tests`, and that is not what [[ADR-0039]] says about those notes

All **74** of `your-trainer`'s Tier 3 checks (`covers: []`, no `command:`, `automation: manual`) derive to `SECTION_FEATURE` — standing behaviour claims, re-invalidated by every overlapping change, forever. Six of them are unsettled, and those are the six entering the gate.

ADR-0039's own measured table calls that population **68 checks, 67 of them automated**, and decision 3 keeps an automated check precisely because *"a kept check with a resolving command is self-correcting"*. These carry no command, so the derivation cannot see what the ADR asserts about them and records them as manual feature checks. Decision 4 grandfathered the 68 Tier **2** checks by ID with a dated promotion rather than *"migrated by guess"*, because reclassifying them as behaviour checks *"is the exact behaviour this decision removes"* — the 74 Tier **3** checks take that same reclassification with **no grandfather and no promotion date**, because the ADR believed they were the automated population. Decision 3 also says their `area:` values *"are repaired or emptied, **not left**"*; they were left, and [[ISS-0238]] stays open.

So *"exactly what ADR-0039 decides"* is defensible as applying the rule and is not what the ADR says about these particular notes. What the record should say is that the six enter as **feature checks**, not merely that they block.

### F. Residual gaps neither pass has closed

- **The resolver's non-Python extensions are unexercised.** Removing `swift` from all three copies at once passes the whole suite (1859 passed). The new parity test compares the pattern strings, so a one-sided edit is caught; nothing asserts that a `.swift`/`.ts`/`.tsx`/`.js`/`.mjs` command resolves at all. If that regressed, an iOS command would read `UNCHECKABLE` rather than `RESOLVES`/`BROKEN`, and `Broken command` would never fire for the iOS half of the fleet — the self-correcting property [[ADR-0039]] and [[FEAT-0138]] rest on.
- **"One predicate" is two readings.** `acceptance.section_of` uses `_ISS_REF.match(ref)`; `cockpit._covers_an_issue` uses `_ISS_IN_REF.search(str(v))` over raw frontmatter, under a docstring saying *"it must stay the same question"*. They diverge on a constructible input — `covers: ["[[FEAT-0010-Fixes-ISS-0042]]"]` is regression to one and feature to the other. Not live, because the two populations are disjoint. Changing `match` to `search` in `section_of` passes the whole suite (1859 passed).
- **[[REQ-0059]] is `status: implemented`** with a frontmatter `acceptance:` entry reading *"`tier:` is read by no code path and the tier constants are deleted"* and a Statement reading *"`tier:` **must not** be read"*, above a review paragraph in the same note saying three paths read it. The phase criterion got a `~`; the requirement did not.

### Judgement on the corrections themselves

Honest rather than cosmetic **for the thing that was corrected**: the `~` markers carry both numbers and their basis, and the table above them lets a reader arrive at `62 → 68` without knowing it in advance. What did not happen is generalising from the finding to its class — three more numbers in this same note, one exit criterion, one requirement criterion and one test docstring still carry measurements taken from 588 uncommitted files, and B is a fresh instance of the defect the whole change is about: a check that reports nothing because its predicate cannot fire.

**Recommended follow-ups**: an `ISS-*` for B (blocking — restore `missing_issue_refs` to a predicate that can return a row, and give it a test that fails when it cannot), one for A (re-measure the three validator counts against `HEAD` and correct [[PHASE-039]] criterion 1, this note and [[REQ-0060]]), one for C (the four surviving statements plus the two orphaned comment blocks), and amendments to [[ISS-0240]] for D and to this note for E.
