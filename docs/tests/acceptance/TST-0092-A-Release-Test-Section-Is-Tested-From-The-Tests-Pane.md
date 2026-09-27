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
entrypoint: "Tests pane, Acceptance tests, Release test"
command: ""
last_verified: ""
covers: ["[[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]"]
issues: []
tasks: ["[[TASK-0645-Pilot-The-Equipment-Section-Then-The-Rest]]"]
artifacts: []
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

1. Open the Tests pane and look under "Acceptance tests".
2. Choose the Android row.
3. Note the next check Continue names, then choose Continue.
4. Read the section page from the top without scrolling past the first group.
5. Give the first check Pass. Give the second Fail and type a reason. Give the third Blocked from More without a reason, then add one.
6. Look at the pane and the scroll position. Go back to the overview.
7. Choose a Needs you entry.
8. Give every remaining check of one test note a result, then compare the ledger copy with the copy set aside.
9. Open `~walk/android` by address.

## Expect

- Step 1: "Release test · <version>" sits under "Acceptance tests", above "Feature tests" and "Regression tests", with one row per platform and its sections under Android.
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
