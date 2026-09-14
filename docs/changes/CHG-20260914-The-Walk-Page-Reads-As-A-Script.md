---
type: "[[change]]"
id: CHG-20260914
aliases: ["CHG-20260914"]
title: "The walk page reads as a script: the survey is screen cards with before and after, a sitting is its written procedure, and a tick goes on a step"
date: 2026-09-14
status: merged
owner: user:edwin
phase: "[[PHASE-044-The-Walk-Page-Reads-As-A-Script]]"
source: ["[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]"]
implements: ["[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]"]
tasks: ["[[TASK-0622-The-Survey-As-Screen-Cards]]", "[[TASK-0623-Each-Sitting-As-Its-Procedure]]", "[[TASK-0624-A-Tick-Per-Step]]", "[[TASK-0625-The-Checks-Page-Groups-By-Screen]]", "[[TASK-0626-The-Page-And-The-Sheet-Agree-On-Your-Trainer]]"]
related: ["[[CHG-20260913-The-Walk-Page]]", "[[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]", "[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]", "[[ISS-0250-A-Surface-Rename-Silently-Orphans-Its-Checks]]"]
tags: [change, acceptance, publication, walk]
---

# The walk page reads as a script

## Summary

A walker opening `~walk/<platform>` now reads a script instead of a list of checks. The survey at the top is one card per screen the release changed, with the picture from the last release beside the picture from the candidate. A sitting that has a written procedure is drawn as that procedure — the setup stated once, then numbered steps — and the tick moves from the check to the step. When every step citing a check has been ticked, one ledger event is written for that check, exactly the event the old per-check tick wrote. `~checks` groups by screen at the same time, so a dialog's checks sit under the screen it opens from.

## Impact

- The walk page (`~walk/<platform>`): the survey is cards with two pictures and no check ids; a sitting with a procedure shows that procedure instead of one block of Setup, Steps and Expect per check; steps carry the tick.
- The checks page (`~checks`): the groups are screens, a dialog's checks are indented under the screen it opens from and labelled `in <screen>`, and an `area:` that matches no surface note is drawn last and says so.
- The design view's Surfaces group: the heading counts top-level screens and children separately, and the list puts each child under its parent.

*(No `[[SUR-####]]` link on these lines: this repo keeps one surface note, `SUR-0001`, for the tests view. Its own screens are not noted, so there is no id to name. That is a gap in this repo's record, not in the change — filed as [[ISS-0306-This-Repos-Own-Screens-Have-No-Surface-Notes]].)*

## What a walker sees

**The survey is screens, not test categories.** It was built from the ledger's invalidation events until today. An invalidation names a check and never a screen, so on `your-trainer` it listed things like "Hardware", which spans five screens and is not a place anybody opens. It now reads the `## Impact` list on every change note added since the last release tag: one screen per line, one sentence each. Each screen is a card — the screen's name, the sentences with a link to the change note behind each, and the capture from the last release beside the capture from the candidate at the same width. A screen captured now and not before is marked **new**. A dialog's card is drawn inside its parent screen's card, because that is where the walker will be standing when they open it. The cards carry no `TST-` id at all: this is a list of places to look, not a list of things to run.

**A sitting is its procedure.** `your-trainer`'s data-only sitting has five checks whose Setup sections all say the same thing; drawn as rows, the walker reads that setup five times. A sitting with a procedure under `docs/tests/acceptance/walk/` now shows the setup once, then each step the release still owes something from, with the screen the step happens on linked to its surface note. Each expectation line shows the check's own Expect text — the procedure quotes it word for word and the upstream validator checks the quote — beside the check parts it settles. A part already walked on this platform is shown struck through: the procedure covers the whole sitting, and the sheet prints the owed part of it.

**A procedure the module refuses falls back to the rows**, with the refusal printed in the module's own words. A stale script that vanished silently would leave the walker reading rows and wondering where the script went.

## The tick moved, and the ledger did not

A step can satisfy parts of several checks, so a step tick cannot be a verdict on its own. The page holds each step's mark and writes a check's verdict when every step citing that check has one.

- **The mark is the worst of them** (Edwin, 2026-09-14): `fail` over `partial` over `pass`, and a `question` on any citing step makes the whole check a question.
- **A check with one unticked citing step gets no ledger event.** A verdict written from half a walk would claim evidence nobody gathered.
- **A failing step is asked for its reason once**, and every check it cites gets that reason with the step number in front of it — which is what `ledger.NEEDS_REASON` already requires for every mark but `pass`.
- **Ticks live in the browser**, per workspace, keyed by release, platform, sitting and step. Never in the repo and never in the ledger: a half-walked check in either would be a second store ([[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]) and a ledger format change. A tick is forgotten once the step stops being printed, which is exactly when its check's event has been written.
- **The ledger's format is unchanged.** Still one event per check ([[ADR-0037-A-Verdict-Is-An-Event]]), the same keys, through `/api/notes/mark-check`. The POST is now built in one function, `postCheckVerdict`, which both the row tick and the step tick call — so the two cannot come to build different events.

A step tick may pass a check, and that stays inside [[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]: the rule is that a surface which does not show the procedure may not pass a check. This one shows it, and each expectation line quotes the check's own words.

## `~checks` groups by screen

The page grouped by the `area:` string, so the groups sorted by whatever that string happened to be. Once a repo's surfaces are screens with dialogs as children (upstream ADR-0044), a flat list of area names puts "HR-zone interval sheet" nowhere near "Workout editor". Groups are now the screen, with each child surface indented under its parent and labelled `in <screen>`; `subsystem` and `surface-less` surfaces follow the screens, because they are surfaces without being places. An `area:` matching no surface note is drawn last and marked — a surface rename orphans its checks silently ([[ISS-0250-A-Surface-Rename-Silently-Orphans-Its-Checks]]), and a group reading like every other one is how that goes unnoticed.

**The parent lookup is the bundled walk module's**, not a second reading of `parent:`. The field is written three ways across the fleet — a bare id, a wikilink, and the parent's title — and the first implementation to miss a spelling is where this page and `walk-sheet.py` start disagreeing about which screen a dialog belongs to.

The design view's Surfaces heading now counts **top-level screens** against [[FEAT-0130-Surfaces-Are-A-First-Class-Type]]'s 12 to 15 target, with children counted separately (Edwin, 2026-09-14). Counting every surface against a target set for screens told a repo that had named its dialogs properly it had three times too many places.

## Where the rules live

Unchanged from [[CHG-20260913-The-Walk-Page]] and worth restating, because this change is mostly about rendering what the module already computes: the survey rule, the procedure format and the placement are the template's, stated once upstream in `tools/instructions/TESTING.md` and implemented by `tools/scripts/walk-sheet.py`, which is bundled here verbatim as `src/project_os_cockpit/walk_sheet_bundled.py`. This page implements no survey rule and no procedure rule of its own.

`tests/test_walk_agreement.py` asserts the two agree, on a two-platform fixture always and on `your-trainer`'s live corpus when that repo is checked out: the survey's screens and capture keys, the sitting order, the printed step numbers, and the owed set, for every platform the repo keeps a ledger for.

## Documentation Coverage (All Types Considered)

- features: updated
- requirements: not-applicable
- tasks: updated
- issues: new
- tests: updated
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new
- snapshot: updated

## Follow-ups

- [ ] [[TASK-0626-The-Page-And-The-Sheet-Agree-On-Your-Trainer]] is not finished: its live comparison runs and passes, but `your-trainer` has no procedures yet (its TASK-0906), so nothing exercises the procedure half of it on real content. Walking [[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]] by hand waits on the same thing.
- [ ] [[ISS-0306-This-Repos-Own-Screens-Have-No-Surface-Notes]] — this change's own Impact section could name no screen id.
