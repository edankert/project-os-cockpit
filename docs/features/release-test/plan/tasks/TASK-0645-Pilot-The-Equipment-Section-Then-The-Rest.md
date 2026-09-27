---
type: "[[task]]"
id: TASK-0645
title: "Pilot: Your Trainer's Android Equipment Hub section end to end, compared with the example page; then the other Android sections; then iOS"
status: doing
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-27
updated: 2026-09-27
source: ["Edwin, 2026-09-27: pilot one section end to end, compare with the example, then the rest, then iOS"]
parent: "[[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]"
effort: "M"
due: ""
depends: ["[[TASK-0643-The-Section-Page-And-Its-Results]]"]
blocks: ["[[TASK-0644-Retire-The-Walk-Page-In-The-Publication-View]]"]
related: ["[[TST-0092-A-Release-Test-Section-Is-Tested-From-The-Tests-Pane]]"]
tests: ["[[TST-0092-A-Release-Test-Section-Is-Tested-From-The-Tests-Pane]]"]
---

# Pilot the equipment section, then the rest

## Definition of Done

- [ ] Your Trainer's Android Equipment Hub section, rewritten in your-trainer (your-trainer FEAT-0129, the rewrite of the procedures and test notes with the Equipment section pilot), renders in the cockpit from a copy of Your Trainer's docs and ledger.
- [ ] It is compared with `../../__attachments__/release-test-example/index.html` part by part: header, what changed, Setup, each group and each check. Every difference is listed below with whether it is fixed here, in the generator (project-os-dev), or in Your Trainer's notes.
- [ ] Edwin has looked at the rendered pilot section beside the example and said whether it matches. That answer is quoted here.
- [ ] Only then: every other Android section renders, and the Android overview's totals equal `ledger.owed` for Android.
- [ ] Then the same for iOS.
- [ ] No ledger outside a copy is written by this task.

## Differences from the example

None recorded yet.

## Notes

Complexity: Medium for the pilot section, judged by how much it touches. No time estimates.

## Progress, 2026-09-27

The page is built (TASK-0639 to TASK-0643) and your-trainer's Equipment section is rewritten (your-trainer TASK-0975). The section was opened in this page through `desktop/harness/live-harness.html` on a scratch copy of your-trainer, and it matches the approved example's layout; the differences and why are in your-trainer TASK-0975's notes, with screenshots in your-trainer `docs/features/release-test/evidence/`. **Waiting on Edwin** to compare it with the example in the real app and say whether the other sections follow it. The desktop app needs a restart to load this code.

## Edwin's review of the pilot, 2026-09-27

> "First issue is that the left hand pane does not allow to select the sections only allows to select the android main section, the android page does allow you to select these sections, which is correct, I like the android page both the section pages and the android top section page can make better use of the overall screen-width though. Second issue is that I think the total number is incorrect, I see a number 95 todo on the acceptance page but I see 25/355 done on the release test section? But other than that the overall setup is now really good."

What each point is, and where it is fixed:

1. **The pane's sections were there but folded** behind a small count toggle under each platform row. They now show under a platform by default, and always under the platform being read (TASK-0641).
2. **The pages are narrower than the window** (860 px, the example's width). They now widen with the window (TASK-0642, TASK-0643).
3. **The two numbers count different things.** 355 is printed checks, the numbered steps, and 25 of them have a result, a Fail included. The acceptance page counts test notes: 86 manual notes still owed on Android, plus 9 automated notes with no result, which is the 95. The page and the pane now name their unit and also show test notes still owed, which matches the acceptance page's manual count (TASK-0642).
