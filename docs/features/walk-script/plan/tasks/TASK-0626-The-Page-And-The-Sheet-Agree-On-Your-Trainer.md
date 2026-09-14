---
type: "[[task]]"
id: TASK-0626
aliases: ["TASK-0626"]
title: "On your-trainer, for Android and iOS, the walk page and walk-sheet.py agree on the survey screens, the sitting order, the printed steps and the owed set"
status: backlog
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
- [ ] The live-corpus test compares, for `android` and `ios`: survey surface ids, sitting order, printed step ids per sitting, and owed check ids, between `acceptance.walk_payload` and the bundled module run the way `walk-sheet.py` runs it. All four are equal.
- [ ] The test also asserts the payload's `errors` list is empty, closing FEAT-0149's review finding 5 for this path.
- [ ] Walk one sitting by hand on `~walk/android` and record the result on TST-0089.
- [ ] The capability register rows for the survey cards, procedure rendering and step ticks are added or changed.
