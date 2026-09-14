---
type: "[[feature]]"
id: FEAT-0150
aliases: ["FEAT-0150"]
title: "The walk page reads as a script — the survey as screen cards with before and after, each sitting as its procedure, a tick per step that settles every check it cites, and ~checks grouped by screen"
status: doing
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
