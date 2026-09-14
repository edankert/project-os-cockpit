---
type: "[[task]]"
id: TASK-0626
aliases: ["TASK-0626"]
title: "On your-trainer, for Android and iOS, the walk page and walk-sheet.py agree on the survey screens, the sitting order, the printed steps and the owed set"
status: doing
phase: "[[PHASE-044-The-Walk-Page-Reads-As-A-Script]]"
owner: user:edwin
created: 2026-09-14
updated: 2026-09-14
source: ["[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]", "Edwin's goal, 2026-09-14: 'The cockpit walk page and walk-sheet.py agree on survey, sittings, steps and owed set for both platforms.'"]
parent: "[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]"
effort: S
due: ""
depends: ["[[TASK-0622-The-Survey-As-Screen-Cards]]", "[[TASK-0623-Each-Sitting-As-Its-Procedure]]", "[[TASK-0624-A-Tick-Per-Step]]"]
blocks: []
related: ["[[TASK-0618-The-Walk-Payload]]"]
tests: ["[[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]]"]
tags: [task, acceptance, walk]
---

# The page and the sheet agree on your-trainer

## Why

The goal's last "done when" line. FEAT-0149 already has a live-corpus test that the walk payload's rows equal `ledger.owed()` on your-trainer, skipped when that repo is not checked out. This extends it to the new survey and procedures, and runs it on both platforms.

## Definition of Done

- [ ] your-trainer TASK-0906 is done (its v2.2.0 procedures exist and pass the validator).
- [x] The live-corpus test compares, for `android` and `ios`: survey surface ids, sitting order, printed step ids per sitting, and owed check ids, between `acceptance.walk_payload` and the bundled module run the way `walk-sheet.py` runs it. All four are equal.
- [x] The test also asserts the payload's `errors` list is empty, closing FEAT-0149's review finding 5 for this path.
- [ ] Walk one sitting by hand on `~walk/android` and record the result on TST-0089.
- [x] The capability register rows for the survey cards, procedure rendering and step ticks are added or changed.

## Where this stands, 2026-09-14

**The test is written and it passes on both of `your-trainer`'s platforms.** `tests/test_walk_agreement.py` compares the page and the sheet on the survey's screens and capture keys, the sitting order, each sitting's printed step numbers and the owed set, for every platform that repo keeps a ledger for. It reads the ledger directory rather than naming `android` and `ios`, so it needs no edit when a third arrives.

**Two boxes are not ticked and neither is this repo's to tick.** `your-trainer` has no `docs/tests/acceptance/walk/` directory at all: its TASK-0906 has not been done, so its v2.2.0 procedures do not exist. The comparison therefore runs today with both sides agreeing that every sitting has no procedure — which is a real agreement and a weak one. The procedure half of the comparison is exercised by the two-platform fixture in the same file, and on real content it is exercised the day TASK-0906 lands. Walking [[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]] on `~walk/android` waits on exactly the same thing.

Writing those procedures is out of this phase's scope by its own Out of Scope list. This task stays `doing` rather than `done` so that the record says the walk was never run on real procedures, which is the fact a reader needs.
