---
type: "[[phase]]"
id: PHASE-039
aliases: ["PHASE-039"]
title: "A test says who executes it, and every section is derived"
status: done
order: 39
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
goal: "A test note records who executes it and what it covers. Nothing records whether an automated test passed, and no section a reader sees is filed by hand."
features: ["[[FEAT-0139-The-Suite-Is-The-Verdict]]", "[[FEAT-0140-Sections-Are-Derived-Not-Filed]]", "[[FEAT-0141-The-Contract-Says-It-Upstream]]"]
requirements: ["[[REQ-0058-An-Automated-Test-Carries-No-Verdict]]", "[[REQ-0059-A-Section-Is-Derived-Never-Filed]]", "[[REQ-0060-A-One-Time-Check-Names-Its-Issue]]"]
tasks: []
issues: ["[[ISS-0237-An-Automated-Check-Still-Blocks-The-Manual-Walk]]", "[[ISS-0238-There-Is-Nowhere-To-Put-An-Automated-Check]]", "[[ISS-0239-The-Runner-Stamps-Failing-On-A-Missing-Device]]"]
related: ["[[ADR-0038-The-Suite-Is-The-Verdict]]", "[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[DES-0012-Tests-In-Two-Flows]]"]
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
tags: [testing, schema]
---

# A test says who executes it

## Goal

Two fields already answer every question this corpus asks about a test — `command:` says who executes it, `covers:` says what it is about. A third thing, `tier:`, restated part of the second, and a fourth, `status:`, restated what CI already knows. This phase removes both restatements and derives what a reader sees from what is left.

**Nothing here starts until [[ADR-0038]] and [[ADR-0039]] are accepted.** Both read `proposed`. That is the same gate [[ADR-0030]], [[ADR-0031]], [[ADR-0034]] and [[ADR-0037]] each used: the phase is documented in full, and no note migrates.

## Scope

- An automated test stops carrying a verdict; CI is the verdict ([[ADR-0038]]).
- The three sections — Feature tests, Regression tests, Automated tests — are derived from `covers:` and `command:`, and `tier:` is read nowhere ([[ADR-0039]]).
- `Broken command` becomes a section: an automated test whose `command:` no longer resolves.
- The rules land upstream in `project-os` and sync to the fleet.
- No UI string says *run* or *walk*.

## Out of Scope

- **Making CI execute in the fleet repos** ([[ISS-0209]]). The gate reaches no repo holding a check, and this phase must not claim otherwise.
- **Stripping `tier:` from the 671 notes that carry it.** The field stops being read; removing it is a later migration once the derived sections have been read against for a while.
- **Excavating the 67 destroyed `area:` values** from `your-trainer`'s history.
- Observed coverage ([[FEAT-0138]]), which is the next argument and not this one.

## Exit Criteria

- [~] **Corrected after a second independent review.** True in this repo, and the rules are in place — but *"zero violations, erroring from day one"* was measured here alone. `your-trainer` at `HEAD` carries 2 + 4, so the fleet corpus was not clean and ADR-0011 clause 3 forbade the day-one promotion. The command-bearing half is now its own code, `TEST-AUTOMATED-STATUS`, and both it and `TEST-AUTOMATED-EVIDENCE` warn with a cutover of 2026-11-18
- [~] **Overstated, corrected after independent review.** No *section* and no *gate* decision reads `tier:`, and `GATING_TIERS`/`PERMANENT_TIERS`/`TIER_LABELS` are gone. But `sort_items`, `_delta_key` and the migration script still read it, so the criterion as written was false
- [x] The three sections are derived identically in both front doors — one predicate, `acceptance.section_of`
- [~] **Measured, and measured against the wrong tree.** `your-trainer` 68 → 59 is its WORKING TREE; against `HEAD` it is **62 → 68**, because zero of its acceptance checks carry a `command:` at `HEAD` and six Tier 3 checks enter instead. `project-os-cockpit` 0 → 0 and `your-sudoku` 56 → 56 hold either way. Corrected in [[CHG-20260820]]
- [x] `TESTING.md` and `STATUSES.md` carry the rules upstream, and the fleet is synced — all 12 project-os repos, committed per repo naming only the three synced paths
- [x] No UI string contains *run* or *walk* — guarded over the chrome the product writes, deliberately not over note prose it renders
- [x] Deleting a covering test puts its check back on the list — proved on constructed input in `tests/test_command_targets.py`, with the mutant executed, because the corpus holds **zero** broken commands

## Reviewed twice, and what the second pass changed

**Both passes returned `changes-requested`.** The first found seven; the second verified five of those fixed, found the remaining two only partly done, and found **six more** — including one the first fix introduced.

**The regression worth naming**: moving `missing_issue_refs` off `tier:` made its two clauses contradict, so it returned nothing and `return []` passed the entire suite. `your-trainer` went 73 → 0. That is the exact defect this phase is about — a check reporting nothing because its predicate cannot fire — reintroduced while fixing a review, and it needed a third pair of eyes to see.

**The pattern behind most of the rest**: numbers measured against `your-trainer`'s working tree, which carries 588 uncommitted files. The first pass caught it in the gate delta; the second caught the same error in four more places, including in the note filed to correct it and in [[ADR-0039]]'s own context table. Every one is now stated at both bases.

## Closed 2026-08-20

Seventeen tasks, three features, three requirements, two decisions. 1854 tests pass; the validator is green here and across the fleet sync.

**What the phase found that its own ADRs did not say**, both recorded where they happened rather than smoothed over:

- **The file shape must read its heading, not derive.** A row parsed from `ACCEPTANCE_TESTS.md` carries neither `command:` nor a frontmatter `covers:`, so the derivation had nothing to read and classified all three of a document's headings as feature tests — which would have pushed unmigrated repos' Tier 3 rows into the gate by accident.
- **The migration's parity check caught the one real semantic change** rather than a person finding it: blocking 3 → 4, because a migrated Tier 3 row is a note with no `command:` and is therefore owed. Parity is now scoped to the rows the tier already gated, and the delta prints as `ENTER THE GATE` before the source is deleted.

**Left open on purpose**: [[ISS-0238]] — 67 checks still read an `area:` naming a heading in a deleted document, and recovering the real values is excavation across `your-trainer`'s history rather than a migration. [[ISS-0209]] is untouched and bounds what any of this proves: the acceptance gate executes in no repo holding a check.

**Not delivered, and not attempted**: `tier:` still sits in 671 notes.

**And removing it is not the safe follow-up this note first implied.** Independent review simulated the strip against `your-trainer`: **74 rows change suite position and 232 of 579 delta keys change identity**, so rows would read as removed-and-new across a release tag. `sort_items` and `_delta_key` still read the field. Whoever takes that migration must move both onto a stable key first, or the release delta lies for one cycle.

## Independent review 2026-08-20 — `changes-requested`

Reviewed by `model:claude-opus-5` from the notes and the diff alone, in a session that never saw the authoring reasoning.

Three of the seven exit criteria do not hold as written. *"`tier:` is read by no code path"* — three paths read it (finding 4). *"The gate delta is measured per repo — `your-trainer` 68 -> 59"* — reproduced exactly against `your-trainer`'s working tree, but against its committed HEAD the same code gives `62 -> 68` with six checks entering, which is the tightening `blocking()`'s own comment says was reverted on 2026-08-18 as needing a person's decision (findings 2 and 3). *"Deleting a covering test puts its check back on the list"* — the resolver is proved; the list is not, and removing the `Broken command` wiring passes all 1854 tests (finding 1). *"No UI string contains run or walk — guarded"* — the guard is vacuous over both labels this phase introduced (finding 5). Full detail in [[CHG-20260820-The-Suite-Is-The-Verdict]].

## Second independent review 2026-08-20 — `changes-requested` (verdict stands)

Second pass, `model:claude-opus-5`, fresh context and a different session from both the author and the first reviewer; same model family, recorded in `reviewed_by` as provenance ([[project-os-dev#ADR-0013]]). Every mutant was applied and executed by the reviewing session.

**Five of the seven first-pass findings are genuinely fixed and their mutants now fail.** Reproduced: deleting the `Broken command` routing fails 3 tests; renaming `Needs you` fails the vocabulary guard; dropping `swift` from one side fails parity; `test_the_tiers_render` is a real biconditional. The corrected gate delta reproduces exactly — `62 → 68` at `your-trainer`'s `HEAD`, entrants `TST-0592`..`TST-0597`, zero acceptance checks carrying a `command:`.

**Exit criterion 1 does not hold as written, and it is still ticked `[x]`.** *"both erroring from day one because the migration left zero violations"* is true of this repo and false of the fleet. Measured against `your-trainer` at `HEAD`: `TEST-AUTOMATED-EVIDENCE` **4 errors**, `ACCEPTANCE-STATUS` **2 errors** — and the pre-change validator reports zero on the same corpus, so the widening introduced them. In its working tree `TEST-AUTOMATED-EVIDENCE` is **71**. Not live today only because `your-trainer` carries a validator copy from 2026-08-18 without either rule.

**A new defect was introduced by the review fix itself.** `missing_issue_refs` (`acceptance.py:670-686`) moved off `tier(2)` onto a pair of clauses that are contradictory for a note-shape item, so it can never return one: `your-trainer` **73 → 0**, and replacing its body with `return []` passes the entire suite. Its only consumer, `test_every_tier_two_item_names_the_issue_that_created_it`, can no longer fail. That is the check [[ISS-0173]] and [[PHASE-034]] made honest (158-of-158 → 73-of-158) reporting nothing again.

**Two corrections are themselves incomplete.** Finding 3's stale comment was rewritten in one block; four statements in the same function still assert the tier filter, including the block directly above the line that replaced it. And [[ISS-0240]]'s *"74 rows change suite position"* is a working-tree number — at `HEAD` the strip moves **0** rows, because ids were allocated in document order; only the 232 delta keys hold in both trees.

**On the six entrants**: they derive to `Feature tests`, not to anything [[ADR-0039]] contemplates for them. All 74 Tier 3 checks do — a population the ADR's own table calls *67 automated* — and unlike the 68 Tier 2 checks they carry no grandfather and no promotion date. The ADR also says their `area:` values *"are repaired or emptied, not left"*, and this phase closed with them left ([[ISS-0238]]).

Full detail, with the measurements, in [[CHG-20260820-The-Suite-Is-The-Verdict]].

## Third independent review 2026-08-20 — `changes-requested` (verdict stands)

Third pass, `model:claude-opus-5`, fresh context: a session that had seen neither the authoring reasoning nor either prior reviewer's. Same model family as all three, recorded in `reviewed_by` as provenance ([[project-os-dev#ADR-0013]]) — what is independent is the context, not the weights. Every mutant applied and executed by this session; every count measured against `git archive HEAD` copies of the fleet repos, never their working trees. Baseline **1861 passed, 3 skipped**, validator OK.

**Four of the second pass's six are genuinely fixed and their mutants fail.** `missing_issue_refs` can fire again (`return []` now fails its guard; **117** at `your-trainer`'s `HEAD`, **44** in its working tree, **0** here, and each equals `CHECK-SUBJECT`'s count on the same tree). [[ISS-0240]]'s numbers reproduce exactly — **0** rows move at `HEAD`, **232** delta keys change. [[ADR-0039]]'s corrected table is exact at both bases. `_covers_an_issue` delegates, and restoring its own regex fails the new parity guard. **All seven of the first pass's fixes are still intact**, re-mutated and re-executed.

**Two are partly done, and one of the remainders is a live rule rather than prose.** `ACCEPTANCE-STATUS` and `TEST-AUTOMATED-STATUS` are split on `level:`, not on `command:` — so a `level: acceptance` note carrying a `command:` at `passing` reaches the **day-one error**, which the pre-change validator did not raise at all. That is 89 of the fleet's 139 automated notes by this change's own measurement, and every fleet repo still ships the `run-tests.py` that writes those statuses. The stale-tier sweep left `blocking()`'s docstring **summary line** at *"Unsettled Tier 1/2 items"* and the orphaned `#:` block in `cockpit.py:4302-4327` untouched, still saying *"`tier:` itself is untouched"* two lines above *"Gone with `tier:`"*.

**And the wrong-basis class is not closed.** *"`CHECK-SUBJECT` is 117, not 44"* was corrected in none of the three places the second pass enumerated — the `PROMOTIONS` comment in both validator copies, the test docstring, and [[REQ-0060]] criterion 2. The new `PROMOTIONS` comment claims measurement *"against every repo"* and cites two; fleet-wide at `HEAD` the two dated codes carry **12** and **24**, not 2 and 4.

**Exit criteria**: criterion 1's `[~]` is the right shape but its figure is a two-repo one; the rest hold as written or as marked. [[REQ-0059]] is still `status: implemented` with *"`tier:` is read by no code path"* ticked, which is the criterion this note marked `~`.

**Navigability**, asked directly: a reader starting here arrives at the true state — the `~` markers carry both bases and *"Reviewed twice"* states the regression plainly. A reader starting at [[CHG-20260820-The-Suite-Is-The-Verdict]] does not: it ends on the second pass's recommended follow-ups with no section saying what was done, and its section B still describes `missing_issue_refs` as broken in the present tense. One correction section there closes it.

Full detail with line numbers and measurements in [[CHG-20260820-The-Suite-Is-The-Verdict]], section *Third independent review*.

## Fourth independent review 2026-08-20 — `changes-requested` (verdict stands)

Fourth pass, `model:claude-opus-5`, fresh context: a session that had seen neither the authoring reasoning nor any prior reviewer's. Every mutant applied and executed here; every fleet count measured against `git archive HEAD`, never a working tree. Baseline **1868 passed, 3 skipped**, validator OK.

**Three of the third pass's five hold under independent re-measurement, and a fourth holds where it was filed.** `CHECK-SUBJECT` is **117** at `your-trainer`'s `HEAD` and 44 in its working tree, corrected in all four named places. The `PROMOTIONS` comment's fleet figures are exact: `TEST-AUTOMATED-STATUS` **12** (2/4/6), `TEST-AUTOMATED-EVIDENCE` **24** (4/8/12), `ACCEPTANCE-STATUS` **0** everywhere. Both stale tier statements are gone. [[REQ-0059]] is honestly narrowed. **All thirteen earlier findings survive re-mutation** — the `Broken command` routing, the vocabulary rename, the `swift` parity pair, `missing_issue_refs` and the `_covers_an_issue` delegation each fail their guards, the last still failing after the `fm["level"]` removal.

**The blocking finding is that the recut is incomplete in the silent direction.** Cutting the split on *what ADR-0038 newly forbids* is the right line, but `newly_forbidden` tests `status in TEST_RUNNER_STATUSES`, so a command-bearing note that is **not** `level: acceptance` at `status: ready` falls out of both branches and is reported by nothing — warned by the immediately preceding commit, silent before ADR-0038, silent again now. All 24 cells of the cross-product were executed; that one is the only one that does not land where the record says. The six-case matrix omits it, and closing it breaks no test. Zero instances at every fleet `HEAD`, so latent — the same standing on which the third pass's A1 was filed blocking, in the worse direction. Exit criterion 1 and [[REQ-0058]] criterion 1 both state the closed reading.

**And [[ISS-0240]]'s title took the number the third pass rejected**: `232 of 580`, where that pass said 579 is right; measured here, 579 suite items, 578 distinct delta keys, 580 files including `README.md`.

Full detail with line numbers and measurements in [[CHG-20260820-The-Suite-Is-The-Verdict]], section *Fourth independent review*.

## Fifth independent review 2026-08-20 — `changes-requested` (one finding)

Fifth pass, `model:claude-opus-5`, fresh context: a session that had seen neither the authoring reasoning nor any of the four prior reviewers'. Every cell, mutant and count executed here; every fleet count taken from `git archive HEAD`, never a working tree. Baseline **1878 passed, 3 skipped**, validator OK.

**H1 is fixed and this pass could not break it.** All 16 cells of the cross-product were executed against the validator rather than read off the table, and all 16 agree with it on code *and* severity; four further level values behave as their case-folded equivalents. Five mutants applied and none survived — restoring the old clause fails exactly the cell it dropped. The four non-blocking findings also hold under re-measurement: `REQ-0060` is 85 + 32 = 117 at `HEAD`, the fleet figures are 12/24/117/0 exactly, line 24 of the change note carries its retraction, and `89 of 139` carries its basis (137 on today's trees, so stale rather than wrong). The five earlier fixes re-mutated here still fail their guards.

**The finding is [[ISS-0240]]'s `232`.** Withdrawing it lost a reproducible measurement and the claim that replaced it is false: stripping `tier:` changes **232** keys and leaves **349** unchanged, because `item_from_note` defaults an absent `tier:` to 1 (`acceptance.py:917-922`). 232 reproduces at `HEAD` on both load paths and in the working tree. Third consecutive round in which correcting a finding introduced a defect of the same class — a claim wider than the code — this time in prose rather than in a predicate.

**Navigability**, asked directly: a reader starting here reaches the true state only by following the pointer to [[CHG-20260820-The-Suite-Is-The-Verdict]], whose *"Corrected after the fourth independent review"* section says plainly that it is the current state. That works; this note and the three `FEAT-*` notes would carry it better if each review section opened with one line saying whether its findings were later fixed.

Full detail with measurements in [[CHG-20260820-The-Suite-Is-The-Verdict]], section *Fifth independent review*.
