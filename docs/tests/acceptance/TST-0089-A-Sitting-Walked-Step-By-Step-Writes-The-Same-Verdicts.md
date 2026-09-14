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
last_verified: "2026-09-14"
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

## Walked, 2026-09-14 — `partial`

Steps 1 to 7 were walked against the fixture repo this check's Setup allows, in a browser on `desktop/harness/live-harness.html` behind a one-origin proxy, over a real sidecar and a real ledger file. What was observed, against each Expect line:

- **Step 2.** Two cards: `Ride cockpit (SUR-0001)` with `ride-cockpit` and `ride-cockpit-dataonly (data-only)` before and after, and `HR-zone interval sheet (SUR-0002)` drawn inside it, marked `— new` because it has a candidate capture and no previous one. Both pictures of a pair rendered at 358 px. No `TST-` string anywhere in the survey.
- **Step 3.** The setup printed once for a sitting of three owed checks. Every step named its screen. The step lines showed words, not Markdown — which they did not on the first render; see below.
- **Step 4.** Ticking step 2 alone, with step 1 unticked, wrote **nothing**: the ledger file was byte-identical afterwards, and the page said `TST-0001 … waiting on step 1`.
- **Step 5.** After a reload the tick on step 2 was still shown and the page was where it was left.
- **Step 6.** Step 1 `pass`, then step 2 `fail` with a reason, wrote one event: `TST-0001`, `fail`, `reason: "Step 2: the cadence stuck at 42 for eight seconds"`, `method: manual`, platform android. Ticking step 1 had already written `TST-0004` as `pass` — its only citing step — and ticking step 3 wrote `TST-0002`, after which step 3 stopped printing and its stored tick was gone.
- **Step 7.** The ledger carried exactly one event per settled check, with the keys it carried before: `check`, `date`, `mark`, `by`, `method`, and `reason` where there was one.

**Why `partial` and not `pass`.** Step 8 — ticking the same checks one by one on the fallback rows and comparing two ledgers by hand — was not walked. It is asserted instead by the node test *"walking a sitting step by step writes the same events as ticking its checks one by one"*, which runs both paths against one stubbed POST and compares the request bodies. That is a stronger comparison than a person reading two files, and it is not this check.

Nothing here was walked on `your-trainer`: it has no procedures yet ([[TASK-0626-The-Page-And-The-Sheet-Agree-On-Your-Trainer]]).

**Two defects the walk found, both fixed with tests before this was recorded.**

1. The step's own line printed its Markdown: `**Ride cockpit.** Pedal for five seconds`, asterisks and all, on the page and again in the mark dialog's title. The node suite could not see it — its DOM stub has no reader. Emphasis markers are now stripped where the line is drawn and where the dialog is named.
2. The walk route resolved the **platform** from the open release and left the **release** empty, so every payload came back with `release: ""`. A step tick is keyed by release, platform, sitting and step, so a tick left over from one walk would have shown as already ticked on the next. The route now resolves the release the same way it resolves the platform, and the page header names it.
