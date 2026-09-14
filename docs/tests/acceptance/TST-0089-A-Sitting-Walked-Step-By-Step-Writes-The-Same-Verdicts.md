---
type: "[[test]]"
id: TST-0089
aliases: ["TST-0089"]
title: "A sitting walked step by step on the walk page writes the same ledger verdicts as its checks ticked one by one, under screen cards that show before and after"
status: active
phase: "[[PHASE-044-The-Walk-Page-Reads-As-A-Script]]"
owner: user:edwin
created: 2026-09-14
updated: 2026-09-14
source: ["[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]"]
scope: feature
level: acceptance
entrypoint: "~walk/<platform>"
command: ""
last_verified: ""
covers: ["[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]"]
issues: []
tasks: ["[[TASK-0622-The-Survey-As-Screen-Cards]]", "[[TASK-0623-Each-Sitting-As-Its-Procedure]]", "[[TASK-0624-A-Tick-Per-Step]]", "[[TASK-0626-The-Page-And-The-Sheet-Agree-On-Your-Trainer]]"]
artifacts: []
last_run: ""
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TST-0088-The-Walk-Page-Hands-Over-The-Owed-Checks]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]"]
tier: "1"
area: "the walk"
after: ["TST-0088"]
tags: [test, acceptance, publication]
---

# A sitting walked step by step writes the same verdicts

## Setup

The desktop app with a workspace whose release is `draft`, whose WALK.md has at least one sitting with a procedure, and whose ledger has at least one check in that sitting already passed. Before your-trainer's v2.2.0 procedures exist, use the fixture repo TASK-0624 builds. Copy the working ledger file aside before starting, so it can be compared afterwards.

## Steps

1. Open the walk page for the release's platform from the release rung.
2. Look at the survey.
3. Scroll to the sitting with a procedure.
4. Tick every step except the last one that cites some check, with `pass`.
5. Reload the page and return to the sitting.
6. Tick the last step with `fail` and give a reason.
7. Compare the working ledger with the copy from Setup.
8. On a second copy of the same fixture, tick the same checks one by one on the per-check rows (open the sitting's fallback by removing its procedure), with the same combined marks, and compare the two ledgers.

## Expect

- Step 2: one card per changed screen, each with a sentence, and before and after pictures where both exist. No `TST-` id on any card.
- Step 3: the setup appears once. Steps name their screen. A tag for the already-passed check is shown as passed.
- Step 4: no new ledger event for the check whose last step is unticked.
- Step 5: the ticks from step 4 are still shown, and the page is where it was.
- Step 6: one ledger event per check that step completed, `fail` for the checks the last step cites, `pass` for checks whose steps were all ticked `pass` earlier, each with the walk's platform and `method: manual`.
- Step 8: the two ledgers carry the same events, check for check and mark for mark, apart from timestamps.

## Not this check

- The survey's and procedure's content rules. Those are upstream's (project-os-dev TST-0010, TST-0011).
- The checks page grouping (TASK-0625).
