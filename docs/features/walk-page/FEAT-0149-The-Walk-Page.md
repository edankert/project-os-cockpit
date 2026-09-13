---
type: "[[feature]]"
id: FEAT-0149
aliases: ["FEAT-0149"]
title: "The walk page — the owed checks as a procedure, survey first, sittings in the consumer's order, the steps on the page"
status: done
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-13
updated: 2026-09-13
source: ["Edwin, 2026-09-13: 'I find it increasingly difficult to understand what steps need to be done to satisfy the outstanding acceptance tests, so I am wondering is there another thing we need to create on-top of the actual tests, which goes through the things that I should be doing to satisfy these tests in a logical order'", "Edwin, 2026-09-13: 'one thing I notice the tests do not suggest me doing is to look at the changed screens at all, which is strange because that is normally the first step I would do'", "Survey of your-trainer, project-os and project-os-cockpit, 2026-09-13: three run plans written by hand and thrown away, none addressable"]
goal: "Give the person walking a release one page in the publication view that lists every owed check in the order the consumer repo authored, with the surfaces the release changed first and each check's setup, steps and expected result on the page, so the walk is read top to bottom and every tick lands in the ledger."
requirements: []
tasks:
  - "[[TASK-0618-The-Walk-Payload]]"
  - "[[TASK-0619-The-Walk-Page]]"
  - "[[TASK-0620-The-Survey]]"
  - "[[TASK-0621-The-Release-Rung-Points-At-The-Walk]]"
release: ""
acceptance_exception: ""
acceptance: "[[TST-0088-The-Walk-Page-Hands-Over-The-Owed-Checks]]"
design: ""
depends:
  - "[[ADR-0037-A-Verdict-Is-An-Event]]"
  - "[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]"
related:
  - "[[FEAT-0102-Publication-Becomes-A-View]]"
  - "[[FEAT-0114-The-Suite-Is-A-View]]"
  - "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]"
  - "[[ADR-0036-The-Sweep-Is-Withdrawn]]"
  - "[[ADR-0039-Three-Sections-Derived-Not-Filed]]"
  - "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]"
  - "[[TASK-0449-Order-The-Walk-By-Its-Setup-Cost]]"
  - "[[TASK-0465-One-Walk-Layer]]"
  - "[[TASK-0556-Incomplete-First]]"
  - "[[ISS-0280-The-Checks-Page-Does-Not-Survive-Leaving-The-Project]]"
  - "[[DES-0012-Tests-In-Two-Flows]]"
---

# The walk page

## Goal

A person preparing a release opens `~walk/<platform>` and reads down. The first section names the screens the release changed. The sections after it are sittings, each with the state it needs and what must be on the bench, and inside each the owed checks with their setup, steps and expected result on the page. A tick opens the mark dialog the walker already knows, and the verdict goes to the ledger. Nothing on the page is stored anywhere but the ledger and the notes.

## Why a third surface

The cockpit has two surfaces that touch acceptance checks, and [[TASK-0465-One-Walk-Layer]] measured that they do not converge. `~checks` is a filtered list with a persistent verdict per row. The retired runner was a stepper: it advanced one step at a time and recorded its results in one batch at the end. Three axes of difference against one of similarity, and the task concluded there was no single walk layer to build.

The walk page is neither. It is a list that carries the procedure. That is the thing `view_payload` describes itself as, *"the suite as a list somebody walks"*, and does not do: its rows are ordered section, then area, then id, with owed rows floated to the top of their area ([[TASK-0556-Incomplete-First]]), and nothing in the payload models a prerequisite, a setup state, an order between checks, a session, or a screen to look at. `ledger.owed()` calls itself *"the run list"* and is the right predicate; nothing turns it into a run.

The release page cannot be that surface either. [[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]] keeps marks off it, and its second objection is the design rule this feature pays in full: *"the release page shows the check's name and area, not its steps, so the control is offered at exactly the distance from the procedure where a person cannot be walking it."* [[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]] decision 4 says the same thing as a requirement: a surface that records a verdict must render the procedure. The walk page renders the procedure on every row, and it is the page where a `pass`, `partial` or `fail` is recorded during a walk. The release page keeps its three settle marks and nothing else.

The consumer corpus shows the cost of not having it. `your-trainer` hand-maintains a 719-line run plan, marked temporary, self-described as *"self-contained, every step has its action and expected result inline so you don't flip back"*, with a pre-flight section listing what must be on the bench and twelve phases ordered as a state machine over tier upgrades and device wipes. That is a walk sheet. Its 315 row addresses point into a document deleted in the notes migration, five `TST-*` ids appear in the whole file, and two earlier versions are retired. It has been written three times and could never be generated, because nothing in the system held the order.

## What this builds

**A payload** ([[TASK-0618-The-Walk-Payload]]). `acceptance.walk_payload(docs_root, index, platform=, release=)` returns the survey, the sittings and the unplaced rows. Its rows are exactly `ledger.owed(platform, checks)` restricted to `MANUAL_SECTIONS`. The ordering and survey rules are the template's, implemented once in `tools/scripts/walk-sheet.py` upstream (project-os-dev FEAT-0029), and the cockpit bundles that module the way it bundles the validator.

**A page** ([[TASK-0619-The-Walk-Page]]). `~walk/<platform>` in the publication view. Survey, then sittings, then rows. A row shows the check's Setup, Steps and Expect sections inline, or "Setup: not stated" linking to the note. The mark button is `askForMark` with all seven marks. The page does not reorder when a row is ticked, and it remembers the walker's place per workspace.

**The survey** ([[TASK-0620-The-Survey]]). For every owed check whose latest ledger event is an invalidation, the surface it belongs to and the change or task that invalidated it, grouped by surface. Where the invalidating note carries a `## Acceptance checks reopened` section, that section is quoted. Where WALK.md declares a gallery command, it is shown at the top of the survey.

**The links** ([[TASK-0621-The-Release-Rung-Points-At-The-Walk]]). The release rung and the release page say "N owed · walk them" and open the walk. The checks page gains the same link while a release is `draft`.

## What this must not become

**A second store.** A file naming the checks for this release is the design [[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]] and [[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]] option 3 rejected, and `PARITY_MATRIX.md`'s rot in `your-trainer` is the named failure: a maintained matrix rots, a computed query cannot. The sheet is computed from the ledger and the notes every time it is opened.

**A reordering list.** [[TASK-0556-Incomplete-First]] recorded Edwin's rule for the checks page: *"a list that reorders itself as you tick things is one you lose your place in."* The walk page holds its order for the whole walk. A ticked row changes its mark and stays where it is.

**A schedule.** [[TASK-0449-Order-The-Walk-By-Its-Setup-Cost]] was cancelled, and its guard rails outlive it: *"No time estimates. Order, not schedule."* and no new tag vocabulary. The payload carries no minutes and the page prints none. Counts of rows are the only numbers.

**An inference.** TASK-0449 died because it read burden from bracket tags that existed in one hand-written document, and a scanner over the corpus got six false positives out of six. This feature infers nothing. Order comes from WALK.md, authored once per consumer repo by the person who knows the product. A repo without WALK.md gets one sitting per area in id order, labelled as unordered, and the page says so.

**A new obligation.** [[ADR-0036-The-Sweep-Is-Withdrawn]] removed the close-out sweep because an obligation whose common case is "nothing to do, say so" is a cost paid on every task for a benefit paid on few. The survey reads the invalidation events the ledger already records. It adds no question to close-out.

## The survey, in more detail

The survey answers Edwin's second sentence: the tests never say to look at the changed screens. The information exists. Every invalidation in the ledger names the check and the change (`{check, invalidated_by, date}`, [[ADR-0037-A-Verdict-Is-An-Event]]). Every check names its surface in `area:`, and [[DES-0012-Tests-In-Two-Flows]] made surface the axis the suite is organised on. Joining the two gives, for the open release, the set of surfaces whose checks were reopened and the tasks that reopened them. That is the list of screens to open before any scripted check.

Session-based testing calls this the survey session and puts it first: a look at the product and its general risks before analysis and deep coverage. ADR-0036's own consequences section asked for it: *"when invalidation matters again, the replacement should be keyed on the surface a change touched, not on the feature."*

The survey renders, per surface: the surface name, the owed checks under it, the invalidating change and task ids with their titles, the quoted reopened section where one exists, and a link to the surface note (`SUR-*`) where the repo has one. Where WALK.md's frontmatter declares `gallery:` with a command, the survey opens with that command and the instruction to regenerate and compare before walking.

## Acceptance

- The walk payload's rows for a platform are exactly `ledger.owed(platform, manual checks)`: a test computes both over `your-trainer`'s live corpus and over a constructed fixture and asserts equality.
- Every sitting in the payload appears in WALK.md, in WALK.md's order, and no sitting with zero rows is rendered.
- A check named by two sittings appears in the first only, and a check named by none appears under "Unplaced" at the end.
- Inside a sitting, a check whose `after:` names another check in the same sitting is rendered after it; a cycle is reported as a payload error naming both checks, never silently broken.
- The survey lists a surface if and only if at least one owed check under it has an invalidation as its latest ledger event, and for that surface names every `invalidated_by` id from those events.
- A row whose note has a `## Setup` heading renders its text; a row whose note has none renders "Setup: not stated" with a link to the note. Steps and Expect likewise.
- Ticking a row opens `askForMark` with all seven marks, and the resulting event is readable by `ledger.events_by_check` with `method: manual`.
- After a tick the row keeps its position and the page keeps its scroll; leaving the workspace and returning restores the walker's place, the mechanism [[ISS-0280-The-Checks-Page-Does-Not-Survive-Leaving-The-Project]] built for `~checks`.
- The release page's gate row and the checks page's header carry a link to `~walk/<platform>` while a release is `draft`, and neither gains a mark control.
- The payload and the page contain no time estimate. A test greps the walk payload for `minute`, `duration` and `estimate` keys and finds none.

## Risk scan

**No new RISK-* is owed.** Bundling the template's walk module is a second instance of an existing pattern: `validate_docs_bundled.py` is a verbatim copy of the upstream validator, kept in step by `tools/scripts/sync-project-os.sh` and verified by `tools/scripts/test-decision-rule.py`. The same sync and the same verification cover the walk module. The hazard, a bundled copy drifting from upstream, is the one PHASE-041 built the fleet drift check for, and it applies here without a new note.

**No DES-* is warranted.** The repo's design gate is optional (`design:` on the feature, `DESIGN-GATE` warns and never blocks). The page's shape is fixed by decisions already taken: rows are `~checks` rows with the procedure inlined, the mark dialog is `askForMark` unchanged, and the sittings are headings. There is no visual choice a design would settle that [[DES-0012-Tests-In-Two-Flows]] and [[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]] have not already made.

## Upstream landed, 2026-09-13 — and one thing to settle here

The template half shipped: `tools/scripts/walk-sheet.py`, `tools/scripts/test-walk-sheet.sh`, `docs/__templates__/walk.md`, and the eight rules stated once in `tools/instructions/TESTING.md`, "The walk" (project-os-dev FEAT-0029, ADR-0029). This repo was synced the same day and its diverged `TESTING.md` and `test.md` were hand-merged rather than overwritten. The bundling decision this note already records — bundle, as with the validator — was taken as the answer to ADR-0029's acceptance box 4.

**One question for TASK-0618, and it is the only disagreement found.** The upstream generator treats every `[[test]]` at `level: acceptance` anywhere under `docs/` as a check, which is what `LIFECYCLE.md` "Test storage" allows; `acceptance.load_notes` globs `docs/tests/acceptance/TST-*.md` alone. Measured on your-trainer the same day: 649 notes against 431, with all 431 the cockpit loads resolving identically in both and section derivation agreeing on every one. So nothing is wrong today — and a check filed beside its feature would appear on a generated sheet and never on this page, which is the badge-versus-sheet disagreement rule 7 exists to prevent. Filed upstream as project-os-dev ISS-0063; whichever scoping wins, the payload should read it rather than choose it.

## Links

- Requirements: none. The requirement lives upstream as project-os-dev REQ-0028; this repo implements its cockpit half.
- Tasks: [[TASK-0618-The-Walk-Payload]], [[TASK-0619-The-Walk-Page]], [[TASK-0620-The-Survey]], [[TASK-0621-The-Release-Rung-Points-At-The-Walk]]
- Upstream: project-os-dev ADR-0029 (the walk is derived; its order is authored once), project-os-dev FEAT-0029 (the walk sheet in the template), project-os-dev ADR-0027 (the Setup, Steps, Expect, Not-this-check headings a row renders).
- Consumer: your-trainer FEAT-0119 authors `docs/tests/acceptance/WALK.md` from its run plan and is the first corpus this page is measured on.
- Repo paths: `src/project_os_cockpit/acceptance.py`, `src/project_os_cockpit/ledger.py`, `src/project_os_cockpit/server.py`, `desktop/src/renderer/renderer.ts`.

## Built 2026-09-13

All four tasks are `done` and the change note is [[CHG-20260913-The-Walk-Page]]. The capability register carries `shell.pages.walk`, `shell.pages.walk.survey`, `api.read.walk` and `cli.walk-sheet`, and records the link each of the three existing surfaces gained.

**The scoping question this note left open is answered, and not by choosing.** The payload reads the cockpit's own suite — the same set `~checks` and the gate read — and reports in `errors` any owed row the bundled module then drops. Running the generator beside the page on this repo found a real difference on the first try: the sheet lists a check at `status: retired`, which the page does not ([[ISS-0303-The-Walk-Sheet-Lists-Retired-Checks]]). A second upstream defect came out of writing this repo's walk order ([[ISS-0304-The-Walk-Order-Reader-Splits-Inside-A-Quoted-String]]). Both are upstream's to fix and neither is patched here; the bundled copy stays byte-identical, verified by `tests/test_walk_bundle.py`.

**This repo now has a walk order of its own**, `docs/tests/acceptance/WALK.md`: five sittings that climb from the server in a browser through the shell and one workspace to the rows that write. It was written to have an authored order to render against, and it is the artefact the fallback exists to replace.

**Walked, and the walk found two defects.** [[TST-0088-The-Walk-Page-Hands-Over-The-Owed-Checks]] carries the record: a check that states its Setup was told "Setup: not stated", and a row a walker had just ticked kept the glyph that means nobody has walked it. Both fixed, both with a test that fails without the fix. Its verdict is `partial` because step 13 walks the register's own detection commands, which are written in the same commit.
