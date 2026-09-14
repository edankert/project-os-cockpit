---
type: "[[phase]]"
id: PHASE-044
aliases: ["PHASE-044"]
title: "The walk page reads as a script — changed screens as cards with before and after, each sitting as its procedure, and a tick per step"
status: planned
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

Edwin approved the goal wording on 2026-09-14: *"A tick in the cockpit records the verdict for every check that step satisfies."* The template half is project-os-dev PHASE-0005 (FEAT-0030, FEAT-0031, proposed decisions ADR-0044 and ADR-0045). The consumer half is your-trainer PHASE-024 (FEAT-0120, FEAT-0121).

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

- [ ] Ticking every step of a sitting writes the same ledger events, check for check and mark for mark, as ticking each of its checks one by one on today's page. A test proves it on a fixture.
- [ ] For your-trainer on both platforms, the page's survey, sittings, steps and owed set equal what `walk-sheet.py` prints.
- [ ] The survey shows no test id, and every card with a before capture shows the after capture beside it.
- [ ] `~checks` puts a dialog under the screen it opens from, the same way the template's rules and the walk sheet do.
- [ ] The capability register names every new or changed row (CLAUDE.md, "Every change note that adds, changes or retires capability").

## Notes

- **Builds against a fixture first.** TASK-0622 to TASK-0625 need no real content: a fixture repo with a release tag, two change notes, a capture map, a procedure and a ledger is enough. TASK-0626 waits for your-trainer's TASK-0906.
- **Hard upstream dependency.** The procedure shape and the survey payload come from the template's `walk-sheet.py` (project-os-dev TASK-0118, TASK-0121), bundled byte for byte. This page implements no survey or procedure rule of its own.
- **Risk scan.** No new dependency or environment variable. Images are served from the consumer repo through the existing framed viewer route ([[PHASE-042-A-Note-Shows-What-It-Is-About]]). Step ticks that are not yet a verdict need somewhere to live between clicks; where is TASK-0624's first question, and it must not become a second store. No `RISK-*` until that is decided.
