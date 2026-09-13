---
type: "[[phase]]"
id: PHASE-043
aliases: ["PHASE-043"]
title: "The walk page — the publication view hands the owed checks over as a procedure"
status: done
order: 43
owner: user:edwin
created: 2026-09-13
updated: 2026-09-13
goal: "When a release is in preparation, the publication view gives the person walking it one page that says what to do and in what order: the surfaces the release changed first, then every owed check inside the sitting it belongs to, with its setup, steps and expected result on the page, and a tick that writes the ledger."
features:
  - "[[FEAT-0149-The-Walk-Page]]"
requirements: []
tasks:
  - "[[TASK-0618-The-Walk-Payload]]"
  - "[[TASK-0619-The-Walk-Page]]"
  - "[[TASK-0620-The-Survey]]"
  - "[[TASK-0621-The-Release-Rung-Points-At-The-Walk]]"
issues: []
related:
  - "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
  - "[[PHASE-038-A-Verdict-Is-An-Event]]"
  - "[[FEAT-0102-Publication-Becomes-A-View]]"
  - "[[FEAT-0114-The-Suite-Is-A-View]]"
  - "[[ADR-0036-The-Sweep-Is-Withdrawn]]"
  - "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]"
  - "[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]"
  - "[[TASK-0449-Order-The-Walk-By-Its-Setup-Cost]]"
  - "[[DES-0012-Tests-In-Two-Flows]]"
tags: [acceptance, publication, walk]
---

# The walk page

## Goal

A person preparing a release should open one page and know what to do next. Today the cockpit tells them what is owed and lets them record a verdict, and nothing in between. `~checks` is the suite as a list ([[FEAT-0114-The-Suite-Is-A-View]]), ordered section, then area, then id, with owed rows floated to the top of their area. The release page reports the gate and lets a release settle scope ([[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]], [[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]). Neither says which check to walk first, what has to be on the bench before a sitting starts, or which screens a release changed. Edwin, 2026-09-13: *"I find it increasingly difficult to understand what steps need to be done to satisfy the outstanding acceptance tests"*, and *"one thing I notice the tests do not suggest me doing is to look at the changed screens at all, which is strange because that is normally the first step I would do."*

This phase adds the layer between the list and the ledger. Test practice has a name for it: ISO 29119-3 calls it a test procedure specification, the test cases of a set in execution order with their start-up and wrap-up. Test tools call the per-release instance a test run, a test execution or a test cycle. Session-based testing puts a survey session first, a look at the product before any scripted check. project-os names the same things in its own vocabulary, stated once upstream in project-os-dev (TESTING.md, "The walk"). A **walk** is the existing verb for executing an acceptance check. A **walk sheet** is the owed checks for one release and one platform, in the order a person should walk them, each with its procedure inline. A **sitting** is a group of checks sharing one setup state. The **survey** is the sheet's first section: the surfaces the release changed. The **walk order** is one authored file per consumer repo, `docs/tests/acceptance/WALK.md`, listing the sittings in product-state order.

The cockpit's job in this phase is to render that sheet inside the publication view, from the data model the template ships, and to let the walker tick as they go.

## Why this is a phase and not a task in PHASE-034 or PHASE-037

The repo's rule (CLAUDE.md, "When to open a phase") asks two questions.

**Can the goal be stated without listing its parts?** Yes. The paragraph above states it as a property of the publication view: a person opens one page and knows what to do next.

**Are the exit criteria something other than "the tasks are done"?** Yes. They are measurements against `your-trainer`'s live corpus and against the ledger, listed below.

**Why not PHASE-034.** PHASE-034 built publication as a view and attached the gate to the release rung. It closed on 2026-08-16 and it was closed four times. Its cancelled task [[TASK-0449-Order-The-Walk-By-Its-Setup-Cost]] is the nearest thing to this work, and the reason it was cancelled is the reason this is a phase and not that task revived: TASK-0449 wanted to infer the order from burden tags in prose, and this work has the order authored once, in the consumer's WALK.md. That is a different mechanism with a different owner.

**Why not PHASE-037.** PHASE-037 is the checks page and its defects. The walk page is a third surface beside `~checks` and the retired stepper, not a fix to either. [[TASK-0465-One-Walk-Layer]] measured why the list and the stepper do not converge, and the same measurement says the sheet is neither.

This justification is reversible: if the payload turns out to be a filter over `view_payload` and the page a variant of `buildChecksPage`, fold the work into PHASE-037 and supersede this phase.

## Scope

- One payload, `acceptance.walk_payload`, whose rows are exactly `ledger.owed` for the platform, grouped into the sittings WALK.md names, with a survey section derived from the ledger's invalidation events.
- One page, `~walk/<platform>`, inside the publication view, reached from the release rung.
- Each row carries the check's Setup, Steps and Expect inline, or says the setup is not stated.
- A tick is the existing mark dialog and writes a ledger event. The page never reorders as the walker ticks, and it remembers where the walker was.
- The release page and the checks page link into the walk while a release is `draft`.
- The ordering and survey rules are implemented once, in the template's module, and the cockpit bundles that module. Template-owned surfaces land upstream first ([[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]] decision 6, carried by [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]).

## Out of Scope

- **A second store.** The sheet is a rendering of the ledger and the notes. No file records "the checks for this release" ([[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]).
- **A stepper.** The retired runner advanced one step at a time and recorded results in a batch at the end. The walk page is a list that carries the procedure; a verdict is per row and immediate, as on `~checks`.
- **Inferring order from prose.** No burden tags, no keyword scan of the procedure. Order comes from WALK.md or it is id order labelled as such.
- **Time estimates.** No minutes anywhere on the page or in the payload, the guard rail TASK-0449 wrote and this phase keeps.
- **A new close-out obligation.** The survey reads invalidation events the ledger already holds. Nothing asks an agent a new question at close-out; that is what [[ADR-0036-The-Sweep-Is-Withdrawn]] withdrew and this phase does not reintroduce it.
- **The walk order itself.** WALK.md is authored in the consumer repo. `your-trainer` writes its own from its hand-kept run plan; this phase only reads it.

## Exit Criteria

- [x] On `your-trainer` with the Android ledger open, the walk payload's row set equals `ledger.owed("android", <manual checks>)` exactly, asserted by a test that computes both and compares them. — `tests/test_walk_payload.py::test_the_live_corpus_row_set_equals_ledger_owed`, 39 rows, no duplicates, no payload errors.
- [x] The survey section for `your-trainer`'s open Android release names every surface whose owed checks carry an invalidation event, and for each names the change or task ids that invalidated them. Checked by comparing against `ledger.events_by_check` directly. — `tests/test_walk_survey.py::test_the_live_survey_equals_the_ledgers_own_invalidations`; six surfaces and eleven task ids at the time of writing, both sides computed rather than pinned.
- [x] A walker can tick a row on `~walk/android`, and the same verdict is what `~checks` and the release gate show next, with no second write path. Checked by one walk recorded in a `TST-*` note for this phase. — [[TST-0088-The-Walk-Page-Hands-Over-The-Owed-Checks]], steps 7-9. **On `macos` rather than `android`**: the Android ledger is `your-trainer`'s record and writing a verdict into it to satisfy a criterion here would be this repo marking another repo's homework. The tick was recorded on this repo's own ledger, through the same path, and the property the criterion is about — one write path, the verdict on `~checks` and gone from the gate — was checked there.
- [x] `grep -n "minute\|duration\|estimate" src/project_os_cockpit/acceptance.py desktop/src/renderer/renderer.ts` returns nothing inside the walk payload or the walk page. — `acceptance.py` returns nothing at all. The renderer returns **one** hit, in the comment that states the rule: *"no minutes, no estimate, no schedule"*. Two tests hold the substance rather than the grep: one walks the payload for a banned key at any depth, one reads the whole of every walk function in the renderer with its comments stripped.
- [x] `tools/scripts/sync-project-os.sh ../project-os` reports the bundled walk module as identical to upstream, or the reason it cannot be is written in [[FEAT-0149-The-Walk-Page]]. — The sync reports no difference on `tools/scripts/walk-sheet.py`, and `tests/test_walk_bundle.py` asserts `walk_sheet_bundled.py` is byte-identical to it. The one adaptation the sidecar needs is made by seeding a global at the call site, not by editing the copy.

## Notes

- **Hard ordering constraint.** The template module (project-os-dev FEAT-0029, `tools/scripts/walk-sheet.py`) must exist upstream before [[TASK-0618-The-Walk-Payload]] bundles it. Until it lands, the cockpit can prototype the payload behind the same function signature, but the ordering and survey rules are not the cockpit's to decide.
- **Second constraint.** The Setup, Steps and Expect headings a row renders are project-os-dev ADR-0027's shape, which is `proposed` and unimplemented in the template as of 2026-09-13. A row whose note lacks them shows "Setup: not stated" and links to the note. That is the intended state for most of the corpus on day one; the shape is rewritten on contact, never swept.
- **What the corpus looks like today.** `your-trainer` hand-maintains a 719-line `docs/tests/ACCEPTANCE_RUN_PLAN.md`, marked temporary, with 315 rows addressed into a document deleted in the notes migration and five `TST-*` ids in the whole file. Its twelve phases, ordered as a state machine over tier upgrades and device wipes, are the walk order this page will render once they are written as WALK.md. Two earlier versions of the same plan are retired. The need has been met by hand three times and thrown away each time.

## Closed 2026-09-13

Four tasks `done`, one acceptance check walked, one change note ([[CHG-20260913-The-Walk-Page]]), four new rows in the capability register.

**The justification this note offered to reverse was not taken up.** It said: if the payload turns out to be a filter over `view_payload` and the page a variant of `buildChecksPage`, fold the work into PHASE-037 and supersede this phase. Neither happened. The payload is a join of three sources — `ledger.owed`, the note bodies and an authored `WALK.md` — and shares only `_row` with `view_payload`; the page reuses `buildCheckRow` and none of `buildChecksPage`, which is filters and facets the walk deliberately has neither of.

**Two upstream defects came out of the work** and are parked under [[PHASE-999-Future]] because they belong in another repository: [[ISS-0303-The-Walk-Sheet-Lists-Retired-Checks]] and [[ISS-0304-The-Walk-Order-Reader-Splits-Inside-A-Quoted-String]]. Both were found by running the template's generator beside this page on one corpus, which is the check the bundling decision was taken to make possible.
