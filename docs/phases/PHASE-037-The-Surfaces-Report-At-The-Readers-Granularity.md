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
review_response: "2026-08-21: the count was wrong three ways and is now measured - 97 children, and the breakdown adds up. All seven findings across the range are fixed; see the response on each note."
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

### Three defects found while building, each of them a rule that could not fire

The pattern this phase kept meeting, met three more times on its last day:

1. **`Remove` on the release page was unreachable.** It is guarded on `c.kind !== 'derived'` and a test pinned that guard — and `publication.py` never emitted a third kind, so a feature could be added through the front door and never taken back out through it.
2. **The gate's subtraction could not fire on `~release/next`.** The selection was read with `index.by_id(release_id)`, and `release_id` is the literal `"next"` on the page a person opens.
3. **The coverage emitter's invalidation set was computed from the declarations**, so deleting the test — which deletes the declaration — removed the check from the set that could be invalidated. `covered_by:`'s silent rot, reproduced inside the tool built to end it. Its test **failed on first run**, which is the only reason it is not still there.

And a fourth, in the tooling rather than the product: the declaration scanner **read its own docstring** as a coverage claim, because a `#` comment inside a string satisfies *"is this a comment"*. It uses `tokenize` and `ast` now.

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
