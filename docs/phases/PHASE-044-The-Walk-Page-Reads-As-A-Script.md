---
type: "[[phase]]"
id: PHASE-044
aliases: ["PHASE-044"]
title: "The walk page reads as a script — changed screens as cards with before and after, each sitting as its procedure, and a tick per step"
status: done
order: 44
owner: user:edwin
created: 2026-09-14
updated: 2026-09-14
goal: "The person walking a release reads the walk page as a script: the screens the release changed as cards with before and after pictures, then each sitting as one procedure, and a tick on a step that records the verdict for every check that step satisfies, with the ledger unchanged."
features:
  - "[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]"
requirements: []
tasks:
  - "[[TASK-0622-The-Survey-As-Screen-Cards]]"
  - "[[TASK-0623-Each-Sitting-As-Its-Procedure]]"
  - "[[TASK-0624-A-Tick-Per-Step]]"
  - "[[TASK-0625-The-Checks-Page-Groups-By-Screen]]"
  - "[[TASK-0626-The-Page-And-The-Sheet-Agree-On-Your-Trainer]]"
issues: []
#: ISS-0306 was found inside this phase and re-homed to PHASE-999 when it
#: closed: writing this repo's surface notes is a job of its own.
related:
  - "[[PHASE-043-The-Walk-Page]]"
  - "[[FEAT-0149-The-Walk-Page]]"
  - "[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]"
  - "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]"
  - "[[ADR-0036-The-Sweep-Is-Withdrawn]]"
  - "[[ADR-0037-A-Verdict-Is-An-Event]]"
  - "[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]"
tags: [acceptance, publication, walk]
---

# The walk page reads as a script

## Goal

The walk page from [[PHASE-043-The-Walk-Page]] lists owed checks inside sittings, each check with its own Setup, Steps and Expect. On your-trainer's v2.2.0 walk that repeats one setup four times in a sitting, and its survey lists test categories such as "Hardware" rather than screens. This phase makes the page read as a script. The survey becomes one card per changed screen with before and after pictures. Each sitting becomes one written procedure. A tick goes on a step, and records a verdict for every check the step satisfies once all its steps are ticked.

Edwin approved the goal wording on 2026-09-14: *"A tick in the cockpit records the verdict for every check that step satisfies."* The template half is project-os-dev PHASE-0005 (FEAT-0030, FEAT-0031, and decisions ADR-0044 and ADR-0045, accepted by Edwin on 2026-09-14). The consumer half is your-trainer PHASE-024 (FEAT-0120, FEAT-0121).

**Why a phase and not more tasks under PHASE-043.** Its goal is stated without its parts, and its exit criteria are about equivalence with the ledger and agreement with the sheet, not about tasks being done (CLAUDE.md, "When to open a phase"). PHASE-043 is closed and reviewed; reopening it would blur what that review approved. If this turns out to be one session's work, fold it into PHASE-043 and supersede this note.

## Scope

- Survey as screen cards with before and after images ([[TASK-0622-The-Survey-As-Screen-Cards]]).
- Each sitting rendered as its procedure, from the bundled `walk-sheet.py` payload ([[TASK-0623-Each-Sitting-As-Its-Procedure]]).
- A tick per step, with a check's verdict written once every step citing it has one ([[TASK-0624-A-Tick-Per-Step]]).
- `~checks` groups by screen, parents first, following the template's surface rules ([[TASK-0625-The-Checks-Page-Groups-By-Screen]]).
- The page and `walk-sheet.py` agree on your-trainer for both platforms ([[TASK-0626-The-Page-And-The-Sheet-Agree-On-Your-Trainer]]).

## Out of Scope

- Any ledger format change. One event per check stays ([[ADR-0037-A-Verdict-Is-An-Event]]).
- Writing procedures or change notes for any repo.
- Merging steps without a written procedure.
- A mark control on the release page ([[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]], [[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]).

## Exit Criteria

- [x] Ticking every step of a sitting writes the same ledger events, check for check and mark for mark, as ticking each of its checks one by one on today's page. A test proves it on a fixture. — `desktop/tests/walk-page.test.mjs`, *"walking a sitting step by step writes the same events as ticking its checks one by one"*: four steps citing three checks, both paths run against one stubbed POST, the request bodies compared.
- [x] For your-trainer on both platforms, the page's survey, sittings, steps and owed set equal what `walk-sheet.py` prints. — asserted and passing on `android` and `ios` by `tests/test_walk_agreement.py`. **The procedure half of that comparison has nothing to compare yet**: `your-trainer` carries no `docs/tests/acceptance/walk/` directory, so both sides agree that no sitting has a procedure; the procedure half is exercised on a two-platform fixture in the same file. Edwin settled the scope on 2026-09-14 — *"Finish the project-os-cockpit phase only, the your-trainer functionality will be handled in the your-trainer repo"* — and that repo's `TASK-0907` already names this comparison as its own step.
- [x] The survey shows no test id, and every card with a before capture shows the after capture beside it. — two node tests, and observed in a browser on the fixture: both pictures of a pair rendered at 358 px.
- [x] `~checks` puts a dialog under the screen it opens from, the same way the template's rules and the walk sheet do. — `tests/test_checks_by_screen.py`, including one test that the parent this page resolves is the one `walk.top_screen` resolves, for all three spellings of `parent:`.
- [x] The capability register names every new or changed row (CLAUDE.md, "Every change note that adds, changes or retires capability"). — `shell.pages.walk.steps` is new; `shell.pages.walk`, `shell.pages.walk.survey` and `shell.pages.checks` each gained a dated line.

## Closed, 2026-09-14

All five tasks are `done` and [[FEAT-0150-The-Walk-Page-Reads-As-A-Script]] is `done`.

**It was walked in a browser**, not only against a stub DOM: a fixture repo with a release tag, two change notes, three capture files, a walk order and a three-step procedure, served by a real sidecar behind a one-origin proxy and driven through `desktop/harness/live-harness.html`. That walk wrote real events into a real ledger file, and it found two defects the node suite structurally could not:

1. **Step lines printed their Markdown.** `**Ride cockpit.** Pedal for five seconds` appeared with the asterisks, on the page and again in the mark dialog's title. The DOM stub has no reader, so nothing was looking at the words.
2. **The walk route resolved the platform and not the release.** Every payload came back with `release: ""`, and a step tick is keyed by release, platform, sitting and step — so a tick left from one walk would have shown as already ticked on the next.

Both are fixed with tests. The walk is recorded on [[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]] as `partial`, because its step 8 — the same checks ticked one by one on the fallback rows, two ledgers compared by hand — was not walked; it is asserted instead by a node test that runs both paths against one stubbed POST.

**Where the consumer half went.** This phase's last task was open against `your-trainer`, whose PHASE-024 had not started and whose first step is a screen-mapping table awaiting Edwin's approval. He settled it: *"Finish the project-os-cockpit phase only, the your-trainer functionality will be handled in the your-trainer repo."* So the comparison this repo owns is written and passing, and your-trainer `TASK-0907` runs it against real procedures when it has them. Nothing here has to change for that.

**Filed, not fixed:** [[ISS-0306-This-Repos-Own-Screens-Have-No-Surface-Notes]] — one surface note for roughly fourteen screens, so this repo's own change notes cannot write an `## Impact` line and its own survey will always be empty.
