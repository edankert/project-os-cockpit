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
reviewed_by: model:claude-opus-5
review_date: 2026-09-13
review_verdict: changes-requested
review_response: "All ten findings acted on. Both blocking ones fixed: a tick on the walk now carries the walk's own platform rather than the nav picker's (it could write to the wrong ledger, or to none), and the two upstream issues are re-homed out of the parking lot now that they are fixed. Seven non-blocking findings fixed with tests; one filed as ISS-0305 because it is a decision about CI."
review_response_date: 2026-09-13
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

**The scoping question this note left open is answered, and not by choosing.** The payload reads the cockpit's own suite — the same set `~checks` and the gate read — and reports in `errors` any owed row the bundled module then drops. Running the generator beside the page on this repo found a real difference on the first try: the sheet lists a check at `status: retired`, which the page does not ([[ISS-0303-The-Walk-Sheet-Lists-Retired-Checks]]). A second upstream defect came out of writing this repo's walk order ([[ISS-0304-The-Walk-Order-Reader-Splits-Inside-A-Quoted-String]]). Both were fixed upstream the same day and re-synced here rather than patched locally; the bundled copy stays byte-identical to `tools/scripts/walk-sheet.py`, verified by `tests/test_walk_bundle.py`. The sheet and the page now agree at 3 owed rows on this repo.

**This repo now has a walk order of its own**, `docs/tests/acceptance/WALK.md`: five sittings that climb from the server in a browser through the shell and one workspace to the rows that write. It was written to have an authored order to render against, and it is the artefact the fallback exists to replace.

**Walked, and the walk found two defects.** [[TST-0088-The-Walk-Page-Hands-Over-The-Owed-Checks]] carries the record: a check that states its Setup was told "Setup: not stated", and a row a walker had just ticked kept the glyph that means nobody has walked it. Both fixed, both with a test that fails without the fix. Its verdict is `partial` because step 13 walks the register's own detection commands, which are written in the same commit.

## Independent review 2026-09-13 (model:claude-opus-5) — changes-requested

Fresh context, separate session, commit `199c0fd` reviewed from the notes and the diff alone. Same model family as the author, which is recorded in `reviewed_by:` as provenance; independence here is the context, not the weights ([[project-os-dev#ADR-0013]], `tools/instructions/QUALITY.md` "Independent review (clean-context)").

### Blocking

**1. A tick on the walk is not recorded against the walk's platform.** `walkOneCheck` sends `platform: verdictPlatform()` (`desktop/src/renderer/renderer.ts:9480`). `verdictPlatform()` (same file, 2346-2350) reads the nav picker's stored value, falls back to the single ledger platform, and otherwise returns `''`. It never sees the walk's platform, and `renderWalkPage` sets neither input — `ledgerPlatforms` is assigned in exactly one place, inside `renderChecksPage` (9676), and `loadStoredPlatform()` returns `'all'` until somebody clicks the picker, which `renderPlatformBar` hides on a one-platform repo. Two failures follow. On a one-platform repo, a walker who reaches the walk from the publication ladder without opening `~checks` first sends no platform, and `note_writes` refuses the mark outright — *"this verdict has no platform to belong to"* — on the page the whole feature exists for. On a two-platform repo the picker wins: `../your-trainer` keeps `WORKING-android.json` and `WORKING-ios.json`, so opening `~walk/android` with the picker on `ios` writes the verdict to the iOS ledger. The repaint then refetches `~walk?platform=android`, finds the row still owed, and redraws it unchanged, so there is no error and no visible effect. `TST-0088` step 9 verified the write on this repo, which keeps one ledger and so cannot show either case.

**2. The test suite is red at this commit.** `tests/test_coverage_registers.py::test_no_terminal_note_sits_in_the_parking_lot` fails on `['ISS-0303 (issue, fixed)', 'ISS-0304 (issue, fixed)']`. Both notes are created by this commit at `status: fixed` with `phase: "[[PHASE-999-Future]]"`. [[ISS-0303-The-Walk-Sheet-Lists-Retired-Checks]] argues for the parking under a heading of its own, and that argument was written while the issue was open; once the same commit marked it `fixed`, the guard fired.

### Non-blocking findings

**3. Two of the three links appear when there is no walk.** `cockpit._release_content_rows` guards on `_ledger_platforms(index)`; the release page's gate button (`d.preparing && unchecked && d.platform`) and the checks page's header (`v.blocking && v.platform`) do not. On a repo with a draft release naming a platform and no ledger — the state of every repo before its first mark — both render and both open the route's 400 refusal. [[CHG-20260913-The-Walk-Page]] says *"Each appears only when there is a walk to do"*; for two of the three that is not what the code does.

**4. The dropped-rows reconciliation is unguarded.** Replacing `dropped = sorted(owed_ids - kept)` in `acceptance.walk_payload` with `dropped = []` leaves all 42 walk tests green. The mechanism whose stated purpose is to catch the two owed predicates disagreeing has no test that it fires.

**5. The headline claim is guarded only by a skippable test.** Removing `section_of(i) in MANUAL_SECTIONS` from `walk_payload` fails only `test_the_live_corpus_row_set_equals_ledger_owed`, which is skipped unless `../your-trainer` is checked out. `test_the_rows_are_exactly_what_the_ledger_says_is_owed` survives the mutation because it asserts the row ids and not `payload["errors"]`, which the mutation makes non-empty.

**6. The walk page's behavioural tests run nowhere but a developer's machine.** `desktop/tests/walk-page.test.mjs` reads `desktop/dist/renderer/renderer.js`, which `desktop/.gitignore` excludes, and no workflow in `.github/workflows/` runs `node --test`. A stale build silently tests the previous renderer.

**7. A checked-off row loses its own history.** `repaintWalkRow` sets `checksHistory = fresh.history`, and the payload restricts `history` to the rows it kept — so a check just marked `pass` is no longer in it. Reopening the dialog on the row still on screen shows no past verdicts, including the one just written, and the row's *"N comments"* meta disappears.

**8. The change note describes two defects that this commit fixes.** [[CHG-20260913-The-Walk-Page]] says the sheet *"lists a check at `status: retired`"* and that *"neither is patched here"*. Both were fixed upstream and re-synced in this same commit (`.project-os-sync` moves to `bb2802d`), and `python3 tools/scripts/walk-sheet.py --release REL-0002 --platform macos` now reports 3 owed rows — the same 3 `walk_payload` returns. The issue notes record the upstream fix correctly; the change note reads as though both are still live.

**9. The unplaced section gives fallback readers an instruction they cannot follow.** With no `WALK.md` and a check carrying no `area:`, `unordered_sittings` makes no sitting for it, so it lands under *"add a sitting that claims them, or add the surface to one that exists"* — about a walk order that does not exist.

**10. The payload's time-estimate guard matches whole key names only.** `str(key).lower() in banned`, so `setup_minutes` would pass. The renderer's guard uses a word-boundary regex and is the stronger of the two.

### What was attacked and held

Disabling the chosen-verdict redraw in `repaintWalkRow`, and disabling `walkBlock`'s `note` branch, each fail a node test — the two defects the walk found are really guarded. Loosening the survey's invalidation predicate fails two tests. The route's two refusals are end-to-end tests against a live server. The `_VD` seeding is safe: it assigns the same module object idempotently, and every bundled entry point that needs the validator is reached only after `_walk_module()` has seeded it. Bundle byte-identity holds, the page and the CLI agree at 3 owed rows on this repo, and `validate-docs.sh` is green. Both edited guards are corrections rather than weakenings: the `buildCheckRow` parameter pin is updated *and* strengthened with an assertion on `onMark`'s default, and `_body_of`'s new paren-walk fixes a helper that a brace inside a parameter type would otherwise mis-bound.

**On the randomized-order failure of `test_a_fresh_process_is_not_stale`:** unrelated to this change. `sidecar_stale` is *newest `.py` mtime under the package > this process's start*; no test writes into `src/project_os_cockpit/` (every reference there is a read), so ordering cannot produce it. An external write under `src/` while the run is in flight can, which is the cross-process hazard `test_source_newer_than_the_process_reads_as_stale` documents in its own docstring.

## What was done about the review, 2026-09-13

The verdict stands as the reviewer wrote it ([[project-os-dev#ADR-0011]]: a verdict is the reviewer's, and clearing it yourself turns an independent gate into a formality). This records what was done.

**Blocking 1 — a tick went to the wrong ledger, or to none.** `walkOneCheck` took the platform from the nav picker. A walk is one platform by construction, and reading the picker was wrong in both directions: on a one-ledger repo reached from the publication ladder without opening `~checks` first, `ledgerPlatforms` was empty and the platform resolved to `''`, which the write path refuses outright — the mark failed on the page the whole feature exists for. On a two-ledger repo with the picker on `ios`, a tick on `~walk/android` wrote the verdict into the iOS ledger and the row redrew as still owed, with no error. `walkOneCheck` now takes the platform as an argument; the walk passes its payload's, `~checks` passes `verdictPlatform()` and is unchanged. Two node tests pin it, and they fail if the argument goes back to the picker. `renderWalkPage` also fills `ledgerPlatforms` from its payload, so the rest of the app stops depending on the reader having visited the list.

**Blocking 2 — the suite was red.** `ISS-0303` and `ISS-0304` were written at `triage` and parked under [[PHASE-999-Future]] so they would not hold this phase open; upstream fixed both the same day and another session marked them `fixed`, leaving two terminal notes in the parking lot — exactly what `test_no_terminal_note_sits_in_the_parking_lot` exists to catch. Both are re-homed to this phase, where they were found and where they were resolved.

**3 — two of the three links appeared with no walk behind them.** The release page's button and the checks header did not check that the repo keeps a ledger for the platform, so both rendered on any repo with a draft release and no ledger — every repo before its first recorded mark — and opened the route's 400. Both now consult the ledger, guarded by a test.

**4, 5, 10 — three assertions that would have survived the behaviour being removed.** The dropped-rows reconciliation had no test and now has one that forces the disagreement by monkeypatching the bundled module's `resolve`; the fixture for *the rows are the owed set* now also asserts `errors == []`, which is what a missing `MANUAL_SECTIONS` filter shows up as; and the banned-key guard matches a key that *contains* `minute`, `duration` or `estimate` rather than one spelled exactly that.

**7 — a ticked row lost its own history.** `repaintWalkRow` assigned `checksHistory` from a payload restricted to the rows still owed, so the check just walked lost everything anybody had said about it. Merged now, not replaced.

**8 — the change note described the two upstream defects as unfixed.** True when it was written and false within hours. Corrected, with the correction dated and the original wording named.

**9 — the "Unplaced" sentence pointed at a file that does not exist.** With no walk order, a row reaches Unplaced only when its check names no `area:`, and telling that reader to add a sitting sends them to a `WALK.md` that is not there. The page says something different in each case.

**6 — filed rather than fixed** ([[ISS-0305-The-Desktop-Node-Suite-Runs-Nowhere-But-A-Developers-Machine]]). The node suite skips on CI because `desktop/dist/` is gitignored and no workflow builds it, so the twenty-three tests holding this page's behaviour run only where somebody has built the desktop. It is not this feature's defect and it predates it by a year; it is filed because this feature put its strongest assertions there. Whether CI grows a node install is Edwin's call.

**The randomized-order flake is not ours.** The reviewer reached the same conclusion independently: `sidecar_stale` compares the newest `.py` mtime under the package against the process start, no test writes there, and an external write under `src/` mid-run is the cross-process hazard the sibling test's own docstring records.
