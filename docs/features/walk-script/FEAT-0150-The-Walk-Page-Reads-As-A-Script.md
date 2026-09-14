---
type: "[[feature]]"
id: FEAT-0150
aliases: ["FEAT-0150"]
title: "The walk page reads as a script — the survey as screen cards with before and after, each sitting as its procedure, a tick per step that settles every check it cites, and ~checks grouped by screen"
status: done
phase: "[[PHASE-044-The-Walk-Page-Reads-As-A-Script]]"
owner: user:edwin
created: 2026-09-14
updated: 2026-09-14
source: ["Edwin, 2026-09-14, approved goal: 'Before v2.2.0 ships, Edwin walks the release from a sheet that works like a script … A tick in the cockpit records the verdict for every check that step satisfies. \"Done\" means Edwin walks the whole v2.2.0 release this way and never opens a check note.'"]
goal: "The walk page shows the screens a release changed as cards with before and after pictures, presents each sitting as its written procedure, and lets the walker tick steps, recording each check's verdict in the ledger once every step that cites it has been ticked."
requirements: []
tasks:
  - "[[TASK-0622-The-Survey-As-Screen-Cards]]"
  - "[[TASK-0623-Each-Sitting-As-Its-Procedure]]"
  - "[[TASK-0624-A-Tick-Per-Step]]"
  - "[[TASK-0625-The-Checks-Page-Groups-By-Screen]]"
  - "[[TASK-0626-The-Page-And-The-Sheet-Agree-On-Your-Trainer]]"
release: ""
acceptance_exception: ""
acceptance: "[[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]]"
reviewed_by: model:claude-opus-5
review_date: 2026-09-14
review_verdict: changes-requested
review_response: "All three gate-holding findings fixed with tests, plus four of the nine others. 1: the walk route filtered its release by platform, so ~walk/ios no longer names an Android draft. 2: a step tick is keyed by the owed parts the step cites instead of its position, so an edited procedure cannot hand a mark to a step nobody walked. 3: the ~checks fixture ids now run against the answer, and the sort-key mutation that left 253 tests green fails 5. Also fixed: 5 (a refused write is reported), 6 (the agreement fixture gained a passed check, and the known= mutation now fails 3 tests), 7 (the payload carries the module's own quote, so the page no longer derives one), 9 (a flow no longer counts as a screen). Filed, not fixed: 4 as ISS-0308, 8 as ISS-0309 (upstream, the bundle must not be patched locally), 10 added to ISS-0306, 11 as ISS-0307 and TST-0089's ledger entry corrected to by: model:claude-opus-5. 12 needed nothing: both notes already disclose it."
review_response_date: 2026-09-14
design: ""
depends:
  - "[[FEAT-0149-The-Walk-Page]]"
  - "[[ADR-0037-A-Verdict-Is-An-Event]]"
related:
  - "[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]"
  - "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]"
  - "[[ADR-0036-The-Sweep-Is-Withdrawn]]"
  - "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]"
  - "[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]"
  - "[[TASK-0556-Incomplete-First]]"
  - "[[ISS-0250-A-Surface-Rename-Silently-Orphans-Its-Checks]]"
  - "[[ISS-0280-The-Checks-Page-Does-Not-Survive-Leaving-The-Project]]"
---

# The walk page reads as a script

## Goal

Edwin opens `~walk/android` for your-trainer and reads down. First, one card per screen the release changed: the screen's name, what it now shows in a sentence a rider would understand, and a picture from the last release beside a picture from the release candidate. Then each sitting as one procedure: the setup once, numbered steps each naming a screen, and expectation lines tagged with the check step they satisfy. He ticks steps. When every step that cites a check has a tick, the check's verdict goes to the ledger as one event, the same event today's page writes.

## What exists, and what changes

[[FEAT-0149-The-Walk-Page]] built `~walk/<platform>`: a survey of surfaces whose owed checks were invalidated, sittings in WALK.md order, and one row per owed check with Setup, Steps and Expect and a mark button (`askForMark`). The payload comes from the bundled `walk_sheet_bundled.py`.

Upstream now changes two of the rules that page renders (project-os-dev ADR-0045, accepted by Edwin on 2026-09-14):

- The survey is built from change notes since the last release tag, grouped by the screens their Impact section names, with before and after captures. It prints no test id.
- A sitting may carry a procedure, and the sheet prints only the steps that cite an owed part. A sitting without one prints per-check rows as today.

Upstream also says a surface is a screen by default, with dialogs as children (project-os-dev ADR-0044, accepted 2026-09-14). `~checks` groups by `area:` today, and should group by screen with children under parents.

## What this builds

**Screen cards** ([[TASK-0622-The-Survey-As-Screen-Cards]]). The survey payload's surfaces render as cards with the sentences and the two captures. Images come from the consumer repo through the framed viewer.

**Procedures** ([[TASK-0623-Each-Sitting-As-Its-Procedure]]). A sitting with a procedure renders its setup once and its owed steps, each expectation line with its tags. A passed tag shows as passed. A sitting whose procedure fails the upstream validator shows the message and falls back to per-check rows.

**Step ticks** ([[TASK-0624-A-Tick-Per-Step]]). The tick moves from the check to the step. A check's verdict is written when every step citing it has a tick. The ledger still stores one event per check.

**`~checks` by screen** ([[TASK-0625-The-Checks-Page-Groups-By-Screen]]). Groups follow the surface notes' `parent:`, so a dialog's checks sit under its screen.

**Agreement** ([[TASK-0626-The-Page-And-The-Sheet-Agree-On-Your-Trainer]]). On your-trainer, both platforms, the page and `walk-sheet.py` agree on survey, sittings, steps and owed set.

## What this must not become

**A second store.** Step ticks that have not yet produced a verdict are progress, not verdicts. Edwin decided on 2026-09-14 that they live in the cockpit's per-workspace browser storage, the way the walker's place already does ([[ISS-0280-The-Checks-Page-Does-Not-Survive-Leaving-The-Project]]), never in the repo or the ledger and never read by the gate ([[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]).

**A bulk pass.** [[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]] forbids `pass` from a surface that does not show the procedure. The walk page shows it, so a step tick may pass several checks. A pass from a step attests the check's own expectation, because each expectation line quotes the check's Expect text word for word and the upstream validator checks the quote (Edwin, 2026-09-14, recorded on project-os-dev ADR-0045).

**A reordering list.** Ticking a step never moves it ([[TASK-0556-Incomplete-First]]).

**A rule of its own.** Survey membership, procedure filtering and surface grouping come from the bundled module. The page renders them.

## Acceptance

- A check's verdict is the worst mark among the steps citing it (Edwin, 2026-09-14).
- On a fixture sitting, ticking every step writes ledger events equal, check for check and mark for mark, to ticking the same checks one by one on FEAT-0149's page. [[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]] walks it; a unit test asserts it.
- A check cited by two ticked steps and one unticked step has no new ledger event.
- A step marked `fail` makes every check it cites `fail` once that check's steps are all ticked, and the dialog asks for the reason `ledger.NEEDS_REASON` already requires.
- The survey cards contain no `TST-` string, and a card with a before capture shows both images.
- `~checks` renders a dialog's checks under its parent screen, and a screen with no checks still appears (FEAT-0130).
- On your-trainer, both platforms, the page's survey surfaces, sitting order, printed step ids and owed set equal `walk-sheet.py`'s.
- The payload and page contain no time estimate.

## Risk scan

No new dependency or environment variable. Captures are read from the consumer repo through the existing viewer route. State between step ticks lives in the viewer's per-workspace browser storage (decided 2026-09-14), so no `RISK-*` is owed.

## Links

- Upstream: project-os-dev PHASE-0005, FEAT-0030, FEAT-0031, ADR-0044, ADR-0045, REQ-0029.
- Consumer: your-trainer PHASE-024, FEAT-0120 (surfaces are screens), FEAT-0121 (v2.2.0 procedures and captures).
- Repo paths: `src/project_os_cockpit/acceptance.py`, `src/project_os_cockpit/ledger.py`, `src/project_os_cockpit/server.py`, `src/project_os_cockpit/cockpit.py`, `desktop/src/renderer/renderer.ts`, `src/project_os_cockpit/walk_sheet_bundled.py`.

## Done, 2026-09-14

All five tasks are `done`. The page reads as a script: screen cards with before and after, a sitting drawn as its written procedure, a tick on a step that writes one ledger event per check when every citing step has a mark, and `~checks` grouped by screen.

**Scope settled by Edwin the same day**, when this feature's last task was open against another repo: *"Finish the project-os-cockpit phase only, the your-trainer functionality will be handled in the your-trainer repo."* So [[TASK-0626-The-Page-And-The-Sheet-Agree-On-Your-Trainer]] closes on this repo's half — the comparison is written and passes on `your-trainer`'s live corpus for `android` and `ios` — and the run against that repo's real v2.2.0 procedures is your-trainer's `TASK-0907`, which already carries it by name.

**It was walked in a browser, and that is where two defects were found.** A fixture repo with a release tag, two change notes, three captures, a walk order and a three-step procedure, served by a real sidecar behind a one-origin proxy. Step lines printed their Markdown markers, on the page and in the mark dialog's title; and the walk route resolved the platform but never the release, so every payload named no release while step ticks are keyed by one. Both fixed with tests. Recorded on [[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]], which is `partial`: its step 8 is asserted by a node test instead of walked by hand.

**One thing this repo cannot show itself**: it keeps one surface note for roughly fourteen screens, so its own change notes cannot write an `## Impact` line and its own survey will always be empty. [[ISS-0306-This-Repos-Own-Screens-Have-No-Surface-Notes]].

## Independent review, 2026-09-14 — `changes-requested`

Reviewed from the notes and the diff (commits `024041c`, `e36fdaf`, plus the uncommitted note edits) in a fresh session that did not author the work. Same model family as the author, recorded in `reviewed_by:` as provenance; clean context is what the gate asks for (`tools/instructions/QUALITY.md`, "Independent review (clean-context)"; project-os-dev ADR-0013). Twelve findings, each reproduced by a command unless marked otherwise. No code was changed by the review; mutations were run and reverted.

### The three I would hold the gate on

1. **A walk names another platform's release.** `src/project_os_cockpit/server.py`, the `/api/cockpit/walk` release resolution: `open_releases(index)` is not filtered by the platform being walked, so `_release = _open[0]["id"]` takes the highest-version open draft whatever platform it belongs to. On `tests/test_walk_route.py`'s own fixture, `?platform=ios` returns `release: "REL-0001"` — the Android draft. On `your-trainer` today `open_releases` returns exactly one row, `REL-0017` / android, so `~walk/ios` is headed *"Walk — REL-0017, ios"* and keys its iOS step ticks under an Android release id. The day an iOS draft with a higher version appears, the key prefix changes under a walk in progress: those ticks stop being read, and `pruneStepMarks` never removes them because it only prunes the current prefix.
2. **A procedure edited mid-walk re-attaches old marks by position.** The key is `release|platform|sitting|step-number` and a step's number is its position, not anything about the step. Seed one mark on step 1, insert a new first step in the procedure, redraw: the new step 1 is drawn `step 1 — pass` and the mark the walker gave to a different step is now one tick away from entering a verdict. This is the same class of defect the release segment was added to fix, one level down.
3. **The `~checks` ordering rule has no test that can fail.** Replacing `_area_sort_key`'s body with `return (0,)` leaves 253 tests green across the nine test files that touch `areas`. `tests/test_checks_by_screen.py`'s corpus writes `TST-0001`..`TST-0004` in exactly the order the assertions expect, so a stable sort with a constant key satisfies every one of them. TASK-0625's first and third Definition-of-Done boxes are unguarded.

### The rest

4. **Re-ticking a step writes a duplicate ledger event.** `fail` and `question` keep a check owed, so its tag stays `owed` and its steps keep printing. Ticking any citing step again re-posts the check with the same combined mark and the same stored reason, dated now. Reproduced against the node harness: two identical `["TST-0001","fail","Step 3: it broke"]` posts from one walk.
5. **With `localStorage` refusing writes, a check cited by more than one step can never be settled, silently.** Ticking all four fixture steps posted `TST-0002` and `TST-0003` and never `TST-0001`. The comment beside `saveStepMarks` says *"storage unavailable — the walk still works, tick by tick"*; it works only for checks cited by exactly one step.
6. **`tests/test_walk_agreement.py` does not guard the regression its docstring claims.** Reverting `walk_payload`'s `known=known` to `known=checks` — the defect the file's header describes — leaves all four of its tests green. The two tests that do catch it are in `tests/test_walk_payload.py`. The live half has no procedure to compare on `your-trainer`, and the fixture has no already-passed check for a procedure to cite.
7. **The page does implement one procedure rule of its own.** The payload carries each line's raw text but not the module's `expectation.quote`, so `walkLineText` re-derives it. For `- The banner reads **DONE**  now. \`TST-0001.1\`` the module's quote is `The banner reads **DONE** now.` and the page draws `The banner reads DONE  now.` — emphasis stripped mid-line where `normalise` strips it only at the ends, and the double space kept where `normalise` collapses it. The walker judges a string the validator never compared. "This page implements no survey rule and no procedure rule of its own" is therefore not exactly true.
8. **The ADR-0041 justification is wider than the code.** *"Each expectation line quotes the check's Expect text word for word and the upstream validator checks the quote"* holds only where the check states an `## Expect`: `_audit_tag` returns no problem when `expect_lines(check)` is empty. Measured on `your-trainer`: 14 of the 39 owed rows have Expect lines, so for 25 of them the quote is unchecked and the line is the procedure author's own wording. The page still shows the procedure, so ADR-0041's literal rule holds; the sentence justifying it does not.
9. **A `flow` is counted as a screen.** `_surface_tree` counts every root whose kind is not `subsystem` or `surface-less`, and `TAXONOMY.md` lists `flow` as "a sequence across screens". On `your-trainer`'s 17 surfaces the design view's heading counts 10 screens where 6 are screens and 4 are flows, against [[FEAT-0130-Surfaces-Are-A-First-Class-Type]]'s 12-to-15 target. The test corpus has no `flow`.
10. **Every `~checks` group in this repo now carries the orphan badge.** Measured through `view_payload` on this repo's own docs: 25 areas, 25 `unresolved`. [[ISS-0306-This-Repos-Own-Screens-Have-No-Surface-Notes]] records the empty survey and the "1 screen" heading but not this, and ISS-0250's signal reads as noise when it is on every group.
11. **Who walked [[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]] is not stated** (not reproduced — a gap in the record). Its ledger entry says `by: user:edwin`, but `postCheckVerdict` hard-codes `by: 'user:edwin'` for every tick the shell makes, so the field cannot distinguish a person from an agent. `QUALITY.md` makes "a person performing it" the whole reason an acceptance test owes no separate review, so the walker's identity is load-bearing and belongs in the note.
12. **The bar moved in the commit that cleared it** (an observation, not a defect). PHASE-044's second exit criterion went from `[~]` to `[x]` with its text rewritten, and TASK-0626's title and two Definition-of-Done boxes changed, in the same edit that closed both. Both notes disclose the rewrite and quote the decision behind it, so it is legible — but a reader comparing the phase's opening criteria with its closing ones is comparing two different bars. The same edit deletes PHASE-044's "Edwin's decisions, 2026-09-14", "Start order" and "Notes" sections; the decisions survive on TASK-0624 and the risk scan on this note, so nothing is lost outright.

### What held up

The combine rule, the holding rule, the storage key's four segments, the prune's release-and-platform confinement, the `owed`-tag filter and the Markdown stripping each have a test that fails when the behaviour is removed — six mutations run, six caught. The ledger format is unchanged and both tick paths go through `postCheckVerdict`. The framed-viewer route resolves and confines to the workspace `docs/` root. The full Python suite is 2,141 passing and `validate-docs.sh` reports OK.
