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
review_verdict: approved
tags: [change, testing, schema]
---

# The suite is the verdict

## What changed

**A test note that declares a `command:` records that a machine executes it, and nothing about whether it passed.** CI is the verdict. A manual test is unchanged and still records one, because nothing else knows how a person's check went.

**No section and no gate decision reads `tier:`.** A check's section is computed: a non-empty `command:` is *Automated tests*, else a `covers:` naming an `ISS-*` is *Regression tests*, else *Feature tests*. *(This line said "read by no code path" until the fourth review; `sort_items`, `_delta_key`, `Suite.tier` and the migration script still read it — [[ISS-0240]].)*

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

## Third independent review 2026-08-20 — `changes-requested`

Third pass, `model:claude-opus-5`, from the notes and the diff (`936eb64..72e2038`) in a session that had seen neither the authoring reasoning nor either reviewer's. Same model family as the author and both prior reviewers; different context and different session, which is the gate ([[project-os-dev#ADR-0013]]) — what is independent here is the context, not the weights, and that is recorded so a reader can judge it rather than infer it. Every mutant below was applied and executed by this session. Every count was measured by this session against `git archive HEAD` copies of the fleet repos, never their working trees. Baseline on a clean tree: **1861 passed, 3 skipped**; `validate-docs.sh` OK.

### The six second-pass findings, verified independently

| # | claim | verdict |
| --- | --- | --- |
| A / B2 | the widened rule split into two codes, both dated | **partly** — the union is preserved and both codes warn, but the split is cut on `level:` rather than on `command:`, and three of the four places carrying the wrong count were not corrected. See A1/A2 |
| B / B1 | `missing_issue_refs` is a predicate that can fire | **holds** — `return []` now fails `test_every_tier_two_item_names_the_issue_that_created_it`; **117** at `your-trainer`'s `HEAD`, **44** in its working tree, **0** here, and both figures equal `CHECK-SUBJECT`'s on the same tree |
| C / B3 | stale tier prose and orphaned comments corrected | **partly** — 4 of 6. See C1 |
| D / B4 | [[ISS-0240]]'s numbers restated at both bases | **holds in the body** — reproduced exactly: **0** rows move at `HEAD`, **232** delta keys change identity. The title still carries the retracted figure. See D1 |
| E / B5 | [[ADR-0039]] carries a dated correction at both bases | **holds** — the table is exact: working tree 349/164/68 with 89 commands (17/5/67), `HEAD` 349/158/74 with **0**. The `Feature tests` half of the finding is recorded as a criticism, not as a statement of what the notes now are |
| F / B6 | `_covers_an_issue` delegates to `section_of` | **holds** — restoring its own regex fails `test_the_navigator_and_the_page_classify_a_note_identically`. Two caveats in F1 |

**The first pass's seven were re-checked and all seven fixes are still intact.** Deleting the `Broken command` routing at `cockpit.py:4217` fails 3 tests (`test_a_broken_command_routes_to_its_own_section`, `test_the_broken_section_asks_for_a_person`, `test_every_section_label_carries_no_verb`). Renaming `Needs you` to `Needs a run` fails the vocabulary guard. Dropping `swift` from both validator copies fails both parity parametrisations. `test_the_tiers_render_in_the_tests_view` carries no dead code and a real biconditional; forcing empty groups to render fails `test_an_empty_group_is_absent_rather_than_zero`. `62 → 68` reproduces exactly at `your-trainer`'s `HEAD` (581 items through the index, entrants `TST-0592`..`TST-0597`), against **62** from the pre-change tree at `5adcbc8` on the same corpus. [[ISS-0240]] exists. The fleet sync is real: 12 repos, `TESTING.md` sha1 `0a8b0cd4` and `STATUSES.md` sha1 `a0c9d5da` in every one, none dirty.

### A1. The split is cut on `level:`, not on `command:`, so 64% of the widened domain still errors on day one

The stated rationale is *"`ACCEPTANCE-STATUS` keeps its day-one error over `level: acceptance` … The command-bearing half is `TEST-AUTOMATED-STATUS`, dated"*. The code (`validate_docs_bundled.py:2424-2438`) branches `if level == "acceptance"` **first**, so a note that is *both* reaches `ACCEPTANCE-STATUS` and never `TEST-AUTOMATED-STATUS`. Constructed and executed, one note carrying `level: acceptance`, `command:` and `status: passing`:

| validator | result |
| --- | --- |
| pre-change (`5adcbc8`) | *silent* — `passing`/`failing` were exempt with a `command:`, deliberately, because the runner owned the status |
| current | `ERROR [ACCEPTANCE-STATUS]`, no cutover |

So the newly-widened behaviour — removing the runner exemption — lands as a **day-one error** for exactly the population ADR-0038 is about, while the identical situation on a note without `level: acceptance` merely warns until 2026-11-18. This file's own module docstring measures that population: *"89 of the fleet's 139 automated notes: 64% of the domain"*. Zero today at every fleet `HEAD` and in every working tree, so ADR-0011 clause 3 is not breached **yet** — but `your-trainer` carries 89 such notes in uncommitted work, and every other fleet repo still ships the old `run-tests.py` that stamps `status:` (measured: 5 `fm_set` sites in `your-trainer`, `your-health`, `project-os-dev` and `project-os`; 0 here). One `run-tests.py` run after the next validator sync makes it non-empty and red, with no cutover to absorb it. That is the same argument the author accepted for the other half.

Secondary: the `ACCEPTANCE-STATUS` message now cites only `(ADR-0031)`. An auditor who hits it on an automated acceptance check is pointed at the decision that did not cause it.

### A2. *"`CHECK-SUBJECT` is 117 not 44"* was not corrected in three of the four places the second pass enumerated

Measured this session — `CHECK-SUBJECT` against `your-trainer`: **117** at `HEAD`, **44** in its working tree. Still carrying the working-tree figure with no basis:

- `src/project_os_cockpit/validate_docs_bundled.py:866` and `tools/scripts/validate-docs.py:866` — *"44 findings at introduction, ALL in `your-trainer` … 12 name nothing at all and 32 name only a `PHASE-*` or a `TASK-*`"*. This is the comment that justifies dating the code, sitting six lines above the block added to correct the same class of error.
- `tests/test_automated_test_holds_no_verdict.py:230` — *"Measured 2026-08-20: 44 checks in `your-trainer`"*. Named explicitly by the second pass.
- [[REQ-0060]] criterion 2 — *"the checkable population is **44**"*, still with no `HEAD` figure, seventeen lines above that note's own review paragraph saying *"reports **117**, not 44"*. The note contradicts itself within one screen.

Three more statements in the same test file were left asserting the pre-fix behaviour: the module docstring at `:15` (*"Landed at **zero violations**, so it errors from day one rather than taking a warning tier"*), `:89` (*"The half that was already law, unchanged — 89 notes' worth"* — for those 89 it is precisely **not** unchanged, per A1), and `:129` (*"Why this errors on day one instead of warning"*).

And the new `PROMOTIONS` comment at `:875` claims *"Measured at introduction against every repo rather than against the authoring one"* while citing `your-trainer` and `project-os-cockpit` only. Measured across all 12 repos at `HEAD` this session:

| code | your-trainer | project-os-dev | your-health | fleet total |
| --- | ---: | ---: | ---: | ---: |
| `TEST-AUTOMATED-STATUS` | 2 | 4 | 6 | **12** |
| `TEST-AUTOMATED-EVIDENCE` | 4 | 8 | 12 | **24** |
| `ACCEPTANCE-STATUS` | 0 | 0 | 0 | **0** |

The debt is 6× what the comment records, and two repos are unmentioned. The `ACCEPTANCE-STATUS` row is the one that matters and it is genuinely clean everywhere, which is what makes A1 a hazard rather than a breach. This is the third consecutive pass at which a claim of fleet-wide measurement rests on two repos.

### C1. Two of the six stale-tier items are untouched, including a docstring's first line

- `acceptance.py:599` — `blocking()`'s **summary line** still reads *"Unsettled Tier 1/2 items — what stops a release."* It is the first of the four statements finding C enumerated, it is the line an IDE tooltip and `help()` show, and the body of the same docstring now explains at length that there are no tiers.
- `cockpit.py:4302-4327` — the orphaned `#:` block is unchanged. It still opens *"Which suite tiers a checked box is 'done' for"* over no code, and `:4319` *"`tier:` itself is untouched — it is still the field, still the grouping, still what [[ISS-0208]] is about"* still sits two lines above `:4322` *"**Gone with `tier:`** (ADR-0039)"*.

The four rewritten blocks are good and one of them (`blocking_for`'s loop) carries the corrected `62 -> 68` measurement, which reproduces.

### D1. [[ISS-0240]]'s title still asserts the number its body retracts

The body is correct and reproduces exactly. The title is still *"removing the field would move 74 rows and change 232 of 579 delta identities"* — the 74 is the working-tree figure the body withdraws, and a title is what a reader sees in a list, a backlink and a search result. The body also says *"232 of 580"* where the title says 579; the suite holds **579** items at `HEAD` (580 files, one of them `README.md`), so the title is right and the body is off by one, inside the note whose subject is measuring against the right thing.

### F1. The delegation is correct at its one call site and answers a different question everywhere else

Two things a later reader should not have to rediscover:

- **`fm["level"] = "acceptance"` at `cockpit.py:4038` is inert.** `acceptance.item_from_note` never reads `level:` — it returns `None` on a missing `id` and on nothing else. The line reads as a precondition being enforced and enforces nothing.
- **The function's name and docstring no longer match its answer.** It asks *"Does this test verify a past defect?"* and now returns *"is this in the Regression section"*, and `section_of` puts `command:` first. Measured across the fleet: three notes in **this** repo — `TST-0017` (covers `ISS-0007`), `TST-0019` (`ISS-0023`), `TST-0022` (`ISS-0062`/`ISS-0063`) — do verify a past defect and now get `False`, plus five in `your-trainer`. Harmless today only because `_tests_groups` routes every command-bearing record to `automated`/`broken-command` before line 4191 is reached. A second caller inherits a silent `False` for every automated regression test. Renaming it, or asserting the precondition, closes it; the parity guard does not, because it compares the two readings rather than the question.

### G1. [[REQ-0059]] still asserts as implemented the thing the record says is false

Unchanged from the second pass's finding F: `status: implemented`, frontmatter `acceptance:` carrying *"`tier:` is read by no code path and the tier constants are deleted"*, criterion 2 ticked `[x]`, and a Statement reading *"`tier:` **must not** be read"* — above a review paragraph in the same note listing three readers, and beside [[PHASE-039]], whose identical criterion carries a `~`. Two notes describing one fact, disagreeing.

### G2. The record is navigable from the phase note and not from here

Asked directly, because three passes of corrections have layered onto four notes. A reader who starts at [[PHASE-039]] arrives correctly: the `~` markers carry both bases, *"Reviewed twice, and what the second pass changed"* states the regression plainly, and the two review sections are dated and attributed. [[ADR-0039]]'s correction section is the best of them — it states the wrong basis, gives both tables, and says why the decision is unchanged anyway.

A reader who starts **here**, at the change note — the durable record of what the repo now does — does not. This note ends on the second pass's *"Recommended follow-ups: an `ISS-*` for B (blocking) …"*, and there is no section after it saying what was done. No such `ISS-*` was filed (the issue counter is still at 0240), which is defensible because B was fixed in code instead — but nothing here says so. Section B still reads *"`missing_issue_refs` was made structurally empty by this fix, and nothing can tell"* in the present tense, of a function that has been fixed and now has a non-vacuous guard. The correction pattern the first pass established — a *"Corrected … after independent review"* section — was not repeated for the second.

**What would fix it**, and it is one section rather than a rewrite: a *"Corrected 2026-08-20 after the second independent review"* section here, listing the six with what changed and what did not, in the shape the first correction already uses. The `~`-and-both-bases habit is working; it just has not reached the note a reader lands on first.

### Verdict

`changes-requested`. B1, B4, B5 and B6 are genuinely fixed and their mutants fail — that is four of six, verified by execution rather than on report, and the first pass's seven are all still intact. B2 and B3 are partly done, and B2's remainder is not only prose: A1 is a live rule that errors on day one over the majority of its own domain, contrary to the reasoning the fix was written from. A2, C1, D1 and G1 are each a claim that is still wider than what the code or the corpus supports, which is the failure mode this phase exists to remove.

**Suggested follow-ups**: one `ISS-*` for A1 (decide whether the runner exemption's removal is dated like its sibling or errors deliberately, and say which in the message); one for A2 + C1 + D1 + G1 as a single sweep of the surviving wrong-basis statements, since they are one class and are now enumerated with line numbers; and the correction section described in G2, which is close-out rather than an issue.

---

# Corrected after the third independent review, 2026-08-20

**Three passes, all `changes-requested`, eighteen findings.** Everything above this line is the record of what each pass found; this section is what was done about the second and third. Read this first if you want the current state — the sections above are evidence, not status.

## The one that mattered

**The split of `ACCEPTANCE-STATUS` was cut on the wrong axis.** The second pass's fix put the command-bearing half behind a dated cutover, and the third pass found the branch tested `level == "acceptance"` first — so a note that is *both* an acceptance check and command-bearing never reached the dated code. That is **89 of the fleet's 139 automated notes**, erroring on day one over a rule they had no chance to satisfy, in repos that still ship the `run-tests.py` which writes those very statuses.

It is now cut on **what ADR-0038 newly forbids**, which is the honest line:

| note | before ADR-0038 | now |
| --- | --- | --- |
| `level: acceptance`, no command, any of the three | error | `ACCEPTANCE-STATUS`, error — unchanged |
| `level: acceptance`, command, at `ready` | error | `ACCEPTANCE-STATUS`, error — unchanged |
| command-bearing at `passing`/`failing`, any level | **allowed** | `TEST-AUTOMATED-STATUS`, warns to 2026-11-18 |

`ready` deliberately does not inherit the cutover: it was already forbidden with a command, because `ready` is what the `Run` obligation counts. Guarded as a matrix in `tests/test_automated_test_holds_no_verdict.py`.

## The rest

- **The `44` that should have been `117`** is corrected in all four places the third pass named — both validator copies, the test docstring, and REQ-0060's scope and criterion. The quotes of it in the review sections above are left standing as evidence of what was found.
- **The promotion comment now carries a fleet measurement rather than a claim of one**: `TEST-AUTOMATED-STATUS` 12 (your-trainer 2, project-os-dev 4, your-health 6), `TEST-AUTOMATED-EVIDENCE` 24 (4/8/12), `ACCEPTANCE-STATUS` **0 everywhere** — which is precisely why that code keeps its day-one error.
- **The last two stale tier statements** are gone: `blocking()`'s summary line, and the `cockpit.py` block whose *"`tier:` itself is untouched"* sat two lines above *"Gone with `tier:`"*.
- **REQ-0059 no longer asserts what the record contradicts.** Its criterion said *"`tier:` is read by no code path"* and was marked `implemented` over four live readers; it now says *no section or gate decision reads it*, which is what was built, with [[ISS-0240]] carrying the rest.
- **`_covers_an_issue`** dropped an inert `fm["level"] = "acceptance"` and states the narrower question it actually answers.

## What is still open, deliberately

[[ISS-0238]] (67 areas naming a deleted document's heading), [[ISS-0240]] (`sort_items`/`_delta_key` read `tier:`; the strip changes 232 of 580 delta keys), and [[ISS-0209]], which bounds what any of this proves: **the acceptance gate executes in no repo that holds a check**.

## Fourth independent review 2026-08-20 — `changes-requested`

Fourth pass, `model:claude-opus-5`, fresh context: a session that had seen neither the authoring reasoning nor any of the three prior reviewers'. Same model family as the author and all three prior passes, recorded in `reviewed_by` as provenance ([[project-os-dev#ADR-0013]]) — what is independent here is the **context and the session**, not the weights. Every mutant below was applied and executed by this session; every fleet count was measured by this session against `git archive HEAD` copies, never a working tree. Baseline on a clean tree: **1868 passed, 3 skipped**; `validate-docs.sh` OK.

### The third pass's five, verified independently

| # | claim | verdict |
| --- | --- | --- |
| 1 | the split is recut on what ADR-0038 newly forbids | **incomplete — a case now falls to silence.** See H1 |
| 2 | `44` → `117` in all four places | **holds** — 117 reproduced at `your-trainer`'s `HEAD` (44 in its working tree); the surviving `44`s are review-section quotes. One stale decomposition, H3 |
| 3 | the `PROMOTIONS` comment carries a real fleet measurement | **holds exactly** — re-measured at every fleet `HEAD`: `TEST-AUTOMATED-STATUS` **12** (your-trainer 2, project-os-dev 4, your-health 6), `TEST-AUTOMATED-EVIDENCE` **24** (4/8/12), `ACCEPTANCE-STATUS` **0** everywhere |
| 4 | the last two stale tier statements are gone | **holds** — `blocking()`'s summary line reads *"Unsettled MANUAL checks"*, and the `cockpit.py` block no longer contradicts itself two lines apart |
| 5 | REQ-0059 narrowed to what was built | **holds in [[REQ-0059]]** — Statement, criterion `~` and frontmatter `acceptance:` all corrected. Not propagated to this note, H5 |

**The earlier thirteen are intact**, each re-mutated and re-executed by this session: `missing_issue_refs` → `return []` fails `test_every_tier_two_item_names_the_issue_that_created_it`; deleting the `Broken command` routing fails `test_a_broken_command_routes_to_its_own_section` and `test_the_broken_section_asks_for_a_person`; renaming `Needs you` → `Needs a run` fails `test_every_section_label_carries_no_verb`; dropping `swift` from both validator copies fails both parity parametrisations; restoring `_covers_an_issue`'s own regex fails `test_the_navigator_and_the_page_classify_a_note_identically` — still failing after the `fm["level"]` removal, so that removal did not weaken the guard. `fm["level"] = "acceptance"` is confirmed inert: `item_from_note` reads `id`, `tier`, `mark` and `invalidated_by`, and never `level`. The new six-case matrix is non-vacuous: reverting the split to its `level`-first form fails two of its parametrisations.

### H1 — the recut drops a case to silence, and that case was reported one commit ago (blocking)

Enumerated the full cross-product against the validator rather than against the table — `level` ∈ {`acceptance`, absent, `integration`} × `command` ∈ {present, absent} × `status` ∈ {`ready`, `passing`, `failing`, `active`}, 24 cells executed. Twenty-three land where the note says. One does not:

| cell | pre-ADR-0038 (`5adcbc8`) | second pass (`72e2038`) | **current (`5671bcc`)** |
| --- | --- | --- | --- |
| command-bearing, **not** `level: acceptance`, at `ready` | *silent* | `WARN [TEST-AUTOMATED-STATUS]` | **silent** |

`newly_forbidden = automated and status in TEST_RUNNER_STATUSES` is `False` for `ready`, and the `elif level == "acceptance"` that follows does not catch a note without that level — so the cell falls out of both branches. [[ADR-0038]]'s Rule is *"a test note that declares a `command:` never holds `ready`, `passing` or `failing`"* over a domain of *"every `TST-*` note whose `command:` is non-empty"*, and this file's own comment sixty lines above says *"the same three statuses are forbidden on both populations, and the rule finally covers the domain it always described."* For `ready` it does not: it covers the `level: acceptance` half only, which is the pre-ADR-0038 domain. The widening is implemented for two of its three statuses.

[[REQ-0058]] criterion 1 is ticked `[x]` — *"the forbidden-status check ranges over `command:` non-empty, not over `level: acceptance` — domain went 89 → 139 notes"* — and for `ready` that is the claim H1 refutes.

**The six-case matrix omits exactly this cell.** It covers (`acceptance`, cmd, `passing`/`failing`), (none, cmd, `passing`), (`acceptance`, cmd, `ready`), (`acceptance`, no cmd, `passing`/`ready`). The seventh case — (none, cmd, `ready`) — is the one that changed, and nothing asserts it in either direction: extending `newly_forbidden` to cover it passes `tests/test_automated_test_holds_no_verdict.py` and `tests/test_tests_view.py` unchanged (104 passed), so the silence is unguarded rather than deliberate.

**Population and severity.** Zero at every fleet `HEAD` today: 50 command-bearing notes fleet-wide (this repo 38, project-os-dev 4, your-health 6, your-trainer 2), **none** of them at `ready`. So this is latent, not live — which is precisely the standing the third pass's A1 had when it was filed blocking, and the direction is the worse one: A1 was a rule biting too hard, this is a rule not biting at all. The `Run` obligation is not affected (`obligations._is_owed` filters test notes through `_is_manual_test`, so a command-bearing note never reaches the badge); the gap is in the validator, which is the conformance mechanism ADR-0038 names.

The prose asserts the closed reading in three places, and each is true only of the `level: acceptance` half: this note's correction table row *"`level: acceptance`, command, at `ready` → error, unchanged"* with the surrounding sentence *"`ready` deliberately does not inherit the cutover: it was already forbidden with a command"* (it was not, without that level); the validator comment's *"What errored before ADR-0038, and still errors on day one"* bullets; and `test_ready_with_a_command_was_already_forbidden_and_still_errors`, whose name generalises past the `level: acceptance` fixture it actually builds.

### H2 — [[ISS-0240]]'s title regressed from the right number to the wrong one (blocking)

The third pass's D1 said, in terms: *"the title is right and the body is off by one"* — title `579`, body `580`, and **579 is right**. The title now reads **`232 of 580`**, and the body still reads `232 of 580`. The correction adopted the number the review identified as wrong.

Measured this session against `your-trainer` at `HEAD`, through this repo's own `acceptance.load`: the suite holds **579** items; stripping `tier:` changes **232** delta identities out of **578** distinct keys; **0** rows change suite position (the body's other figures reproduce exactly). `docs/tests/acceptance/` holds **580** files at `HEAD`, one of them `README.md`. So `580` is a *file* count standing where a *check* count belongs — in the title of the note whose entire subject is measuring against the right basis, and in a list, a backlink and a search result. The `74` was correctly dropped.

### H3 — [[REQ-0060]] criterion 2 keeps the retracted number's decomposition (non-blocking)

The headline is corrected to `117`, and 117 reproduces. The clause after it does not: *"12 naming nothing and 32 naming only a `PHASE-*`/`TASK-*`"* sums to **44**, the working-tree figure the same sentence withdraws. Measured at `your-trainer`'s `HEAD`: **85** name nothing and **32** name only provenance. Both validator copies and the test docstring dropped the breakdown rather than restating it, which is why this survives in one place only.

### H4 — three docstrings the third pass enumerated still assert the day-one erroring (non-blocking)

Named in this phase's own transcription of that pass — *"three docstrings in `tests/test_automated_test_holds_no_verdict.py` (`:15`, `:89`, `:129`) still assert the day-one erroring the fix removed"* — and unchanged: `:15` *"Landed at **zero violations**, so it errors from day one rather than taking a warning tier"*, `:104` *"The half that was already law, unchanged — 89 notes' worth"* (those 89 are command-bearing and no longer take this code at `passing`/`failing`), and `:144` *"Why this errors on day one instead of warning"*. They contradict `:277` in the same file, which asserts the opposite and passes: *"the fleet corpus is not clean, so neither may error on day one."* Not claimed as fixed anywhere, and not carried forward as open either.

### H5 — the correction reached [[REQ-0059]] and not this note's own summary (non-blocking)

Line 24, under **What changed**, still reads *"**`tier:` is read by no code path.**"* — the exact sentence REQ-0059 retracted this round — and line 51 repeats *"It stops being read"*. The closing section correctly says REQ-0059 now says *no section or gate decision reads it*, 270 lines below. A cold reader who takes the change note's summary at face value gets the retracted claim; the third pass's G1 was *"two notes describing one fact, disagreeing"*, and after this round the two notes are [[REQ-0059]] and this one.

### H6 — *"89 of the fleet's 139"* is a working-tree figure carried without its basis (non-blocking)

Measured this session: at every fleet `HEAD`, **zero** notes are both `level: acceptance` and command-bearing — the 89 exist only in `your-trainer`'s uncommitted work, where 89 of its 91 automated notes carry that level. The figure appears unqualified in the validator comment at `validate-docs.py:2432`, in `tests/test_automated_test_holds_no_verdict.py:306` and in this note's correction section, while the `PROMOTIONS` comment 1,560 lines above declares *"Measured at HEAD across every repo carrying a test note"*. It is not load-bearing — the dating rests on the 12/24/0 counts, which are correct — and [[ADR-0038]] does record 139 as a dated 2026-08-19 domain measurement. It is flagged because it is the class three passes have corrected, appearing again beside a claim of `HEAD` measurement.

### Verdict

`changes-requested`. **Three of the third pass's five are fully fixed and one of the remaining two is fixed where it was filed** — the `117` correction, the fleet measurement and the stale tier prose all hold under independent re-measurement, REQ-0059 is honestly narrowed, and the thirteen earlier findings survive re-mutation with no sign that this round disturbed them. The recut is also right in shape: cutting on *what ADR-0038 newly forbids* rather than on `level:` is the correct line, and its matrix is not vacuous.

It does not pass because the recut is **incomplete in the direction that is hardest to notice**. A case that the previous commit reported now reports nothing, no test can tell, and the note, the code comment and a test name all describe the closed reading. That is the third consecutive round in which fixing the previous round's findings introduced a new defect, and the second in which the new defect is *a check that cannot fire* — the failure mode this phase exists to remove. H2 is smaller but the same shape: a review said which of two numbers was right, and the number the review rejected is the one that landed.

**Suggested follow-ups**: extend `newly_forbidden` to the whole of `ACCEPTANCE_FORBIDDEN_STATUSES` for command-bearing notes that are not `level: acceptance` (or state in the code why `ready` is deliberately exempt there, and mark [[REQ-0058]] criterion 1 `~` to match), and add the seventh row to the matrix so the cell is asserted either way; correct [[ISS-0240]]'s title and body to `579` (or `578` distinct keys, stating which); repair REQ-0060's decomposition to 85/32; and fold H4, H5 and H6 into one sweep, since they are one class and are enumerated here with line numbers.

---

# Corrected after the fourth independent review, 2026-08-20

**Four passes, all `changes-requested`, twenty-three findings.** *(Superseded — the current state is the sixth-pass section at the end of this note.)*

## The blocking one, and it was mine again

**Recutting the split, I dropped a case to silence.** `newly_forbidden = automated and status in TEST_RUNNER_STATUSES` excludes `ready`, and the `elif level == "acceptance"` beneath it does not catch a note that is command-bearing but *not* an acceptance check — so **command + `ready` + no level reported nothing at all**, where the previous commit had warned. Third round running in which the new defect is a check that cannot fire.

The clause is now `automated and (status in TEST_RUNNER_STATUSES or level != "acceptance")`, which is *(the rule after ADR-0038) minus (the rule before)* stated exactly. **The six-case sample is replaced by the whole 16-cell cross-product** — level present/absent × command present/absent × four statuses — written out rather than computed, so a rule change must edit the expectation it breaks.

## The denominator, settled rather than picked

ISS-0240's row count was reported as 579, then 580, then 578. All three counted something real: 580 `.md` files in `docs/tests/acceptance/`, 579 of them checks once `README.md` is excluded, and **581** — the population `acceptance.load` actually returns, because two acceptance-level notes live in `docs/tests/` rather than the acceptance directory. 581 is the number the code operates on.

**The `232` figure was withdrawn here, and that withdrawal was wrong** — see the fifth-pass section below. It reproduces exactly: 232 change, 349 do not, because `item_from_note` defaults an absent `tier:` to 1.

## The rest

- **`REQ-0060`'s breakdown** said 12 + 32, which sums to the withdrawn 44. At HEAD it is **85 naming nothing, 32 naming only provenance**.
- **Three test docstrings** still asserted day-one erroring, contradicting the file's own later assertion. The module docstring now carries the fleet figures instead of this repo's.
- **`CHG` line 24** still said *"`tier:` is read by no code path"* — the claim REQ-0059 retracted a round earlier, 270 lines above its own correction.
- **"89 of 139" now carries its basis**: that is `your-trainer`'s working tree; at every fleet HEAD it is 0. Latent, not live — but every repo except this one still ships the `run-tests.py` that writes those statuses.

## Still open, deliberately

[[ISS-0238]], [[ISS-0240]], and [[ISS-0209]] — which remains the boundary on all of it: **the acceptance gate executes in no repo that holds a check.**

## Fifth independent review 2026-08-20 — `changes-requested`, one finding

Fifth pass, `model:claude-opus-5`, fresh context: a session that had seen neither the authoring reasoning nor any of the four prior reviewers'. Same model family as the author and every prior pass, recorded in `reviewed_by` as provenance ([[project-os-dev#ADR-0013]]) — what is independent is the **context and the session**, not the weights, and this session has no memory of authoring any of it. Every cell, mutant and count below was executed here; fleet counts were taken from `git archive HEAD` copies, never a working tree. Baseline on a clean tree: **1878 passed, 3 skipped**; `validate-docs.sh` OK.

### H1 is fixed, and the matrix is right in every cell

The clause `automated and (status in TEST_RUNNER_STATUSES or level != "acceptance")` was checked against the validator rather than against `_SPLIT_MATRIX`: all 16 cells executed on constructed repos, and **all 16 agree with the table, code and severity**. The `ready` cell that fell silent now warns. Four extra levels were executed to look for a cell the table cannot see — `integration`, `unit`, `Acceptance`, `ACCEPTANCE` — and every one lands with its case-folded equivalent, so two level values are sufficient to cover the predicate.

Five mutants, each applied and executed: restoring `automated and status in TEST_RUNNER_STATUSES` fails exactly the dropped cell (`[-True-ready-…]`); `newly_forbidden = automated` and `level == "acceptance"` both fail `test_ready_with_a_command_was_already_forbidden_and_still_errors` by downgrading a day-one error to a warning; `and` for `or` fails the `acceptance`/`passing` cell; `newly_forbidden = False` fails the widening outright. **No surviving mutant.**

### The other four fourth-pass findings, re-measured

| # | claim | verdict |
| --- | --- | --- |
| H3 | `REQ-0060` breakdown is 85/32 | **holds exactly** — at `your-trainer`'s `HEAD`, `CHECK-SUBJECT` is **117** = 85 naming nothing (83 `covers: []` + 2 with no `covers:`) + 32 naming only provenance (17 `PHASE-*`, 15 `TASK-*`) |
| H4 | the module docstring carries fleet figures | **holds exactly** — this repo's validator run against `git archive HEAD` of every fleet repo gives `TEST-AUTOMATED-STATUS` **12** (2/4/6), `TEST-AUTOMATED-EVIDENCE` **24** (4/8/12), `CHECK-SUBJECT` **117** (your-trainer only), `ACCEPTANCE-STATUS` **0** everywhere |
| H5 | line 24 corrected | **holds** — it now carries the retraction inline and names [[ISS-0240]] |
| H6 | `89 of 139` carries its basis | **holds** — 89 `level: acceptance` command-bearing notes in `your-trainer`'s working tree, **0** at every fleet `HEAD`. The `139` denominator is now **137** on today's trees (this repo 37, your-trainer 91, your-health 6, project-os-dev 3); it is dated 2026-08-19, so it is stale rather than wrong |

The five earlier fixes re-mutated here still bite: `missing_issue_refs` → `return []` fails `test_every_tier_two_item_names_the_issue_that_created_it`; deleting the `Broken command` routing fails two tests in `test_command_targets.py`; `Needs you` → `Needs a run` fails `test_every_section_label_carries_no_verb`; a one-sided edit to either validator copy fails `test_the_two_validator_files_are_byte_identical`.

### The finding — the `232` withdrawal (blocking)

**232 reproduces on the first reading, and the claim that replaced it is false.** `item_from_note` defaults an absent `tier:` to **1** (`acceptance.py:917-922`), so stripping the field changes only the non-Tier-1 keys: measured by rewriting all 581 notes in a copy of `HEAD` and diffing `_delta_key` per `note_id`, **232 keys change and 349 do not** — and 232 again at `HEAD` through the directory-only load (of 579) and again in the working tree (of 581). It is the count of Tier 2 + Tier 3 checks, which is why it is basis-independent and why three passes each measured it.

[[ISS-0240]] line 33 now says the strip *"changes the value of every one of the 581 keys"* and that *"a delta … matches nothing: every check reads as removed and newly added"*; the title says *"changes every delta key"*. Both are false for the 349 Tier 1 rows. The `2` collisions the withdrawal rests on are a correct measurement of a **different** operation — dropping `tier` from `_delta_key`, which is step 2 of that note's *Done when*, not the strip the paragraph describes. So a true number was removed on the strength of a measurement that was not of the same thing, and an untrue one put in its place, in the note whose subject is measuring against the right basis. Same class as the four preceding rounds, this time in prose rather than in a predicate.

Two smaller notes, neither blocking. The cross-product comment at `tests/test_automated_test_holds_no_verdict.py:293-295` says *"all 24 (three of the statuses plus `active`, at both levels, with and without a command)"* — the parenthetical enumerates 16; **24** is right for the fourth pass's own run, which used three level values. And this round's commit message reports `1877 passed` where a clean run here gives **1878**.

### On the layering, asked directly

A cold reader can reach the true state, but only through this note: [[PHASE-039]] and all three `FEAT-*` notes end on the fourth pass's findings with no marker that they were fixed, and each points here, where *"# Corrected after the fourth independent review"* says plainly *"This is the current state; everything above is evidence."* That convention works and is not a finding. The cheap improvement, if a sixth round happens, is one line at the head of each satellite review section — *"fixed, see CHG § Corrected after the Nth"* — so the pointer is not the only thing carrying it.

### Verdict

`changes-requested`, on one finding, and everything else has converged. The code is right: the widened rule now covers its stated domain, its cross-product is complete and non-vacuous, no mutant survives, and every count in the record that this pass could re-measure reproduces exactly. The remaining work is a paragraph — restore *"232 of 581 delta keys change, 349 do not, because a missing `tier:` reads as Tier 1"* to [[ISS-0240]]'s title and body, and to the *Denominator* section above. With that edit the record is true as it stands.

---

# Corrected after the fifth independent review, 2026-08-20

**Five passes. The fifth found one thing, and it was the fix I made to the fourth.** *(Superseded — see the sixth-pass section below.)*

**`232` is restored.** I withdrew it as unreproducible; it reproduces on the first reading. `item_from_note` defaults an absent or unreadable `tier:` to **1** (`acceptance.py:921`), so stripping the field from the notes leaves every Tier 1 key untouched and moves the rest: **232 change, 349 do not**, and the 232 are exactly the Tier 2 and Tier 3 checks. That is why it is basis-independent, and why three separate passes each measured the same number.

**What I actually measured was a different operation** — dropping `tier` from the *key function*, which makes 2 items collide — and I reported it as though it measured stripping the field from the *notes*. The claim I substituted, *"all 581 keys change"*, is false for 349 rows. In the note whose entire subject is measuring against the right basis.

The lesson is the one this phase keeps paying for: **a number I could not reproduce meant my measurement was wrong, not the number.** Withdrawing it looked like the conservative move and destroyed a true, three-times-confirmed finding.

Everything else in the fourth-pass round was verified and holds: all 16 cells of the split matrix match on code and severity under independent enumeration, five mutants against the clause all fail, `CHECK-SUBJECT` is 117 = 85 + 32 exactly, and the fleet figures (12 / 24 / 0) reproduce.

## Still open, deliberately

[[ISS-0238]], [[ISS-0240]] — now carrying the right number — and [[ISS-0209]], which remains the boundary on all of it: **the acceptance gate executes in no repo that holds a check.**

## Sixth independent review 2026-08-20 — `approved`

Sixth pass, `model:claude-opus-5`, fresh context: a session that had seen neither the authoring reasoning nor any of the five prior reviewers'. Same model family as the author and every prior pass, recorded in `reviewed_by` as provenance ([[project-os-dev#ADR-0013]]) — what is independent is the **context and the session**, not the weights, and this session has no memory of authoring any of it. Every mutant below was applied and executed here; every fleet count was taken from `git archive HEAD` copies, never a working tree. Baseline on a clean tree: **1878 passed, 3 skipped**; `validate-docs.sh` OK; the working tree was left byte-identical.

**The section above this one — *Corrected after the fifth independent review* — is the current state, and it is approved.**

### The fifth pass's finding is fixed, and this pass could not shake the restored number

Re-measured from scratch, without reference to how the author or the fifth pass measured it: `git archive HEAD` of `your-trainer` into two throwaway trees, `^tier:.*$` deleted from every `.md` file in one of them, `_delta_key` diffed per `note_id`.

| what was checked | result |
| --- | --- |
| files carrying `tier:` at `HEAD` | **581**, and they are exactly the 579 in `docs/tests/acceptance/` plus the 2 in `docs/tests/` — no other note type carries the field |
| indexed load (581 items) | **232** keys change, **349** do not |
| directory-only load (579 items) | **232** keys change, **347** do not |
| composition at `HEAD` | Tier 2 **158** + Tier 3 **74** = 232; the 349 unchanged are all Tier 1 |
| composition in the working tree | Tier 2 **164** + Tier 3 **68** = **232**, Tier 1 **349** — different composition, same total, which is what basis-independent means here |
| cause | `item_from_note` normalises any tier outside `(1, 2, 3)` — absent, unreadable, out of range — to **1** (`acceptance.py:918-922`) |
| suite position | **0** rows move on either load path, confirming the figure the note now omits |

**One claim was tested harder than the note states it.** *"Those 232 rows would read as removed and newly added"* would be an overstatement if a stripped row landed on a key the baseline already held, in which case it would match rather than appear new. Checked: **0 of the 232** collide with a baseline key. The suite's one duplicate key, `(1, "import not gated by tier")`, is a Tier 1 pair present identically before and after the strip. So the sentence is exact.

The rest of [[ISS-0240]] holds: 580 files, 579 once `README.md` is excluded, 581 through `acceptance.load(docs, index)`; the baseline-side asymmetry is real (`_notes_at` `ls-tree`s `docs/tests/acceptance/` only, `acceptance.py:1392`); `test_the_delta_reads_both_shapes_at_their_own_refs` exists at `tests/test_check_migration.py:274`; the withdrawal is recorded as withdrawn in both this note and that one. The `all 24` docstring now reads `= 16 cells`, and `_SPLIT_MATRIX` does hold 16.

### Everything the fifth pass verified, re-proved here independently

| guard | mutant applied | result |
| --- | --- | --- |
| the split clause | `newly_forbidden = automated and status in TEST_RUNNER_STATUSES` | fails **exactly one** cell, `[-True-ready-TEST-AUTOMATED-STATUS-WARN]` — the case that had fallen silent |
| `missing_issue_refs` | body replaced with `return []` | fails `test_every_tier_two_item_names_the_issue_that_created_it` |
| `Broken command` routing | bucket assignment and label both deleted | fails `test_a_broken_command_routes_to_its_own_section` and `test_the_broken_section_asks_for_a_person` |
| vocabulary | `Needs you` → `Needs a run` | fails `test_every_section_label_carries_no_verb` |
| validator parity | one-sided append to `tools/scripts/validate-docs.py` | fails `test_the_two_validator_files_are_byte_identical` |

No mutant survived. Every count in the record that could be re-measured reproduces exactly: `CHECK-SUBJECT` **117** at `your-trainer@HEAD` = **85** naming nothing (83 carrying `covers: []`, 2 carrying no `covers:`) + **32** naming only provenance (17 `PHASE-*`, 15 `TASK-*`); `TEST-AUTOMATED-STATUS` **12** (`your-trainer` 2, `project-os-dev` 4, `your-health` 6); `TEST-AUTOMATED-EVIDENCE` **24** (4 / 8 / 12); `ACCEPTANCE-STATUS` **0** in every repo; `project-os-cockpit` zero of all three, as the `PROMOTIONS` comment says.

### Two non-blocking items — the record describing itself, not the system

Both were introduced by this round, and neither makes a claim about the code false.

1. **[[ISS-0240]]'s `Suite position` paragraph was deleted alongside the withdrawal paragraph.** The fifth pass asked for the withdrawal to go and listed *"the `0` rows at `HEAD`"* among the things that hold; both went. Measured here, the deleted statement was true and remains so: 0 rows move on the 579-item and the 581-item load alike. Two consequences — the body now measures only `_delta_key`, while the *What still reads it* table names `sort_items` as the primary sort key with nothing beside it, so the body reads as though the strip reorders the suite; and line 67 of that note says *"the body's `232` and its `0`-at-`HEAD` both reproduce"* while the body carries only the first. Restoring one sentence closes both.
2. **The current-state banner points one round back.** *"This is the current state; everything above is evidence"* sits on the **fourth** correction section (line 370); the fifth correction section below it opens on *"Five passes"* and carries no equivalent. The fifth pass tested this convention, endorsed it, and suggested the improvement that would have kept it working; appending a section without moving the banner is what broke it. The exposure is small, because the fourth section's one superseded paragraph was patched in place with a forward pointer — but a reader following the note's own navigation instruction stops before the current state. Line 274 carries the same shape and has been stale since the fourth round.

### Verdict

`approved`. The fifth pass's single blocking finding is fixed and the restored measurement survives every attempt made here to refute it, including one the note did not claim. The code is unchanged this round; every guard bites under mutation; every re-measurable number reproduces exactly. What remains is two sentences of self-description, recorded above so they are not lost, and neither warrants a seventh round to settle.

### What was independent, and what was not

Independent: the context and the session. This pass started from the notes and `git log`/`git show`, never the authoring transcript and never a prior reviewer's; the author was not asked what anything meant; every number above was produced by this session's own commands against throwaway `git archive` trees. Not independent: the model. `model:claude-opus-5`, the same family as the author and all five prior passes, recorded in `reviewed_by` so a reader can weigh it rather than infer it ([[project-os-dev#ADR-0013]] — shared weights correlate capability, shared context correlates commitment, and it is the second this gate exists to break).

---

# Sixth independent review, 2026-08-20 — **approved**

**This section is the current state.** Everything above it is the record of six passes; read it for how the work got here, not for what is true now.

**Verdict `approved` on all nine notes** — `PHASE-039`, `CHG-20260820`, `FEAT-0139/0140/0141`, `REQ-0058/0059/0060` and `ISS-0240`. The fifth pass's single finding (the wrongly-withdrawn `232`) is fixed and independently re-measured: 232 changed / 349 unchanged on the indexed load, 232 / 347 on the directory-only load, composition 158 + 74 at `HEAD` against 164 + 68 in the working tree — same total, different parts, which is what makes it basis-independent. The review also refuted a claim the note had not made: **none of the 232 collides with a baseline key**, so *removed-and-new* is exact rather than approximate.

Every guard bites under mutation — the 16-cell split matrix, `missing_issue_refs`, the `Broken command` routing, the vocabulary labels, and validator-copy parity were each broken deliberately and each failed. Fleet counts reproduce exactly: `TEST-AUTOMATED-STATUS` 12, `TEST-AUTOMATED-EVIDENCE` 24, `CHECK-SUBJECT` 117 = 85 + 32, `ACCEPTANCE-STATUS` 0 everywhere.

**Six passes, twenty-four findings, and three of them were defects introduced while fixing the previous pass** — each the same shape: a check that could not fire. That is the honest summary of what this took.

## Still open, deliberately

[[ISS-0238]] — 67 checks naming a deleted document's heading. [[ISS-0240]] — `sort_items` and `_delta_key` read `tier:`, so the strip has a prerequisite. [[ISS-0209]] — **the acceptance gate executes in no repo that holds a check**, which bounds what any of this proves.

