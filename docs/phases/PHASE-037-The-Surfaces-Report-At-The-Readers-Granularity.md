---
type: "[[phase]]"
id: PHASE-037
aliases: ["PHASE-037"]
title: "The release page and the tests view report at the granularity the reader is working at"
status: done
order: 37
owner: user:edwin
created: 2026-08-18
updated: "2026-08-21"
reviewed_by: model:claude-opus-5
review_date: 2026-08-21
review_verdict: changes-requested
review_response: "2026-08-21: the count was wrong three ways and is now measured - 97 children, and the breakdown adds up. All seven findings across the range are fixed; see the response on each note. || Second pass 2026-08-21: finding A was mine and is the worst thing in this close-out - fixing finding 1 deleted two live tests from the same file, hidden by a suite total that rose. Restored from 07602db (22 test functions again) and recorded in the closing section rather than tidied away. All seven second-pass findings fixed. || Third pass 2026-08-21: all five findings fixed. Finding 1 was the sharpest and is the same class as everything this phase was opened to find - the repair for the toolchain hole moved the growth one branch over, invalidating on every run instead of once. The 'three defects found while building' list is now four, and the emitter's own count of them is in TASK-0543."
review_response_date: 2026-08-21
goal: "Every verification surface answers the question its reader actually has, and the record can hold the answer — a release says what holds IT and offers no control that changes a check, the tests view leads with what a person owes rather than with an inventory, and a rendered mark is a check mark. Widened 2026-08-20: where a surface was found stating something nothing had recorded, this phase now also builds the place to record it. Found by use, not by audit."
features:
  - "[[FEAT-0125-The-Release-Page-Reports-What-Holds-It]]"
  - "[[FEAT-0126-A-Rendered-Mark-Is-A-Check-Mark]]"
  - "[[FEAT-0127-Every-Row-In-The-Tests-View-Is-A-Test]]"
  - "[[FEAT-0128-The-Tests-View-Leads-With-The-Work]]"
  - "[[FEAT-0129-A-Release-Names-Its-Own-Contents]]"
  - "[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]"
  - "[[FEAT-0131-The-Suite-Is-Refined]]"
  - "[[FEAT-0132-Acceptance-Tests-Are-Scaffolded-By-Rule]]"
  - "[[FEAT-0115-The-Sweep-Is-Continuous]]"
  - "[[FEAT-0142-A-Release-Says-What-Is-In-It]]"
  - "[[FEAT-0138-Coverage-Is-Observed-Not-Declared]]"
issues: ["[[ISS-0210-The-Release-Page-Offers-Sixty-Live-Marks]]", "[[ISS-0211-The-Mark-Picker-Shows-Words-Where-The-Check-Mark-Was]]", "[[ISS-0212-Retired-Documents-Render-As-Verified-Tests]]", "[[ISS-0214-A-Note-Whose-Id-Contradicts-Its-Filename]]", "[[ISS-0222-The-Left-Pane-Groups-By-Tier-And-Nothing-Else]]", "[[ISS-0223-The-Bar-Is-The-Wrong-Instrument-In-The-Editor]]", "[[ISS-0224-The-Positional-Address-Outlived-The-Document]]", "[[ISS-0225-A-Nav-Row-Carries-Data-No-Renderer-Draws]]", "[[ISS-0226-A-Surface-Wears-A-Test-Status]]", "[[ISS-0227-Every-Surface-Links-To-The-Same-Place]]", "[[ISS-0228-The-Test-Id-Renders-Twice-On-A-Row]]", "[[ISS-0229-Steps-Proven-Is-Sent-And-Nothing-Draws-It]]", "[[ISS-0231-The-Surface-Row-Is-Two-Lines-And-Names-The-Wrong-Thing]]", "[[ISS-0232-A-Check-Row-Shows-A-Status-It-Cannot-Hold]]", "[[ISS-0233-Migration-Provenance-Outlives-Its-Migrations]]", "[[ISS-0234-The-Generated-Page-Repeats-Itself]]", "[[ISS-0235-A-Surface-Wore-Its-Features-Title]]", "[[ISS-0241-The-Section-Head-Restates-Its-Own-Arithmetic]]", "[[ISS-0242-Two-Different-Things-Are-Both-Called-Automated-Tests]]", "[[ISS-0243-The-Automated-Checks-Page-Is-A-Walk-Page]]", "[[ISS-0244-The-Gate-Rows-Wear-A-Mark-That-Does-Nothing]]", "[[ISS-0245-A-Verdict-On-An-Accepted-Note-Is-Owed-Forever]]", "[[ISS-0246-The-Two-Front-Doors-Are-Not-Comparable]]", "[[ISS-0247-The-Tests-View-Lost-Its-Quiet-Group]]", "[[ISS-0248-Two-Predicates-Disagree-About-Not-In-Flight]]", "[[ISS-0249-Two-Check-Write-Paths-Reach-No-Front-Door]]", "[[ISS-0250-A-Surface-Rename-Silently-Orphans-Its-Checks]]", "[[ISS-0251-A-Test-Backdates-A-Shared-Source-File]]", "[[ISS-0252-Two-Sessions-Closing-Out-Collide-In-The-Snapshot]]", "[[ISS-0253-A-Verdict-Outlives-The-Work-It-Judged]]"]
related: ["[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[ADR-0036-The-Sweep-Is-Withdrawn]]", "[[DES-0012-Tests-In-Two-Flows]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[PHASE-036-One-Human-Walk]]"]
tags: [phase]
---

# The surfaces report at the reader's granularity

## Why this is a phase and not four issues

[[CLAUDE]]'s rule is that a phase needs a goal statable without listing its parts, and exit criteria that are not *"the tasks are done"*. Both hold, and the common cause is sharper than the list of symptoms.

**Every one of these defects is a surface answering a question its reader did not ask.** The release page answers *"which checks exist and would you like to tick one"* when the reader asked *"can I ship"*. The tests view answers *"here is the inventory, 579 rows"* when the reader asked *"what do I have to do"*. The mark picker answers *"which state name"* when the reader asked *"which check mark"*.

They were all built correctly for a narrower moment and never re-read from the outside. [[PHASE-036]] finished the model; this is the first phase to find out what the model looks like to somebody using it.

## Widened 2026-08-20 — from *what a surface says* to *whether anything recorded it*

Edwin re-homed [[FEAT-0142]] and [[FEAT-0138]] here rather than opening a phase for them. Both are capabilities, not defects, so this is a genuine widening and the goal above says so.

**The reason they belong here is that four of this phase's own findings turned out to have one cause, and it is not a rendering mistake.** Each was a surface stating something the record had nowhere to hold:

- [[ISS-0241]] — `89 executed by CI`, derived from `command:` and from no observed run. All 89 carry `evidence: []` and an empty `verdict_date`.
- [[ISS-0243]] — `90% complete` across 15 areas, computed from `mark:` over checks with no recorded result.
- [[ISS-0244]] — a check mark on rows nobody can mark, left behind when [[ADR-0035]] disarmed the control.
- [[FEAT-0142]] — *what is in this release*, answered by **when work finished** because nobody could record a choice.

Correcting the wording fixes the lie. It does not make the surface able to tell the truth, because there is still nowhere to put the fact. **[[FEAT-0138]] is that place for the first two** — a claim that a machine covers a check gets *produced by a run* instead of asserted, which is precisely what would make an automated section able to report anything at all. **[[FEAT-0142]] is that place for the fourth**, under [[ADR-0040]].

**The measurement that makes this one body of work rather than two.** Across the entire fleet on 2026-08-20, `docs/releases/ledgers/` exists in **one repo — this one**. `your-trainer`, which holds 581 checks and 59 blocking ones, has no ledger at all and still carries `mark:` in frontmatter. So every surface reading a verdict there is reading an intention, and no amount of care in the renderer changes that.

This does not widen into *everything*. The line is the one [[ADR-0035]] drew and it still holds: **no write path to a check appears on a release page.** A release records facts about itself.

## Where each came from

All five are Edwin's, from reading his own repos rather than from an audit — which is the provenance that matters, because four of them are invisible to the validator and to the suite. Two are live regressions introduced by [[PHASE-036]] itself.

## Membership, corrected 2026-08-20 — the list under-reported itself by thirteen

`issues:` named **15** notes. **28** issue notes name this phase in their own `phase:` field, and the difference had grown quietly as each one was filed: `ISS-0214`, `ISS-0229`, `ISS-0231`, `ISS-0232`, `ISS-0233`, `ISS-0234`, `ISS-0235`, `ISS-0245`, `ISS-0246`, `ISS-0247`, `ISS-0248`, `ISS-0249`, `ISS-0250`.

*(**28, and I first wrote 29** — counted by eye off a listing before counting it. 15 + 13 = 28, and the arithmetic is the check the eye is not.)*

**Nothing was broken by it, and that is the point.** `PHASE-CHILDREN` gates on the *child's* `phase:` field rather than on this list, so every one of the thirteen was already holding the phase open correctly. What the stale list cost was **reading**: a person opening the phase note to see what it covers was shown half of it, and the widening argument above cites four findings from a body of work whose own index did not list them.

`sync-snapshot.py` propagates status and counters; membership is curation it deliberately leaves alone (`CLAUDE.md`), so this is a hand edit and nothing detects the next one. The features list was checked at the same time and is **complete** — 11 named, 11 pointing here.

*(**And it drifted again by three within a day**, exactly as *"nothing detects the next one"* predicted: `ISS-0251`, `ISS-0252` and `ISS-0253` were filed after that correction and named this phase without joining the list. Re-counted at close-out — **30 issue notes name this phase, 30 are listed** — and `ISS-0213` was removed on being re-homed to [[PHASE-999]]. The lesson stands rather than being restated: a hand-curated index beside a machine-checked field drifts in one direction, and only the field is load-bearing.)*

## Exit criteria

*Each checked against the code on 2026-08-21, not against memory of it — this phase has recorded five separate occasions on which a state was asserted from a grep and was wrong.*

- [x] **No page whose subject is a release offers a control that changes a check.** `gateMark` is **deleted, not defaulted**, and so is `markGateRow` — both replaced by a comment naming why (*"a live-looking helper is how the next caller re-acquires the behaviour a decision just removed"*). [[ISS-0210]], [[ISS-0244]], [[ADR-0035]]. Re-asserted at close-out by `test_no_write_path_to_a_check_appears_on_the_release_page` over the new held-back block.
- [x] **A rendered mark is a glyph on every surface**, guarded by `test_no_surface_brackets_a_raw_mark_rather_than_its_glyph` — which fails if any render site reads `mark` directly instead of going through `MARK_GLYPH`. [[FEAT-0126]], [[REQ-0045]] (`implemented`).
- [x] **Every row in the tests view is a test.** The three `status: retired` run plans are no longer typed as tests ([[ISS-0212]]), and the indexed loader selects on `level: acceptance` over `index.notes_by_type("test")` — **not** on the directory — so an acceptance check outside `docs/tests/acceptance/` routes by its level. [[FEAT-0127]] (`done`), [[REQ-0046]] (`implemented`).
- [x] **The tests view opens on what is owed.** [[TASK-0556]]: surfaces sorted by percentage incomplete, children incomplete-first, sorted **server-side** so both front doors get it from one place. The inventory is reachable and is not the landing. [[FEAT-0128]], [[REQ-0047]] (`implemented`).
- [x] **A release can name its own contents, and the gate can be scoped to them.** [[FEAT-0129]] built the naming; [[ADR-0040]] decided that **selection subtracts and never divides**; `Suite.blocking_minus` implements it and `test_the_mixed_cell_still_gates` guards the cell a subtraction rule gets wrong. [[FEAT-0142]] closed the reporting half — an exclusion records a reason and the page says what the selection cost.

## What this phase must not do

**It must not re-open the vocabulary.** `mark:` stays words in storage — that is [[ISS-0200]], accepted and migrated across 669 notes. The glyph is a *rendering* concern and this phase touches only rendering.

**It must not widen the gate.** [[ISS-0208]] is open and owns the tier question. Nothing here changes which checks block.

## Independent review — 2026-08-20

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `222e19e..6cc7f72`; the author's reasoning trace was not available to it. Verdict: **changes-requested**.

The widening is well-argued: the four findings really do share one cause, and re-measurement confirms the claim that joins them — `docs/releases/ledgers/` exists in exactly **one** of the twelve `SNAPSHOT.yaml`-bearing repos, this one, and `your-trainer` has none while still carrying `mark:` in frontmatter. The `FEAT-0138` re-homing is consistent across the note, `docs/PHASES.md`, `PHASE-999` and `SNAPSHOT.yaml`.

Two corrections inherited from the child notes: *"90% complete across 15 areas"* — the 90% is exact, the **15** does not reproduce (61 area blocks, 45 distinct names); and see the shared basis finding.

**Shared finding — every `at HEAD` measurement in this range is a working-tree measurement.** `your-trainer` carries 591 dirty files under `docs/`. Re-measured against a `git archive HEAD` and a fresh `--shared` clone: tier1 total **496** (not 406), tier2 **85** (not 86), and **zero** command-bearing acceptance checks — so at HEAD that repo emits *no automated section at all* and the 89/9-todo/`evidence: []` population does not exist there. The gate is **68** blocking at HEAD (43 covering a `FEAT`, ten features, 40 out of scope), not 59/39/nine/36. Every figure quoted reproduces exactly against the working tree. No note in this range carries a basis caveat, while `CHG-20260820-The-Suite-Is-The-Verdict` — the note six prior review rounds spent on this exact point — carries 24.

## Independent review — second pass, 2026-08-20

**This supersedes the first-pass verdict above. Current verdict: approved.** Same reviewer, same conditions — fresh context, separate session, `model:claude-opus-5` — re-run against the working tree after the first pass's findings were acted on. Every claim below was re-measured or re-executed rather than read.

Basis blockquote present; the `15 areas` line is resolved on `ISS-0243` (it was true when written). The widening argument and the ledger measurement stood up in the first pass. Corrections are tracked on the child notes.


## Closed 2026-08-21

**Ninety-seven notes name this phase and all ninety-seven are resolved.** Eleven features, nine requirements, three ADR-type notes, thirty issues, thirty-eight tasks, one design, five change notes.

*(**The first version of this line said ninety-five, and its own breakdown summed to ninety-nine.** Neither number was measured — both were typed. Corrected after independent review by counting: `97`, and the breakdown now adds up. This is the phase whose thesis is that a count with no cause beside it is the defect, and whose membership section already says *"the arithmetic is the check the eye is not"*. It said it twice and did it neither time.)*

### What the last day added, and why it is not a tail

Four of the five exit criteria were met before 2026-08-21. The work done to close the fifth was **not** bookkeeping, and every piece of it was the same defect this phase was opened to find — *a state the record could not express, so it was expressed by nothing*:

- [[TASK-0576]] / [[FEAT-0142]]: an exclusion records **why**, and the page reads `N features held back · M checks no longer gating`. A gate that fell from 59 to 23 with nothing beside it is [[ISS-0241]] and [[ISS-0243]] in a new place.
- [[FEAT-0138]] / [[REQ-0057]]: **coverage is observed, not declared.** The test declares the check, the run emits, and deleting the covering test puts the check back on the run list by itself. `covered_by:` — a standing claim that had never settled a check in any repo — is removed, and [[REQ-0039]] is superseded.
- [[ISS-0250]]: `SURFACE-ORPHAN`. A rename silently orphaned every check on a surface, and an orphaned surface was indistinguishable from an untested one.
- [[ISS-0253]]: `review_response:` and `REVIEW-STALE`. **51 notes** were closed while still reading `changes-requested`. *(Both this note and the rule first said 43 — the issue's filed count was not re-measured and the rule could not see `CHG-*` notes at all. Two errors agreeing. Corrected after independent review.)*
- [[ISS-0249]]: `retire_check` is routed; `cover_check` is deleted. And `test_no_public_write_in_note_writes_is_unreachable` now asks the general question — *is every write routed?* — that nothing was asking.
- [[ISS-0252]]: `close-out-commit.sh` names what it changes in `SNAPSHOT.yaml`'s membership, and the **dangling** case separately, because that is the one that does not self-heal.

### Four defects found while building, each of them a rule that could not fire

The pattern this phase kept meeting, met three more times on its last day:

1. **`Remove` on the release page was unreachable.** It is guarded on `c.kind !== 'derived'` and a test pinned that guard — and `publication.py` never emitted a third kind, so a feature could be added through the front door and never taken back out through it.
2. **The gate's subtraction could not fire on `~release/next`.** The selection was read with `index.by_id(release_id)`, and `release_id` is the literal `"next"` on the page a person opens.
3. **The coverage emitter's invalidation set was computed from the declarations**, so deleting the test — which deletes the declaration — removed the check from the set that could be invalidated. `covered_by:`'s silent rot, reproduced inside the tool built to end it. Its test **failed on first run**, which is the only reason it is not still there.

4. **The coverage emitter's rule for *evidence of absence* was wrong three times**, and each version was found by running it in a loop and counting ledger entries rather than by reading it. It keyed on `--by`, so renaming the CI job stranded every verdict; then on *absence from this run*, so a `.py` run and a `.kt` run on one platform retracted each other every cycle; then it invalidated a skipped test **once per run, forever**, and invalidated checks that had no verdict at all. The rule is *"has the machine's claim stopped being backed"*, read off the ledger, with **skipped** and **absent** kept apart.

And a fifth, in the tooling rather than the product: the declaration scanner **read its own docstring** as a coverage claim, because a `#` comment inside a string satisfies *"is this a comment"*. It uses `tokenize` and `ast` now.

### The close-out's own worst defect: two live guards deleted while fixing a review finding

Fixing the first pass's finding 1 — a test that counted a substring and was vacuous for four of thirteen write paths — **deleted two other tests from the same file.** `test_the_page_groups_by_surface_and_not_as_one_flat_list` and `test_a_stale_tick_is_not_drawn_as_done` were both green, both guarding live renderer behaviour, and both gone at `b635c39`.

The mechanism was a rewrite that replaced *everything from the target function to the end of the file* rather than the function. **The headline hid it**: repo-wide `def test_` went 1829 → 1830, because three tests were added elsewhere in the same commit.

This is [[PHASE-039]]'s recorded lesson one step worse. That phase found three of twenty-four findings were *defects introduced while fixing the previous pass*, each a **check that could not fire**. This is a check that is **not there** — and a suite total that rises is the reason nobody looks. Restored from `07602db`, and `tests/test_checks_view.py` is back to 22 test functions.

Found by the second pass **counting `def test_` across the two commits**, which is the kind of thing only execution finds.

### What is deliberately not closed

- **[[ISS-0213]]** is `deferred` under [[PHASE-999]]. Its finding was this phase's and is answered; what remains is three lines of data in `your-trainer`, costing three blocking checks, on a repo whose surfaces are in no commit. Edwin's call, on his repo.
- **[[ISS-0209]]** bounds what any of this proves: the acceptance gate runs in no repo that holds a check. The coverage emitter runs here and nowhere the fleet's data lives, and every note that touches it says so.
- **The `area:` -> `[[SUR-####]]` schema change** ([[ISS-0250]]) is the durable fix and is a migration across 579 notes in an uncommitted corpus. The validator rule reports the gap it leaves.
- **Whether concurrent close-out sessions are supported** ([[ISS-0252]]) is an ADR-shaped decision. A lock was measured and does not close the collision it was offered against.

### Two vocabularies now exist in three copies each

`OWED_VERDICTS` (cockpit, validator, renderer) and the surface-title join (cockpit, validator). Both are forced — the validator is stdlib-only and standalone, the renderer is TypeScript — and both are pinned by tests that **drive** the copies over the same inputs rather than matching text in either. A text assertion passes on a rule whose normalisation is in a comment, which is this repo's own recorded mutation-testing pitfall and which bit this phase again on its last day.

## Independent review — 2026-08-21

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `f5ca55b..07602db`; the author's reasoning trace was not available to it. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — same model as the author, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant rather than read.


**Verdict: changes-requested.** Four of the five exit criteria hold under refutation, and two of the phase's own new rules do not do what the closing section says they do.

### What survived refutation

- **Criterion 1 holds.** `gateMark` and `markGateRow` are **deleted, not defaulted** — `grep -rn "gateMark\|markGateRow"` over `desktop/src/` and `src/` returns comments and test assertions only, and no `function gateMark` exists anywhere.
- **Criterion 3 holds, and was verified by construction rather than by reading the loader.** I built a temp repo with an acceptance check at `docs/features/weird/plan/tests/TST-9001-Odd-Home.md` — outside `docs/tests/acceptance/` — and `acceptance.load(docs, index=...)` returned it (`shape: notes`, one item). Routing is by `level:`, not by directory.
- **Criterion 5's subtraction is honestly guarded.** `delta()` is pinned both on the mechanism *and* behaviourally, and the behavioural half is real (it builds a suite, deselects a feature, and asserts the row survives in `chronic`). The mechanism assertion is source-text, which is normally this repo's recorded pitfall — here it is defensible, because `delta()` takes no deselection argument and a subtracting mutant cannot be expressed without new plumbing.
- **All 97 children are at a terminal status.** Nothing is closed over. `ISS-0248` is `declined`, which STATUSES.md line 51 lists as resolving.

### Finding 1 — the closing count is wrong three separate ways

*"Ninety-five notes name this phase … Eleven features, eight requirements, three ADRs, thirty issues, forty-one tasks, one design, five change notes."*

Re-counted by parsing every note's own `phase:` field, which is the load-bearing one this note correctly identifies:

| | headline | the note's own breakdown | measured |
|---|---|---|---|
| total | **95** | **99** (11+8+3+30+41+1+5) | **97** |
| requirements | — | 8 | **9** |
| tasks | — | 41 | **38** |

Features (11), ADRs (3), issues (30), design (1) and change notes (5) are all exact. The claim *"all ninety-five are resolved"* is substantively true — all 97 are — but three different integers appear for one population, and none of them is the population. This note's own words are *"15 + 13 = 28, and the arithmetic is the check the eye is not."*

### Finding 2 — *"the rule found exactly that number independently"* is not independent corroboration

The closing section says **43 notes** were closed still reading `changes-requested` *"and the rule found exactly that number independently."* The two 43s are different populations that coincide.

`ID_PREFIXES` in `tools/scripts/validate-docs.py` line 63 does not contain `CHG`, so `build_note_index` never indexes a change note and `REVIEW-STALE` **cannot fire on one**. Measured against `git archive f5ca55b`: **56** notes carry an owed verdict, **51** at a terminal status, **8** of them `CHG-*`. 51 − 8 = 43. See [[ISS-0253]] for the detail.

### Finding 3 — the ISS-0249 general guard is vacuous for the function ISS-0249 is about

`test_no_public_write_in_note_writes_is_unreachable` counts the raw substring `"<name>("` over concatenated source. `_serve_retire_check` contains `retire_check(`, so the handler's own definition and dispatch line supply two free hits. I replaced the real `note_writes.retire_check(` call with a non-existent function and the guard still passed. Vacuous for **4 of 13** write paths — `mark_released`, `release_contents`, `retire_check`, `seal_ledger`. See [[ISS-0249]].

### On the *"two vocabularies in three copies"* claim

Verified rather than accepted. I broke the **cockpit** side of the surface join (`cockpit.py` `surface_coverage`, dropping `.lower()`) while leaving the validator untouched: `test_the_rule_and_the_join_agree_on_normalisation` failed on `'Riding — routes'`. That guard genuinely drives both copies. The closing section's warning about text assertions is correct — and Finding 3 is that same pitfall committed one file away.

## Independent review — second pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `07602db..b635c39` — the first pass's findings and the author's reasoning trace were not available to it, only the seven claims as the notes state them. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]): same model as the author and as the first reviewer, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant.

**This supersedes both earlier verdicts on this note. The `review_response:` above is accurate on the count and wrong on the sweep.**

**The count is now right, measured rather than read.** Parsing every note's own `phase:` field across `docs/`: **97** notes name this phase — 11 `feature`, 9 `requirement`, 30 `issue`, 38 `task`, 1 `design`, 5 `change`, and 3 ADR-type (1 `adr` + 2 `decision`) — which sums to 97 and matches the closing line term for term. **All 97 are at a terminal status**; zero exceptions, statuses spanning `done` 48, `fixed` 29, `implemented` 9, `merged` 5, `accepted` 4, `declined` 1, `superseded` 1. The five exit criteria carry code-level evidence and criterion 5's — the one closed on the last day — checks out end to end (`publication._held_back_rows` records a reason and reports an exclusion that has none; `renderer.ts:7965` draws `N feature(s) held back · M check(s) no longer gating`; guarded by `tests/test_release_held_back.py` and `tests/test_gate_subtraction.py`).

**"All seven findings across the range are fixed" is the claim that does not hold.** Six are. The seventh was fixed by a change that opened a worse one, and the same commit deleted two working guards.

**Finding A (high) — two live regression guards were deleted by this commit and nothing says so.** `tests/test_checks_view.py` went from 22 test functions to 20: `test_the_page_groups_by_surface_and_not_as_one_flat_list` ([[TASK-0520]] / [[ISS-0223]] / [[ISS-0234]]) and `test_a_stale_tick_is_not_drawn_as_done` ([[ISS-0234]]) are gone, and `grep -rn` over `tests/ src/ docs/` at `b635c39` finds neither name anywhere. They were not retired and they were not failing: `git diff --stat 07602db..b635c39 -- desktop/` is empty, and I re-executed both tests' assertion sets against `renderer.ts` at HEAD — all seven strings (`checks-area`, `for (const area of areas)`, `checkPercent(area.items)`, `checkProgress` absent, `items.filter((i) => i.stale)`, `stale} stale`, `(done.length / total)`) still hold. Both would have passed. Repo-wide `def test_` went 1829 → 1830, because three tests were added in `test_observed_coverage.py`, so the deletion is invisible in the headline. The removed block sits immediately after the rewritten tail of `test_no_public_write_in_note_writes_is_unreachable`, which is consistent with an over-wide edit. This is the phase's own signature defect one step worse than the version it was fixing: not a check that cannot fire, a check that no longer exists.

**Finding B (high) — removing the `by` key from the invalidation set opened a new silent-rot hole, and it recurs every run.** `plan`'s `stale` set is now every `method: automated` verdict not re-observed in *this* run. Two runs on one platform that observe different subsets — the two toolchains this tool's own docstring puts in scope — therefore retract each other's verdicts forever. Constructed: a temp repo with `TST-0001` declared by a `.py` test and `TST-0002` by a `.kt` test, one platform, alternating pytest/gradle JUnit reports. At `b635c39`: run 1 `pass TST-0001`; run 2 `pass TST-0002` **+ `invalidate TST-0001 (no covering test observed)`**; run 3 `pass TST-0001` **+ `invalidate TST-0002`**; run 4 `pass TST-0002` + `invalidate TST-0001`. Seven ledger entries after four runs, growing by two per run, and at every instant one of the two checks reads as uncovered although a run observed it passing minutes earlier. The identical script against `07602db` gives **two** entries and `nothing changed` from run 3 onward. So the `by` filter was doing real work, and the fix removed it wholesale instead of separating *which machine wrote it* (correctly irrelevant) from *what this run's scope was* (load-bearing). The bug it fixed — a CI-job rename — happens once; the one it created happens on every run. `.github/workflows/observed-coverage.yml` has a single `observe` job today, so this repo does not trigger it: latent, undetected, in the flattering direction, which is the exact shape of the rot the feature exists to end.

**Finding C (medium) — the other half of the `by` removal is guarded by nothing.** The pass-dedup in `main` dropped `and standing.by == args.by` and carries a comment asserting the consequence (*"Keying on it appended one entry per CI-job rename"*). I restored that clause in a clean worktree at `b635c39` and ran the **full** suite: 2051 passed, 5 skipped, and the only two failures are worktree-path artefacts (`test_the_project_id_is_the_directory_name_by_default`, `test_the_header_measures_from_the_instant_not_the_day`). No emitter test noticed. Three of the four behaviour changes in this file are pinned — mutants restoring `verdict.by == by` in `stale`, making the `failing` branch skip non-automated verdicts, and dropping `method == "automated"` from `stale` each fail their named test — and this one is not.

**Findings D–F (medium/low), recorded on the notes that own them:** the change note's impact table still states the retired `by`-scoped behaviour because the note was appended to rather than corrected (`61  0` on `git diff --numstat`); `migrate-acceptance-checks.py` had one of eleven `LEDGER_MOVED_FIELDS` removed under a reason that applies to all eleven; and the corrected `REVIEW-STALE` prose kept *"dating to 2026-08-02"* when the measured earliest `review_date` among the 51 is **2026-07-30**, while three other sites in the same file still assert the refuted 49/43 breakdown.

### On whether this phase is legitimately `done`

**The membership and the criteria say yes.** Nothing is closed over, the arithmetic finally checks, and every criterion has evidence in code rather than in prose. **The section titled *"Three defects found while building, each of them a rule that could not fire"* is what now reads short** — its third entry is the coverage emitter's invalidation set, and the repair for that entry is Finding B. Four, not three, and the fourth was introduced by the fix for the third.

### Independence

Fresh context and a separate session, which is the gate ([[project-os-dev#ADR-0013]]). **Not** independent: the model family — `model:claude-opus-5` authored the work, ran the first pass, and ran this one, recorded in `reviewed_by` so a reader can weigh it rather than infer it. Findings A and C are the kind a shared-model reviewer is *most* at risk of missing (both are absences rather than assertions), and both were found by execution — counting `def test_` across the two commits, and running the full suite against a restored mutant — rather than by reading.

## Independent review — third pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `b635c39..c9d6a82`; neither the author's reasoning trace nor either earlier reviewer's working was available to me beyond what these notes themselves record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran both earlier passes, recorded in `reviewed_by` as provenance. Every count below was re-measured from the tree and every guard re-executed against a constructed mutant. **This verdict supersedes the second pass's on this note.**

**Verdict: changes-requested — on the record, not on the phase.** Five of the second pass's seven findings are fixed and verified by execution. Finding A's repair is exactly right, including the decision to record the deletion in the closing section rather than tidy it away. But *"All seven second-pass findings fixed"* in the `review_response:` above is false in two independent ways, and one of them is the third consecutive round in which repairing this emitter has introduced the defect it was repairing.

### What survived refutation

- **Finding A's restoration is verbatim and the tests are not vacuous.** I extracted both functions from `07602db` and from `c9d6a82` and diffed them: byte-identical. `tests/test_checks_view.py` is back to **22** `def test_` functions. Both guards kill mutants: flattening `for (const area of areas)` and deleting `checkPercent(area.items)` each fail `test_the_page_groups_by_surface_and_not_as_one_flat_list`; changing `(done.length / total)` to `(settled.length / total)` fails `test_a_stale_tick_is_not_drawn_as_done`.
- **Nothing else was lost anywhere in `f5ca55b..c9d6a82`.** I parsed every `tests/**/*.py` at all four commits and diffed the `def test_` sets file by file. The only removals in the whole range are the seven `covered_by:`/promotion tests at `07602db`, every one of them a test for the mechanism `REQ-0057` deleted, replaced in the same commit by seven guarding its absence; the two at `b635c39`, restored here. No test file was deleted at any point. Totals 1761 → 1829 → 1830 → **1835**.
- **Finding B's own tests are real.** Restoring the absence rule (`check not in passing and check not in failing`) fails `test_two_runs_covering_different_toolchains_do_not_retract_each_other` and `test_a_run_that_never_reached_the_test_leaves_it_alone`; deleting the skipped branch fails `test_disabling_the_covering_test_does_the_same` and the latter; folding skipped back into absence fails two. I also built the alternating-toolchain loop myself — `TST-0001` by a `.py` test, `TST-0002` by a `.kt` test, one platform, three full cycles — and counted **two** ledger entries, both `pass`, no retraction.
- **Finding C's test is real.** Restoring `and standing.by == args.by` fails `test_a_second_machine_saying_pass_adds_nothing` and nothing else.
- **Finding E's claim is true.** `validate_moved_verdict_fields` returns early unless `docs/releases/ledgers/` exists *and* holds a `*.json`, so the twelve `LEDGER_MOVED_FIELDS` are refused only in a ledger-keeping repo. The enumeration is right at its stated arity: all ten named fields are written by `note_text`, `covered_by` is not, and the twelfth (`merged_from`) is correctly absent from both lists.
- **Finding G is done.** The false closing clause is gone from `ISS-0213`'s `review_response`.
- **Suite, validator, CI step set.** `2060 passed, 3 skipped` (268s), `validate-docs: OK`, and `validate-docs.sh --as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `c9d6a82`.
- **The phase's own claims hold.** Parsing every note's `phase:` field across `docs/`: **97** name this phase — 11 `feature`, 9 `requirement`, 30 `issue`, 38 `task`, 1 `design`, 5 change notes, 3 ADR-type (1 `adr` + 2 `decision`) — summing to 97 and matching the closing breakdown term for term. **All 97 are terminal**, zero exceptions (`done` 48, `fixed` 29, `implemented` 9, `merged` 5, `accepted` 4, `declined` 1, `superseded` 1).
- **The two criteria I judged weakest both hold.** Criterion 5 (closed on the last day, and the only one resting on work newer than the previous review) is guarded behaviourally on the payload — `test_the_page_says_how_many_were_held_back_and_what_it_cost` asserts the held-back row, its resolved title *and* `gate.deselection` together — and its renderer half is not merely text-shaped: rewriting the sentence to `${heldBack.length} excluded` fails `test_the_page_never_shows_a_smaller_number_alone`, and emptying `heldBack` while leaving the text in place fails three tests, not one. Criterion 2 (guarded only by source-text assertions over `renderer.ts`, this repo's own recorded pitfall) survives the re-introduction of two of the three defects `ISS-0211` names: a `title` attribute rendering the raw mark fails `test_no_surface_renders_a_raw_mark_unbracketed_either`.

**Finding 3 (medium) — "Finding F fixed" is not true, and the correction that was written is itself wrong.**

*Two of the four sites F named are untouched.* `tools/scripts/validate-docs.py` lines 2884–2886 (and the byte-identical bundled copy) still read *"Measured 2026-08-20: **49 notes carry `changes-requested`, 43 of them at a terminal status**, dating back to 2026-08-02"*, and line 2935 still reads *"Six of the 49 are that"*. Measured at `f5ca55b` by driving the rule's own predicates over the tree: **56** owed, **51** terminal, therefore **5** non-terminal, earliest `review_date` **2026-07-30**. Every one of those five figures is refuted by the `PROMOTIONS` comment 1,800 lines above in the same file. One file states two populations about one rule, which is the exact condition the second pass reported and the response claims to have removed.

*The new number is wrong.* The corrected comment reads *"the earliest six dated **2026-07-30**"* and its parenthesis reads *"Measured: 2026-07-30, on six notes."* Re-measured twice — once through the rule's own predicates over `git archive f5ca55b`, once independently by `grep` over the archived tree — the answer is **eight**: `CHG-20260730-Two-Features-Closed`, `FEAT-0045`, `ISS-0037`, `ISS-0057`, `ISS-0068`, `ISS-0069`, **`PHASE-011`** and **`PHASE-013`**. The two phase notes are not excludable: drop them and the population totals 49, not the 51 the same sentence gets right. The six is the second pass's figure, adopted verbatim rather than re-measured — a number copied instead of counted, in the correction to a comment about numbers copied instead of counted.

**Finding 1 (high) — the fix for B closed absence and reopened the same unbounded growth one branch over, and it writes invalidations about nothing.** Two constructions, both against `c9d6a82`:

*The loop that grows.* A temp repo, one acceptance check `TST-0001`, one declaring `.py` test. Run 1 reports it passing → one `mark: pass` entry. Runs 2–5 report the same test as `<skipped/>` → **`invalidate TST-0001` on every single run**, four in a row, ledger at five entries and growing by one per run forever. `@Ignore` is not a one-off like a CI-job rename: it sits in a codebase for weeks while CI runs on every push, so this recurs in exactly the way finding B said the absence rule recurred. The module's own stated invariant — *"## It appends only when the answer CHANGES"* — is false for this branch.

*The events about nothing.* The same repo with **no verdict ever recorded**, three skipped runs: **three invalidations**, of a check the ledger has never heard of. The `failing` branch guards precisely this (`if check not in current: continue`) and `test_a_check_the_ledger_never_heard_of_is_not_invalidated` states the principle in as many words — *"There is no standing verdict to overtake, and appending an invalidation would be an event about nothing"* — but it only exercises the *absent* case, so the new branch walks straight past it.

The cause is structural rather than a slip. The declaration-gone half of `stale` is derived from `current`, so an invalidation removes the check from `current` and the branch cannot re-fire; the skipped half iterates `declared` and consults neither `current` nor what it has already written. It needs the same two guards the other two branches carry.

**Finding 2 (medium) — a skipped declaring test is laundered into a `pass` by any sibling that passes.** Constructed: `TST-0001` declared by `test_one` and `test_two`; one report in which `test_one` passes and `test_two` is `<skipped/>`. Output: `emit-coverage: pass TST-0001 (test_one)`, one `mark: pass` entry, no invalidation. `plan`'s docstring says *"A check is **observed passing** only when every test declaring it ran and passed"*, and this commit's new comment says *"**Skipped is observed, and it is not a pass.**"* Neither holds: `seen = [t for t in tests if t in results]` still treats a skipped test as absent, and the new loop can never reach the mixed case because `check in passing` short-circuits it. `test_every_declaring_test_must_pass` exercises only the *failing* sibling, which is why nothing catches it. The consequence is the escape hatch the feature exists to close — add one trivially-passing declaring test and an `@Ignore` on the real one stops being visible anywhere.

### Residuals, recorded rather than requested

- **Criterion 2 is written wider than its guard.** It claims the test *"fails if any render site reads `mark` directly instead of going through `MARK_GLYPH`"*. A site assigning `el.textContent = String(item.mark)` passes both mark guards — the regexes match template-literal forms only. Two of the three original defect shapes are caught; the general claim is not what is guarded.
- **The closing section's *"Three defects found while building"* is now short by two.** The second pass made it four. Its third entry is the emitter's invalidation set, and Finding 1 is the third repair of that same entry.

### Independence

Fresh context and a separate session, which is the gate ([[project-os-dev#ADR-0013]]). **Not** independent: the model family — `model:claude-opus-5` authored this work and ran both earlier passes, and runs this one, recorded in `reviewed_by` so a reader can weigh it rather than infer it. I have no memory of authoring any of it. Findings 1 and 3 were both found by execution — running the emitter in a loop and counting entries, and re-measuring a population against `git archive f5ca55b` — rather than by reading, which is the same route the previous two passes' sharpest findings took.

### Can this phase close

**Yes, on its own terms, and the record has to be corrected first.** The membership is measured and complete, all 97 children are terminal, and all five exit criteria hold under refutation — none of the three findings above touches a criterion. What blocks the close-out is narrower and entirely repairable: the `review_response:` on this note asserts a completion that is not true, `FEAT-0138`/`REQ-0057`/`TASK-0543` are at terminal status carrying a live emitter defect of the exact class the phase was opened to find, and the validator file still states two populations about one rule. Fix those and the phase closes with nothing outstanding.
