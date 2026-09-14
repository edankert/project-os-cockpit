---
type: "[[task]]"
id: TASK-0626
aliases: ["TASK-0626"]
title: "The walk page and walk-sheet.py are asserted to agree on the survey screens, the sitting order, the printed steps and the owed set, on every platform a repo keeps a ledger for — your-trainer included, for as much as that repo carries"
status: done
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

- [x] The live-corpus test compares, for every platform the repo keeps a ledger for: survey surface ids and capture keys, sitting order, printed step ids per sitting, and owed check ids, between `acceptance.walk_payload` and the bundled module run the way `walk-sheet.py` runs it. All four are equal. — `tests/test_walk_agreement.py`, passing on `your-trainer`'s `android` and `ios`.
- [x] The test also asserts the payload's `errors` list is empty, closing FEAT-0149's review finding 5 for this path.
- [x] The procedure half of the comparison is exercised, on a two-platform fixture with a screen, a child dialog and a three-step procedure — because `your-trainer` carries no procedures to exercise it on.
- [x] A sitting is walked step by step in a browser and the ledger it writes is checked. — done on that fixture through `desktop/harness/live-harness.html` over a real sidecar; recorded on [[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]].
- [x] The capability register rows for the survey cards, procedure rendering and step ticks are added or changed.

## Scope, settled by Edwin on 2026-09-14

> "Finish the project-os-cockpit phase only, the your-trainer functionality will be handled in the your-trainer repo."

So this task is **this repo's half**: the comparison is written, it runs on `your-trainer`'s live corpus on both platforms, and it needs no edit when that repo gains procedures — it reads the ledger directory rather than naming platforms, and compares each sitting's procedure whenever there is one.

**The run against real v2.2.0 procedures belongs to your-trainer**, and that repo's plan already owns it: its `TASK-0907` carries the line *"project-os-cockpit TASK-0626 has run against this repo: `~walk/android` and `~walk/ios` agree with the sheet on survey, sittings, steps and owed set"*, and a second line for ticking a real sitting step by step. Nothing has to change here for that to happen.

Two boxes this note used to carry are therefore gone rather than unticked, because they were never this repo's to tick: *"your-trainer TASK-0906 is done"* and *"walk one sitting by hand on `~walk/android`"* (meaning your-trainer's Android). Both are your-trainer TASK-0907's, verbatim.

## Next Actions

None here. What remains is your-trainer's, in your-trainer, and its own notes carry it:

1. **your-trainer TASK-0900 to TASK-0902** — its surfaces become screens with dialogs as children. Today its `SUR-*` notes are merged test categories (`SUR-0003` is "Hardware", which spans five screens), so the survey and the `~checks` grouping this phase built have nothing true to group by there.
2. **your-trainer TASK-0904 to TASK-0906** — the v2.2.0 procedures under `docs/tests/acceptance/walk/`, one file per sitting, each expectation line quoting its check's `## Expect` text word for word, plus the capture map. `python3 tools/scripts/walk-sheet.py --check` is the gate they must pass.
3. **Then your-trainer TASK-0907**, which runs this repo's comparison against that corpus and ticks a real sitting step by step on a copy of its ledger. `tests/test_walk_agreement.py` is what it runs; it needs no edit.

**Nothing here is waiting on a decision or on more code in this repo.** The page, the payload and the tests are done and committed (`CHG-20260914`).

### The chain ends at a person, and that was designed

Read end to end on 2026-09-14, from the notes rather than from memory:

| step | what it needs | where that is written |
| --- | --- | --- |
| this task | your-trainer TASK-0906 done | its own Definition of Done, box 1 |
| your-trainer TASK-0906 | TASK-0902 and TASK-0905 | `depends:` on TASK-0906; and its DoD box 6, "every step names a surface from the **approved list** (TASK-0900)" |
| your-trainer TASK-0902 | TASK-0900 and TASK-0901 | `depends:` on TASK-0902 |
| your-trainer TASK-0900 | **Edwin's approval of the screen mapping table** | its DoD box 8: *"Edwin has approved the table … Until then this task stays `doing` and TASK-0901 and TASK-0902 do not start."* |

All eight of your-trainer's PHASE-024 tasks are `backlog`; none has started. So **no amount of work in this repository closes this task**, and no amount of work in your-trainer closes it either until Edwin has read and approved a table that does not exist yet. TASK-0900 is a deliberate review gate, described in its own note as "the first review gate of PHASE-024", on the ground that rewriting `area:` across 649 notes "is cheap to do and expensive to undo".

The one forward move available without Edwin is drafting that table — TASK-0900's own Next Actions say *"Draft the table now … Then stop."* That is your-trainer PHASE-024's work, not this phase's, and [[PHASE-044-The-Walk-Page-Reads-As-A-Script]]'s Out of Scope list rules it out here. Edwin's instruction on the same day was *"v2.2.0 should wait."*

## Notes

**Approaches set aside.**

- **Writing your-trainer's procedures from this session.** Set aside because [[PHASE-044-The-Walk-Page-Reads-As-A-Script]]'s Out of Scope list says, in its own words, "Writing procedures or change notes for any repo" — and because a procedure's expectation lines must quote each check's `## Expect` text exactly, against screens nobody in this session has looked at. A procedure written from the note text alone would pass the validator and describe a product it had never seen.
- **A DOM test for the `~checks` screen grouping.** Set aside for a source-level guard plus payload tests: the checks page has no node harness, and `paintCheckList` reaches a dozen helpers. The grouping decision lives in `view_payload` and is tested there against real payloads; what is left in the page is an indent and a label. Recorded because the next person will weigh the same trade.
- **Rendering the procedure's Markdown.** The step lines carry `**bold**`, and running them through a Markdown renderer was considered and dropped: it would put an HTML pipeline inside the control a verdict is given from. The markers are stripped instead.

**Edwin's decisions, in his words.** From 2026-09-14, on the questions that shaped the tick: *"v2.2.0 should wait. go with your recommendations for the others, will I start the project-os-dev and cockpit phase first?"* — and on the goal itself: *"A tick in the cockpit records the verdict for every check that step satisfies."* The first is why `your-trainer`'s v2.2.0 work has not happened and this task is blocked; it was his instruction, not an oversight.
