---
type: "[[test]]"
id: TST-0092
aliases: ["TST-0092"]
title: "A release test section is opened from the Tests pane, results given on its checks show at once in the pane and the overview, and the ledger holds the same events as marking the checks directly"
status: active
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-27
updated: 2026-09-27
source: ["[[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]"]
scope: feature
level: acceptance
entrypoint: "Tests pane, Release test"
command: ""
last_verified: 2026-09-27
covers: ["[[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]"]
issues: []
tasks: ["[[TASK-0645-Pilot-The-Equipment-Section-Then-The-Rest]]"]
artifacts: ["__attachments__/TST-0092-section-page.jpg", "__attachments__/TST-0092-overview-after-results.jpg", "__attachments__/TST-0092-pane-needs-you-count.png"]
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
review_round: ""
related: ["[[TST-0088-The-Walk-Page-Hands-Over-The-Owed-Checks]]", "[[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]]", "[[ISS-0263-A-Write-Evicts-The-Reader-From-The-Checks-Page]]"]
area: "the release test"
after: []
tags: [test, acceptance, release-test]
---

# A release test section is tested from the Tests pane

## Purpose

Proves that a person can open one section of a release test from the Tests pane, give results where they read each check, and see progress everywhere at once, without the page moving them and without a second write path to the ledger.

## Setup

The desktop app on a copy of Your Trainer's docs and release ledger, with the Android release open. Copy the working ledger file aside before starting so it can be compared afterwards. Use the Equipment Hub section once Your Trainer's rewrite of it exists; until then any section with at least ten checks.

## Steps

1. Open the Tests pane and look at its first group.
2. Choose the Android row.
3. Note the next check Continue names, then choose Continue.
4. Read the section page from the top without scrolling past the first group.
5. Give the first check Pass. Give the second Fail and type a reason. Give the third Blocked from More without a reason, then add one.
6. Look at the pane and the scroll position. Go back to the overview.
7. Choose a Needs you entry.
8. Give every remaining check of one test note a result, then compare the ledger copy with the copy set aside.
9. Open `~walk/android` by address.

## Expect

- Step 1: "Release test · <version>" is the pane's first group, above "Feature tests" and "Regression tests", with one row per platform and its sections under Android.
- Step 2: the overview shows a bar coloured by result, Continue, Needs you and the section list with a bench line each.
- Step 3: the section Continue named opens with that check in view.
- Step 4: what changed comes first, Setup is folded, and each check is one action line and one expected line after an arrow, with its test tag.
- Step 5: Pass is one tap. Fail and Blocked are not saved until a reason is typed. Each row takes its result's colour.
- Step 6: the page did not move. The section's dot and count in the pane changed; the overview's bar, counts and Needs you show the Fail and the Blocked with their reasons.
- Step 7: the entry opens its check.
- Step 8: the ledger copy gained one event per test note given all its results, with the worst result, as marking that test note directly would.
- Step 9: the Android release test overview opens.

## Not this check

- Whether the sections, groups and "Start:" lines are well written. That is Your Trainer's notes and project-os-dev's generator.
- Evidence capture and timers. They keep the behaviour REQ-0069 describes and are covered by the renderer tests.

## Tested 2026-09-27 (model:claude-opus-5-5)

Tested by an agent session, not by Edwin, in a browser on `desktop/harness/live-harness.html`. The cockpit server ran on a scratch copy of your-trainer at `bbd72118`, so the release test was REL-0017 on Android. Edwin had looked at the same pages in the desktop app that day ("It looks great").

1. The Tests pane's first group is "Release test · v2.2.0", above "Feature tests", "Regression tests", "Automated tests" and "Retired". It has an Android and an iOS row, and Android's sections are listed with a dot and a bar each. **The step used to say "under Acceptance tests"; the pane has never had that heading, so the step and its line now say what the pane does.**
2. The Android overview showed the bar split by result, "4 Pass · 8 Fail · 13 Excused", Continue, Needs you and the section list with a bench line each.
3. Continue named Fresh install, check 1, and opened that section with check 1 in view.
4. What changed came first with its pictures, then Setup folded ("1 thing on the bench · 3 steps before you start · 2 later"), then the grouped checks: action, arrow, expected line, tag.
5. Pass on check 1 took one tap. Fail on check 2 and Blocked (from More) on check 3 each opened a reason box outlined in red, and nothing was written to the ledger until every check of the test note had a result. Each row took its result's colour.
6. The page kept its place. The pane's Fresh install dot turned red and its count moved to 3/6. The overview's counts, Continue (now check 4) and Needs you showed the Fail and the Blocked with their reasons.
7. The Needs you entry opened Fresh install with check 2 in view.
8. Giving checks 4 and 5 Pass completed TST-0456. The scratch ledger gained exactly one event, `{"check": "TST-0456", "result": "fail", "method": "manual", "by": "user:edwin", "reason": "check 2: …; check 3: …"}`, which is the worst result with each reason named by check.
9. `~walk/android` opened `~release-test/android`.

Two page defects were found and fixed during the walk. The count of Needs you entries on the platform row drew at the top of the pane, because it borrowed the mode buttons' absolutely placed badge style; it now sits on the row. And the overview's section list drew a half dot for a section holding a Fail, where the pane drew red; both now use one rule. Screenshots are in `artifacts:`.
