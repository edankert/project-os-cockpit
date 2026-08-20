---
type: "[[phase]]"
id: PHASE-037
aliases: ["PHASE-037"]
title: "The release page and the tests view report at the granularity the reader is working at"
status: active
order: 37
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
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
issues: ["[[ISS-0210-The-Release-Page-Offers-Sixty-Live-Marks]]", "[[ISS-0211-The-Mark-Picker-Shows-Words-Where-The-Check-Mark-Was]]", "[[ISS-0212-Retired-Documents-Render-As-Verified-Tests]]", "[[ISS-0213-Acceptance-Tests-Carrying-Level-System]]", "[[ISS-0214-A-Note-Whose-Id-Contradicts-Its-Filename]]", "[[ISS-0222-The-Left-Pane-Groups-By-Tier-And-Nothing-Else]]", "[[ISS-0223-The-Bar-Is-The-Wrong-Instrument-In-The-Editor]]", "[[ISS-0224-The-Positional-Address-Outlived-The-Document]]", "[[ISS-0225-A-Nav-Row-Carries-Data-No-Renderer-Draws]]", "[[ISS-0226-A-Surface-Wears-A-Test-Status]]", "[[ISS-0227-Every-Surface-Links-To-The-Same-Place]]", "[[ISS-0228-The-Test-Id-Renders-Twice-On-A-Row]]", "[[ISS-0229-Steps-Proven-Is-Sent-And-Nothing-Draws-It]]", "[[ISS-0231-The-Surface-Row-Is-Two-Lines-And-Names-The-Wrong-Thing]]", "[[ISS-0232-A-Check-Row-Shows-A-Status-It-Cannot-Hold]]", "[[ISS-0233-Migration-Provenance-Outlives-Its-Migrations]]", "[[ISS-0234-The-Generated-Page-Repeats-Itself]]", "[[ISS-0235-A-Surface-Wore-Its-Features-Title]]", "[[ISS-0241-The-Section-Head-Restates-Its-Own-Arithmetic]]", "[[ISS-0242-Two-Different-Things-Are-Both-Called-Automated-Tests]]", "[[ISS-0243-The-Automated-Checks-Page-Is-A-Walk-Page]]", "[[ISS-0244-The-Gate-Rows-Wear-A-Mark-That-Does-Nothing]]", "[[ISS-0245-A-Verdict-On-An-Accepted-Note-Is-Owed-Forever]]", "[[ISS-0246-The-Two-Front-Doors-Are-Not-Comparable]]", "[[ISS-0247-The-Tests-View-Lost-Its-Quiet-Group]]", "[[ISS-0248-Two-Predicates-Disagree-About-Not-In-Flight]]", "[[ISS-0249-Two-Check-Write-Paths-Reach-No-Front-Door]]", "[[ISS-0250-A-Surface-Rename-Silently-Orphans-Its-Checks]]"]
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

## Exit criteria

- [ ] **No page whose subject is a release offers a control that changes a check.** [[ADR-0035]]. `gateMark`'s `actionable` parameter is deleted, not defaulted.
- [ ] **A rendered mark is a glyph on every surface**, guarded by a test that fails if any surface emits a raw word.
- [ ] **Every row in the tests view is a test** — no retired documents, and every acceptance test routed by its `level:` rather than by which directory it sits in.
- [ ] **The tests view opens on what is owed.** An inventory is reachable and is not what the reader lands on.
- [ ] **A release can name its own contents**, and the gate can be scoped to them.

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
