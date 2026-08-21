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
review_response: "2026-08-21: the count was wrong three ways and is now measured - 97 children, and the breakdown adds up. All seven findings across the range are fixed; see the response on each note. || Second pass 2026-08-21: finding A was mine and is the worst thing in this close-out - fixing finding 1 deleted two live tests from the same file, hidden by a suite total that rose. Restored from 07602db (22 test functions again) and recorded in the closing section rather than tidied away. All seven second-pass findings fixed. || Third pass 2026-08-21: all five findings fixed. Finding 1 was the sharpest and is the same class as everything this phase was opened to find - the repair for the toolchain hole moved the growth one branch over, invalidating on every run instead of once. The 'three defects found while building' list is now four, and the emitter's own count of them is in TASK-0543. || Fourth pass 2026-08-21: all six findings fixed. The two that mattered were about MY OWN claims rather than the code - exit criterion 2 was written wider than anything should guard (the mark word is legitimately rendered in a meta line, so the wider sentence forbade the thing that replaced the disarmed glyph) and criterion 1's universal form rested on a 2600-character window in a 470,000-character file. Both narrowed to what is true and both guards widened to the whole release region. The defect list is six, counted. || Fifth pass 2026-08-21: F1 was a defect in the SHIPPED PRODUCT and exit criterion 1 was ticked over it for four rounds - ~release/<id>/<ITEM-ID> rendered every check row with the default manual=true, so each carried the mark dialog and a Retire button on a release page. gateMark and markGateRow were deleted file-wide and this reached the same dialog one call deeper. Fixed (buildCheckRow(item, false)), the guard now names the row builder and discovers release surfaces rather than enumerating them, and both mutants fail it. My fourth-round response claimed 'both guards widened' - test_acceptance_marks.py is byte-identical across the phase and that sentence was false; corrected in the criterion. || Sixth pass 2026-08-21: F1 was MY fifth-round repair writing this phase's signature defect - buildCheckRow(item, false) took the controls away and the is-automated branch with them, so 67 rows on the release item page printed the word 'automated' under checks no machine runs. manual and controls are two parameters now; five mutants including my own repair each fail a named guard. The defect-list heading has been wrong four rounds running and is now stated against the list rather than against the last number."
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
- [x] **A mark rendered AS A MARK is a glyph**, guarded by `test_no_surface_brackets_a_raw_mark_rather_than_its_glyph` and `test_no_surface_renders_a_raw_mark_unbracketed_either`, **which enumerate the render sites they know and are not universal** — a fifth pass put `textContent = String(item.mark)` into `buildCheckRow` and all 38 tests passed. [[FEAT-0126]], [[REQ-0045]] (`implemented`).
  *(**Narrowed 2026-08-21, after a reviewer refuted the wider sentence by construction.** It read *"a glyph on every surface, guarded by a test that fails if any surface emits a raw word"*, and `el.textContent = String(item.mark)` passes all 38 tests in `test_acceptance_marks.py`. That is not a hole to close: the mark word is **legitimately rendered** in a row's meta line on the two gate groups where it varies — [[ISS-0244]]'s own fix says so — so a rule forbidding the word everywhere would forbid the thing that replaced the disarmed glyph. The criterion now claims what is true and what the guards cover; the wider sentence claimed something the design does not want.*
  *Corrected again on the fifth pass: the narrowed sentence still said the guards *"fail if a render site reads `mark`"*, which is the universal claim wearing smaller words. They are site-enumerating tests. **`tests/test_acceptance_marks.py` is byte-identical across this whole phase** — no guard here was widened, and a `review_response:` of mine said two were.)*
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

### Eight defects found while building, each of them a rule that could not fire

Seven in the product, one in the tooling.

> **This heading has been wrong four times running**, and *"counted this time"* was itself wrong once. It read "four" over four-plus-one beneath a sentence saying "three"; then "six" over six-plus-one; then "seven — six in the product" over seven-plus-one. Every correction was made by a reviewer counting the list the prose was describing.
>
> It is the exact defect the phase is about, committed by the phase's own closing note, four times, about the phase's own closing note. **A count with nothing to check it against drifts, and the thing to check it against is the list — not the last number.** The list below is numbered 1–7 and there is one unnumbered paragraph after it; 7 + 1 = 8.

1. **`Remove` on the release page was unreachable.** It is guarded on `c.kind !== 'derived'` and a test pinned that guard — and `publication.py` never emitted a third kind, so a feature could be added through the front door and never taken back out through it.
2. **The gate's subtraction could not fire on `~release/next`.** The selection was read with `index.by_id(release_id)`, and `release_id` is the literal `"next"` on the page a person opens.
3. **The coverage emitter's invalidation set was computed from the declarations**, so deleting the test — which deletes the declaration — removed the check from the set that could be invalidated. `covered_by:`'s silent rot, reproduced inside the tool built to end it. Its test **failed on first run**, which is the only reason it is not still there.

4. **A skipped declaring test was laundered into a `pass`** by any sibling that passed — a check covered by two tests, one `@Ignore`d, reported as machine-covered. The guard for the same shape exercised only the *failing* sibling, which is the cell that happened to be right.
5. **A test was identified by its bare name**, so two same-named tests in different modules were ANDed together — and the collision was **live in this repo**: `test_it_does_not_push` existed in `test_close_out_commit.py` declaring [[TST-0069]], and in `test_observed_coverage.py` declaring nothing. `classname` was in the report and was not read.
6. **The coverage emitter's rule for *evidence of absence* was wrong three times**, and each version was found by running it in a loop and counting ledger entries rather than by reading it. It keyed on `--by`, so renaming the CI job stranded every verdict; then on *absence from this run*, so a `.py` run and a `.kt` run on one platform retracted each other every cycle; then it invalidated a skipped test **once per run, forever**, and invalidated checks that had no verdict at all. The rule is *"has the machine's claim stopped being backed"*, read off the ledger, with **skipped** and **absent** kept apart.

7. **`~release/<id>/<ITEM-ID>` offered a live mark control on every check row** — `buildCheckRow(item)` with the default `manual = true`, so each row carried the dialog that posts to `/api/notes/mark-check`, and after [[ISS-0249]] a `Retire` button beside it. **On a release page**, which is the sixty live marks [[ISS-0210]] found and [[ADR-0035]] disarmed. `gateMark` and `markGateRow` were deleted file-wide and this reached the same dialog through a shared row builder — **the guard was one call deep and so was the violation.** Exit criterion 1 was ticked over it for four review rounds.

And one in the tooling rather than the product: the declaration scanner **read its own docstring** as a coverage claim, because a `#` comment inside a string satisfies *"is this a comment"*. It uses `tokenize` and `ast` now.

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

## Independent review — fourth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `c9d6a82..9a75f11`; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all three earlier passes, recorded in `reviewed_by` as provenance rather than as a compliance token. Every count below was re-measured from the tree and every claim about behaviour was established by running the code, not by reading it. **This verdict supersedes the third pass's on this note.**

**Verdict: changes-requested — on two exit-criterion sentences, and on nothing else. The phase can close.** Round three broke nothing, its five findings are fixed and I verified each by execution rather than by reading, the membership and the statuses are exactly as claimed, and no criterion fails behaviourally. What I refuted is narrower and is the same defect the phase exists to name: **two of the five ticked criteria are written wider than the guards they cite, and I constructed a passing counter-example for each.** Fix the two sentences — or widen the two guards — and there is nothing outstanding.

### The headline question: did fixing round three break anything

**No.** Test functions were extracted by name, file by file, at `f5ca55b`, `c9d6a82` and `9a75f11` and the sets diffed. `c9d6a82..9a75f11` **removes nothing**: three functions are added to `tests/test_observed_coverage.py` and no other file changes its set, 1835 → **1838**. Across the whole phase range `f5ca55b..9a75f11` the only removals anywhere are the seven `covered_by:`/promotion tests in `tests/test_checks_view.py`, each replaced in the same file by one guarding the mechanism's absence — that file's count is unchanged at 22 — so 1761 → 1838 with a net `+77` accounted for entirely by five new files (6 + 31 + 17 + 13 + 10).

**The emitter was run in loops rather than read.** Twelve scenarios against a temporary repo, counting ledger entries: `pass` then four `<skipped/>` runs → **2** entries (one `pass`, one invalidation); three skipped runs with no standing verdict → **0**; `pass`, skip, then three passing runs → **3**; declaration deleted, four runs → **2**; declaration moved to another file under the same name, four runs → **1**; moved *and* renamed, four runs → **1**; a `.kt`-declared check across five `.py` runs → never invalidated; `pass` then five failing runs → **2**; a passing sibling with a skipped sibling, four runs → **2**; a `manual` verdict under four skipped runs → **1** (untouched); a `manual` verdict under four failing runs → **2**. Every one is bounded, and the bound is structural: `resolve()` pops an invalidated check out of `verdicts()`, so both the `stale` and the `failing` branch leave the set by construction on the next run. Round three's finding 1 is genuinely closed.

**The three new tests are not passengers.** Reverting `elif seen and not held` to `elif seen` fails `test_a_skipped_sibling_is_not_laundered_into_a_pass` and nothing else. Restoring the round-two `stale` rule verbatim fails `test_a_skipped_test_invalidates_once_not_once_per_run` and `test_a_check_with_no_verdict_is_never_invalidated`. The two earlier repairs still hold their ground: `_withdrawn` returning `True` unconditionally fails the two toolchain tests, and returning `False` for a vanished declaration fails `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list`.

**Round three's finding 3 reproduces exactly, every figure.** Driving the rule's own predicates over `git archive f5ca55b`: **56** owed, **51** terminal, **5** non-terminal, `30 done / 8 merged / 4 implemented / 9 fixed`, earliest `review_date` **2026-07-30** on **eight** notes — `CHG-20260730-Two-Features-Closed`, `FEAT-0045`, `ISS-0037`, `ISS-0057`, `ISS-0068`, `ISS-0069`, `PHASE-011`, `PHASE-013`. All 8 `merged` findings are `CHG-*`. The rule reports 51 at HEAD.

**Suite, validator, CI step set, all observed rather than reported.** `2063 passed, 3 skipped` in 269s; `validate-docs: OK`; `--as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `9a75f11`.

### The phase's own claims, re-measured

- **97 children, all terminal, and the breakdown is right term for term.** Parsing `phase:` across every note under `docs/`: 97 name this phase — 11 `feature`, 9 `requirement`, 30 `issue`, 38 `task`, 1 `design`, 5 `change`, 3 ADR-type (1 `adr` + 2 `decision`) — summing to 97. Statuses: `done` 48, `fixed` 29, `implemented` 9, `merged` 5, `accepted` 4, `declined` 1, `superseded` 1. **Zero non-terminal.** Identical to the third pass's figures.
- **Criteria 3, 4 and 5 hold.** Criterion 5 is the one resting on the newest work and it is guarded on both halves — the payload assertion and a renderer guard that fails when the sentence is rewritten to a bare count. I re-ran the whole suite against them.

### Finding 1 (medium) — criterion 2 is written wider than its guard, the third pass said so, and the sentence is unchanged

The criterion reads *"guarded by `test_no_surface_brackets_a_raw_mark_rather_than_its_glyph` — **which fails if any render site reads `mark` directly instead of going through `MARK_GLYPH`**"*. Both mark guards are regexes over template-literal interpolation: `` `[${…mark…}]` `` and `${….mark}`. Constructed — a render site added to `renderer.ts` doing `_t.title = String(c.mark); _t.textContent = String(c.mark);` — **all 38 tests in `tests/test_acceptance_marks.py` pass**. That is not a hypothetical shape: it is defect three of the three the guard's own docstring lists (*"a gate row's `title` said `TST-0123 — done` where the glyph had been"*). The third pass filed this under *"Residuals, recorded rather than requested"* and nothing was amended, so a ticked criterion still claims a universal the guard does not hold. In the phase whose thesis is *a claim written wider than the code*, that is the one place it should not survive to close-out.

### Finding 2 (medium) — criterion 1's universal form rests on a 2600-character window

The criterion opens **"No page whose subject is a release offers a control that changes a check."** `test_no_write_path_to_a_check_appears_on_the_release_page` takes `src.index("const heldBack = c.held_back")` and scans `src[i:i + 2600]` for three literals. `renderer.ts` continues for **469,293** characters past that anchor. Constructed: `btn.onclick = () => askForMark(row.note_id);` inserted at the first newline after the window — anchor **+2621**, twenty-one characters outside — and the test **passes**. The *deletions* the criterion also names are guarded properly and file-wide (`markGateRow` by a comment-stripped regex over the whole source, `gateMark` by two assertions in `test_tests_view.py`), so the sentence is true of what was removed and wider than what is guarded about what could be added. Either scope the sentence to the held-back block — which its own tail already does — or make the scan structural rather than a character count.

### Finding 3 (low) — the closing section's own arithmetic disagrees with itself again

*"### Four defects found while building"* is followed immediately by *"The pattern this phase kept meeting, met **three** more times on its last day:"* and then by four numbered items and a fifth in prose. The heading and item 4 were updated for round three and the sentence between them was not. Separately, round three's finding 2 — the skipped sibling laundered into a `pass`, a distinct defect in the `passing` computation rather than in the evidence-of-absence rule — appears in no entry of that list. This is the fourth consecutive round in which a count in this note was typed rather than counted, on the note that says *"the arithmetic is the check the eye is not"*.

### Finding 4 (low) — the `covered_by:` stranded-file set is declared closed for a third time and is not

`docs/references/TESTING-MODEL.md:110`, under the heading **"## What the cockpit implements today"**, still reads *"**Writes** — mark, *Needs re-check* …, ***Covered by*** and retire"*. `note_writes.cover_check` is deleted, so the cockpit implements no such write. Line 107 still lists a filter over `automation`. Lines 130, 133 and 137, under *"### Verified against the code, unchanged"*, make present-tense claims about `_resolve_coverage` and `cover_check` (*"All three hold"*). The section-level banner added by this range sits on **"## The automation path"** only, and its own words are *"a heading is a landing target, and a reader arriving by link or scroll never sees a warning further up"* — which is precisely the argument against leaving the other three headings unbannered. The file's top banner covers a different supersession (ADR-0034 / PHASE-036) and names none of these fields.


## Independent review — fifth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `9a75f11..991838e`, widened to `f5ca55b..991838e` for the did-anything-break question; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all four earlier passes, and `reviewed_by` records that as provenance rather than as a compliance token. Every claim below was established by running the code, mutating it, or counting the tree; none of it was established by reading a docstring and agreeing with it. **This supersedes the fourth pass's verdict on this note.**

**Verdict: changes-requested. The phase cannot close as it stands.** Two of the fourth pass's six findings are recorded as fixed and are not, one sentence in this note's `review_response:` is false about what the fix did, and — the two that matter — exit criterion 1 is refuted by the shipped product rather than by construction, and round four's repair of the emitter reintroduced the silent rot [[FEAT-0138]] was opened to end. **This supersedes the fourth pass's verdict**, which held that the phase could close once six sentences were corrected.

### The headline question: did fixing round four break anything

**Yes — once, and it is a silent-rot regression.** Test-function names were extracted per file at `f5ca55b`, `07602db`, `b635c39`, `c9d6a82`, `9a75f11` and `991838e` and the sets diffed. `9a75f11..991838e` **deletes nothing**: four functions are added to `tests/test_observed_coverage.py` and `test_it_does_not_push` is renamed to `test_the_emitter_does_not_push`, 1838 → **1841**; no other file changes its set. Round two's failure mode has not recurred. Round three's has: the repair moved the defect one branch over, which is now **four of the five rounds** in which the fix introduced something. Every earlier bound still holds — the emitter was run in loops against temporary repos and the ledger entries counted: `pass` then four skipped runs → **2**; three skipped runs with no standing verdict → **0**; declaration deleted, four runs → **2**; `pass` then five failing runs → **2**; a `.kt`-declared check across five `.py`-only runs → **1** (never invalidated); the declaring test renamed inside its own file, four runs → **1**. All five emitter mutants are caught: `_withdrawn`'s guard → `if False:` fails `test_one_check_gets_at_most_one_invalidation_per_run`; a bare-name fallback added to `_resolve`, and `_resolve` reduced to bare-name matching, each fail `test_two_tests_with_one_name_are_not_the_same_test` and `test_a_report_that_does_not_name_the_file_emits_nothing`; ignoring `classname` in `junit_results` fails 14 tests; `elif seen and not held` → `elif seen` fails `test_a_skipped_sibling_is_not_laundered_into_a_pass`. The claimed guards guard. The rule they guard is what changed underneath them.

### Finding 1 (high) — exit criterion 1 is refuted by the shipped product, not by construction

**"No page whose subject is a release offers a control that changes a check" is false at `991838e`, and the guard's own subject list is what makes it false rather than arguable.** `renderer.ts:7610`, inside `buildReleaseItemPage` — which the guard names in its `subjects` set — renders every acceptance-check row of `~release/<id>/<ITEM-ID>` with `s.appendChild(buildCheckRow(item))` and no `manual` argument, so `manual` defaults to `true` and each row gets **two live write controls**: `checkMark(item)` (`renderer.ts:9200`), a button whose click calls `markCheckRow` → `walkOneCheck` → `askForMark` → `postJson('/api/notes/mark-check', …)`, and a **Retire** button calling `retireCheckRow`. The page is routed at `renderer.ts:1249` off `~release/`, renders in `publication` nav mode, and its three lists — *Checks it originated*, *Checks it invalidated*, *Checks in its areas* — are real `GateItem` rows from `publication.release_item_payload`. The code says so in its own voice at `renderer.ts:7608`: *"The mark control INLINE — the same one the view and the gate wear, so a reader can walk a check from the page that told them it mattered"* — while `retireCheckRow`'s docstring twelve hundred lines later says the control *"lives on `~checks`, never on a release page ([[ADR-0035]])"*. Both cannot be true.

**Why the widened guard does not see it, established by mutation.** Inserting `void askForMark({});` into each of the eight `subjects` functions fails the test **8/8** — the widening works for a *direct* call. Inserting `wrap.appendChild(buildCheckRow(item));` into each of the same eight **passes 8/8**, including into `buildReleasePage` itself, which is the main release page. The guard is one call deep and the live violation is one call deep. [[ADR-0035]]'s harm is fully present on that page: the checks shown are the ones blocking, the row shows name and area and not the procedure, and the fastest way to clear them is to tick them there.

The narrower reading — that a per-item page's subject is a *feature*, not a release — does not rescue the criterion, because [[ADR-0035]] point 2 allows walking only on *"`~checks` and the check's own note — surfaces whose subject IS the check"*, and a feature page is neither. Either the criterion is false or the guard's `subjects` set is wrong about its own scope; the delivered artefact asserts both.

### Finding 2 (medium) — the criterion-1 guard's claims about itself are wider than the guard

Its docstring says *"The region is every release-page render function"* and *"Named rather than pattern-matched, so renaming one into existence outside this list is a visible edit here."* Neither holds. Constructed: a new `function buildReleaseChecksPanel(items: GateItem[])` whose rows call `askForMark`, inserted immediately before `renderReleasePage` → **17 passed**. `found == subjects` detects only the *disappearance* of one of the eight; a ninth is invisible, and the `^(?:async )?function` scan cannot see an arrow-function or exported surface at all. The functions the release pages actually delegate row rendering to — `buildCheckRow`, `checkMark`, `gateGroup` — are not in the set, which is the mechanism of Finding 1.

### Finding 3 (medium) — criterion 2's narrowing corrected the clause that was true and left the clause that was refuted

**The narrowing argument itself is sound and I verified it.** `renderer.ts:9520` reads ``if (withMark && item.mark) bits.push(`marked ${markWord(item.mark)}`);``, set on the two gate groups at 8500 and 8548 where the mark varies, and `markWord` reads `MARK_TITLE[mark]` rather than echoing the stored value. So a rule forbidding the mark *word* on every surface really would forbid what replaced the disarmed glyph. That part is not a weakening to fit.

**But the clause the fourth pass actually refuted survives nearly verbatim.** It read *"which fails if any render site reads `mark` directly instead of going through `MARK_GLYPH`"*; it now reads *"which fail if a render site reads `mark` instead of going through `MARK_GLYPH`"*. Re-constructed the same counter-example inside `buildCheckRow` — `_t.title = String(item.mark); _t.textContent = String(item.mark);` — and got **38 passed**, with the control `` row.title = `${item.mark}` `` giving **1 failed, 37 passed**. Both guards scan only template-literal interpolations of `.mark`; a non-interpolated read walks past. The clause also understates the guards in the other direction, since they permit `MARK_TITLE` and `markWord` as well as `MARK_GLYPH`.

**And `tests/test_acceptance_marks.py` is byte-identical across the entire phase range `f5ca55b..991838e`** — which makes this note's own fourth `review_response:` sentence, *"Both narrowed to what is true and **both guards widened to the whole release region**"*, false twice: neither mark guard was touched, and the one guard that was widened was widened to eight named functions scanned one call deep, not to a region.

### Finding 4 (high) — round four's emitter fix reintroduced silent rot, which is the defect FEAT-0138 exists to end

Detailed on [[FEAT-0138]] / [[REQ-0057]] / [[TASK-0543]]. In one line: `_resolve` now requires the report's `classname` to identify the declaration's own file, and a declaration it cannot match is routed into the same bucket as *absent from this run* — so a check with a standing `method: automated` `pass` whose declaring test becomes unmatchable is **never invalidated and never re-observed**, forever, with the emitter printing *"nothing changed"*. Measured: at `9a75f11` a declaring test inside a pytest class emitted `pass TST-0001`; at `991838e` the same input emits nothing, and four further runs after the refactor leave the ledger at one `pass` entry and the verdict standing. `FEAT-0138`, `REQ-0057` and `TASK-0543` are at terminal status carrying it.

### Finding 5 (medium) — the bare-name collision is narrowed to a basename collision and is now order-dependent

Detailed on the same three notes. Constructed: `tests/test_thing.py` declaring and `integration/test_thing.py` not, both with `test_the_thing` — the non-declaring twin failing and listed first invalidates the check; the same two entries in the opposite order do nothing. Identical inputs, opposite verdicts, decided by XML ordering.

### What the fourth pass asked for, checked one by one

- **Finding 1 (mark criterion)** — *partially fixed*; see Finding 3 above.
- **Finding 2 (2600-character window)** — *fixed in mechanism, not in reach*; the window is gone and the eight named functions are scanned with comments stripped, but see Findings 1 and 2 above.
- **Finding 3 (arithmetic)** — *not fixed*; see Finding 6 below.
- **Finding 4 (`TESTING-MODEL.md`)** — *partially fixed*; the banner is in `## What the cockpit implements today`'s first line and names `covered_by:`, `automation:`-as-coverage, `_resolve_coverage` and *Covered by*, but the two statements themselves sit under `### Verified against the code, unchanged` (line 136, *"All three hold"*) and `### Refuted` (line 143, present tense about `note_writes.cover_check`), and neither heading carries a banner. The argument for putting one on this section is the argument for putting one on those.
- **The two emitter findings** — *fixed as stated and broken elsewhere*; see Findings 4 and 5.

### Finding 6 (low) — the defect-list arithmetic is wrong for the fifth consecutive round

The heading reads *"Six defects found while building"*; the sentence under it reads *"met **six** more times on its last day — **five in the product and one in the tooling**"*; the list that follows has **six numbered product defects** and then *"And one in the tooling…"*. Six plus one is seven, and the product count is six, not five. Both the total and the breakdown are false, on the note that says *"the arithmetic is the check the eye is not"* and has now said it through five rounds of getting it wrong. Counted, not read: items 1–6 are `Remove` unreachable, the `~release/next` subtraction, the invalidation set computed from declarations, the laundered skipped sibling, the bare-name identity, and the evidence-of-absence rule; the scanner reading its own docstring is the seventh.

### The `review_response:` chain

Six notes now carry four rounds joined by `||`, and as a record of what each round claimed the chain is accurate and in order. One sentence in it is not: this note's fourth entry says *"both guards widened to the whole release region"*, and `tests/test_acceptance_marks.py` is untouched across the whole phase range while the guard that did change covers eight named functions one call deep. *"All six findings fixed"* is the same overstatement at the summary level.

**Suite, validator, CI step set — observed, not reported.** `.venv/bin/python -m pytest -q` → **2066 passed, 3 skipped** in 269s (a second full run with `--junitxml` gave the same). `bash tools/scripts/validate-docs.sh` → `validate-docs: OK`, warnings only (16 `FEATURE-UNCOVERED`, one `PATH-ALIAS` over 174 items, two `REVIEW` on `TST-0011`/`TST-0026`). `--as-committed` → *"HEAD passes the full CI step set"*: validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `991838e`.

### Can this phase close

**Not as it stands, and the gap is two things rather than a list.** The membership is exactly as claimed — 97 notes name this phase (11 feature, 9 requirement, 30 issue, 38 task, 1 design, 5 change, 3 ADR-type, summing to 97; statuses 48 `done`, 29 `fixed`, 9 `implemented`, 5 `merged`, 4 `accepted`, 1 `declined`, 1 `superseded`, **zero non-terminal**) — and criteria 3, 4 and 5 hold, criterion 5 including the held-back block's reason column and its honest *"no reason recorded (hand-edited)"* fallback for a hand-edited `features:`. What blocks the close is that **exit criterion 1 is false about the shipped product** (Finding 1) and that **three terminal notes carry an emitter regression introduced by the last repair** (Finding 4). Findings 2, 3, 5 and 6 are corrections to sentences and can ride along.

The phase's own thesis is that a claim written wider than the code is the defect. Criterion 1 is that defect in the product rather than in the prose, and it was found by following a call rather than by grepping a name — which is the sixth time this phase has recorded that a state asserted from a grep was wrong.


## Independent review — sixth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `991838e..c4413e3`, widened to `f5ca55b..c4413e3` for the did-anything-break question; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all five earlier passes, and `reviewed_by` records that as provenance rather than as a compliance token. Every figure below was produced by running the code, mutating it, or counting the tree; none of it by reading a docstring and agreeing with it. **This supersedes the fifth pass's verdict on this note.**

**Verdict: changes-requested — and both of the fifth pass's blockers are genuinely gone.** Exit criterion 1 is now true of the shipped product, established by following every call out of every release surface rather than by grepping a name, and the emitter's silent-rot trigger is fixed with the residual state announced. What holds the phase is smaller and newer: **the repair for F1 replaced a live write control with a false statement, on the same rows, in the same commit** — and the defect-list arithmetic on this note is wrong for the fourth consecutive round, in the sentence that says *"Counted this time"*.

### The headline question: did fixing round five break anything

**Yes — once, and it is an accuracy regression rather than a write path.** Test-function names were extracted per file at `f5ca55b` and `c4413e3` and the sets diffed: `991838e..c4413e3` **deletes nothing**, adds four functions to `tests/test_observed_coverage.py` (six collected cases, since one is parametrised three ways) and touches no other file's set — 1841 → **1845** functions, suite 2066 → **2072**. Round two's failure mode has not recurred. The emitter was run in loops against temporary repos with the entries counted rather than reasoned about: six identical passing runs → **1** append then stable at 37; four consecutive failing runs → **1** invalidation then stable; `pass` → `fail` → `pass` → `pass` → three transitions, **three** entries. No unbounded growth anywhere. What broke is on the release page, and it is Finding 1.

### Finding 1 (medium-high) — the release item page stopped offering a false control and started making a false statement

`buildCheckRow(item, false)` disarms the mark button and the `Retire` button, which is the fix and it works. It also takes the **other** branch of every `if (!manual)` in that function: the row gains the class `is-automated`, and the body gains `checks-row-command` with `item.command || 'automated'`. **Every acceptance check in this repo is manual** — 34 of 34 carry no `command:` — so on `~release/<id>/<ITEM-ID>` each row now says the literal word **`automated`** under its description and wears the class whose own CSS comment reads *"An automated check's row ([[ADR-0039]]). It carries the command that executes it INSTEAD OF a checkbox."*

**Constructed, not inferred.** `buildCheckRow` was lifted out of `desktop/dist/renderer/renderer.js` and executed under a DOM shim. The same manual check, both ways: `buildCheckRow(item, true)` → mark control, `Retire`, no command line; `buildCheckRow(item, false)` → `<div class="checks-row is-automated">` … `<div class="checks-row-command mono"> "automated"`. Then counted against the real corpus: `publication.release_item_payload` was built for all **143** features in this repo and **67** rows across *Checks it originated* / *invalidated* / *in its areas* have no `command:` and therefore now print that word.

**The flag belongs to the item and this call hard-codes it.** `paintCheckList` derives `manual` from the section it is painting — the partition that exists precisely because some checks are machine-executed and some are not. `buildReleaseItemPage` has no such partition and passes `false` for all of them. The fallback's own comment, four lines away, says *"the fallback should never fire — a section is non-manual BECAUSE its checks carry a `command:` — so what it prints is a statement about broken data, and it must not be a claim about CI"* ([[ISS-0241]]). It fires on every row of that page now.

This falsifies no ticked criterion — criterion 1 is about **controls** and criterion 1 now holds. It is a new instance of the thing the phase was opened to remove, written by the commit that closes it, which is why it is reported here rather than filed and waved past.

### Finding 2 (medium) — the widened guard forbids spellings, not the property, so the same defect recurs under a different variable name

`forbidden` names `buildCheckRow(item)`, `buildCheckRow(item,\n` and `buildCheckRow(row)`. Three mutants planted in `buildReleasePage`, each of which re-arms both the mark dialog and `Retire` on the main release page, and each of which the guard **passes**:

- `wrap.appendChild(buildCheckRow(item, true));`
- `const manual = true; … buildCheckRow(item, manual);`
- `const c = …; buildCheckRow(c);` — **the identical defect to F1 with one letter changed.**

The positive assertion added beside it, `assert "buildCheckRow(item, false)" in src`, is scanned over the whole 470,000-character file rather than over the release region, so it stays satisfied by the one legitimate call while a live one sits next to it. The property the rule wants is *no `buildCheckRow` call in a release region whose second argument is not `false`*; what is written is a list of three ways of spelling one call. Two further constructions the guard cannot see, both honestly scoped in its own comment and neither guarded: a release surface whose name omits *release* (`function buildShipmentPage` calling `askForMark` → passes), and an arrow-function surface (`const renderReleaseDrawer = async () => { await askForMark(); }` → passes, because the scan is `^(?:async )?function`).

**What the widening did close, verified by mutant:** reverting to `buildCheckRow(item)` fails it; planting `retireCheckRow(` inside `buildReleaseItemPage` fails it; adding `function buildReleaseChecksPanel` calling `askForMark` fails it on the discovered-set assertion. Three for three, including the exact regression it was written for.

### Finding 3 (medium) — the emitter's bold tier-precedence claim is guarded by nothing, and reversing it changes answers

`_resolve`'s docstring says, in bold, *"Tier 1 must be exhausted before tier 2 is consulted."* Swapping the two blocks so tier 2 is consulted first passes **all 43** tests in `tests/test_observed_coverage.py` and the whole 2072-test suite. The reversal is not cosmetic: for a declaration nested in a class (`classname="tests.test_thing.TestGroup"`) with a same-named test elsewhere that **failed**, the shipped order emits `pass TST-0001` and the reversed order emits nothing — and against a check carrying a standing verdict it would invalidate off the wrong file's failure. `test_two_files_with_one_stem_are_not_order_dependent` does not reach this: its twin pair **ties in tier 2** and falls through to tier 1 either way round, so it demonstrates the tie rule and is silent about precedence.

### Finding 4 (medium) — the tie-refusal is guarded in tier 2 and unguarded in tier 1, which is F3's own defect one tier up

Mutating `if exact: return None` to `return exact[0]` passes the entire suite. Constructed: `tests/test_thing.py` declaring `TST-0001`, the report holding `tests.test_thing.TestA` (passed) and `tests.test_thing.TestB` (failed) — two classes in one module, an ordinary pytest shape. As shipped, both orders refuse and print `NOT ATTRIBUTED`, which is correct. With the mutant, `pass TST-0001` in one order and *"nothing changed"* in the other: **identical inputs, opposite verdicts, decided by XML ordering** — the sentence the fifth pass's F3 was filed under, now true of the tier the fix left unpinned. Two adjacent rules are also unguarded: dropping the dot from the tier-1 prefix test (so `tests/test_a.py` matches `classname="tests.test_abc"`) and loosening tier 2 from *last component* to `endswith` (so `com.x.MyFooTest` matches a declaration in `FooTest.kt`) both pass everything.

### Finding 5 (low) — the defect-list arithmetic is wrong for the fourth consecutive round, in the paragraph claiming it was counted

The heading reads *"Seven defects found while building"*; the sentence under it reads *"met **seven** more times on its last day — **six in the product** and one in the tooling"*; the numbered list beneath now runs **1 to 7**, all of them product defects, and is followed by *"And one in the tooling rather than the product"*. Seven product plus one tooling is **eight**, and the product count is seven, not six. The fifth pass's F6 was answered by appending item 7 and renaming *six* to *seven* without re-reading the breakdown — which is the same edit that produced the previous three errors. The parenthetical now says *"**Counted this time**, and the count is the check the eye is not"*, and it was not counted this time either.

### Finding 6 (low) — one docstring was falsified by its own commit

`tools/scripts/emit-coverage.py:121` still says `plan` returns `(passing, failing, stale, current)`. This commit changed it to return five values. Nothing reads the docstring, and that is the point: it is a claim about the code, in the code, made false by the change beside it.

### Finding 7 (low) — `NOT ATTRIBUTED` reaches stdout and nothing else

Measured: a check observed `pass`, then six consecutive runs in which its declaring test is present but unattributable. Every run prints the notice, every run also prints *"nothing changed (0 check(s) observed passing)"*, the exit code stays **0**, the ledger stays at **one** entry, and `verdicts()` keeps returning `mark='pass', method='automated'`. Nothing in the record and nothing on any surface can tell a reader that the check stopped being observed. The notes claim only that the state is *reported rather than guessed*, which is true, so this is a residual rather than a false claim — but it is the half of the fix that this phase's own thesis says has to exist, and it does not yet.

### Finding 8 (trivial) — the two new banners are byte-identical and one cites a sentence from the other's section

`docs/references/TESTING-MODEL.md:145`, under `### Refuted`, ends *"**All three hold**" held; it does not now"* — and *"All three hold"* is at line 138, under `### Verified against the code, unchanged`. The banner is right about the section it names and is quoting the neighbouring one. Also: the file carries `review_verdict: changes-requested` and **no `review_response:` at all**, though F7's fix was applied to it — the mechanism [[ISS-0253]] built inside this phase, unused on the one note in this range it was made for.

### What survived refutation

- **Exit criterion 1 is now true, and completely so.** `buildCheckRow` has exactly two callers in `renderer.ts` — `paintCheckList` (the `~checks` page, legitimate under [[ADR-0035]]) and `buildReleaseItemPage` (now read-only) — and `checkMark`, `markCheckRow`, `walkOneCheck`, `askForMark` and `retireCheckRow` are reachable only through it. The five other helpers a release surface calls directly (`gateGroup`, `gateLine`, `gateNote`, `buildRecordRow`, `buildRecordCard`) contain no write path at all. There is no second surface reaching a verdict write through a shared helper.
- **The emitter's three tiers work on real output, not only on fixtures.** The declaring files were run with `--junitxml` and the emitter driven over the report: `pass TST-0069` (all five declaring tests), `pass TST-0075`, `pass TST-0076`. pytest writes `classname="tests.test_close_out_commit"`; tier 1 matches exactly. A test nested in a class resolves; `com.x.FooTest`, bare `FooTest` and `src.test.kotlin.com.x.FooTest` all resolve; parametrised names are stripped to the function before matching. **Round four's resolver, reinstated as a mutant, fails three named tests.**
- **Criterion 2's correction is true.** `tests/test_acceptance_marks.py` is byte-identical across `f5ca55b..c4413e3`, collects **38** tests, and `_t.textContent = String(item.mark)` planted in `buildCheckRow` passes all 38 — so *"which enumerate the render sites they know and are not universal"* is exactly the right width, and the retracted `review_response:` sentence was retracted correctly.
- **The membership is exactly as claimed.** 97 notes carry `phase: [[PHASE-037…]]` — 38 task, 30 issue, 11 feature, 9 requirement, 5 change, 3 ADR-type, 1 design — and 48 `done`, 29 `fixed`, 9 `implemented`, 5 `merged`, 4 `accepted`, 1 `declined`, 1 `superseded`. **Zero non-terminal.** Criteria 3, 4 and 5 re-verified and hold.
- **The `review_response:` chains are accurate.** Five rounds joined by `||` on [[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]], [[FEAT-0138]], [[REQ-0057]], [[TASK-0543]] and `CHG-20260821-Coverage-Is-Observed-Not-Declared`; [[FEAT-0142]] and [[TASK-0576]] carry their first, having been approved through the fourth pass. Each entry describes what that round changed, and the fifth entries are true of the diff.

**Suite, validator, CI step set — observed, not reported.** `.venv/bin/python -m pytest -q` → **2072 passed, 3 skipped** in 272s. `bash tools/scripts/validate-docs.sh` → `validate-docs: OK`, **zero errors** and 344 warnings (16 `FEATURE-UNCOVERED`, one `PATH-ALIAS` over 174 items, two `REVIEW` on `TST-0011`/`TST-0026`, the rest pre-existing). `--as-committed` → *"HEAD passes the full CI step set"*: validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `c4413e3`.

### Can this phase close

**Nearly, and not on this commit.** Every exit criterion is now true of the code, the membership is 97 terminal notes with nothing outstanding, and the two things the fifth pass blocked on are fixed rather than argued away — the release item page offers no control that changes a check, and I proved that by walking the call graph rather than by trusting the guard. What stops it is one line: the same edit that removed the false control put a false label in its place, on 67 real rows, and *"a surface must not say more than is true"* is the sentence this phase exists to enforce. Finding 1 is a one-line change with a guard; Findings 2, 3 and 4 are guards that do not guard rules their own comments assert in bold, and can be filed rather than fixed here; Findings 5 to 8 are sentences.

The phase can close the moment a release item row stops calling itself automated. Nothing else in `991838e..c4413e3` blocks it.
