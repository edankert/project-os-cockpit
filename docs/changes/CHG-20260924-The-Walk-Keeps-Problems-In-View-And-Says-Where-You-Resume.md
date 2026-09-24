---
type: "[[change]]"
id: CHG-20260924-The-Walk-Keeps-Problems-In-View-And-Says-Where-You-Resume
title: "The walk keeps recorded problems in view, returns to the saved step, and says what to restore when you resume"
status: merged
owner: user:edwin
created: 2026-09-24
updated: 2026-09-24
source: ["[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"]
commit: ""
pr: ""
impacts: ["[[SUR-0004-The-Release-Walk]]"]
issues: []
features: ["[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0629-Show-One-Walk-Action-And-Its-Readiness]]", "[[TASK-0630-Record-And-Resume-Walk-Observations]]", "[[REQ-0068-The-Walk-Records-One-Clear-Observation-At-A-Time]]", "[[REQ-0069-The-Walk-Resumes-With-Valid-Evidence]]"]
---

# The walk keeps recorded problems in view, returns to the saved step, and says what to restore when you resume

## Summary

A step marked fail, partial or question now stays on screen after it is recorded, and stays listed at the top of the walk after the walker moves on. Before this change, **Something wrong…** advanced to the next step like a pass, so the problem just recorded disappeared.

The other changes, each against one of FEAT-0151's detailed criteria:

- **Continue returns to the saved step (B1, B3, B4).** Leaving the changed-screen review used to restart at step 1 of the first session. A fresh walk now says **Start tests**, and a walk with a saved position says **Continue at step N** and goes there.
- **Progress is counted (B3).** The session shows "3 of 12 done · 1 needs attention". Waiting, readiness and evidence lines use the step positions the cards show, not the procedure file's numbers.
- **Arrow keys move between screens and steps (B5).** They record nothing, and they do nothing while typing in a field or while the mark dialog is open.
- **I can't perform this returns to the step (B6).** The step's own declared reason goes into the decision dialog. The card then shows the decision it recorded.
- **The results summary counts this walk's results (B9).** It was built from the payload loaded when the page opened, so a check passed during the walk read "no current verdict". It now lists what this walk cleared. A check still waiting on some of its steps says which ones, and names any step already marked as a problem.
- **A reopened walk says what to restore (C1, C2).** The first step after a restart says the walk is being resumed, the state the app must be put back in, the earlier steps that get it there, and that the cockpit has not checked the app.
- **Old evidence and old marks are named, never reused (C3).** Evidence saved before a candidate change made its checks owed again no longer answers the later comparison. A step whose instructions changed shows the mark given to the earlier version and says it does not count.
- **A changed procedure lands on the nearest step (C7).** When the saved step no longer exists, the page goes to the same step rewritten, or to the step at the same position, and says why. It used to jump to the first unmarked step without a word.
- **The per-check list in the details is redrawn after each mark.** It still said "waiting on steps 1, 3" after step 1 was marked.

The ledger format, the combination rule and the write path are unchanged.

## Impact

- [[SUR-0004-The-Release-Walk]]: A recorded problem stays on its step and in a "Needs attention" list; Continue returns to the saved step; a reopened walk says what state to restore; arrow keys move between steps.

## Evidence

Fourteen new renderer tests in `desktop/tests/walk-page.test.mjs`, one or more per criterion, drive the built page through its own controls. Each of the eleven new behaviours was broken on purpose in the built bundle, and each break failed its test. The full desktop suite passes 236 of 237 tests with one integration-only skip; 81 Python walk tests pass. The page was also rendered in Chrome against a copy of Your Trainer's REL-0017 Android walk (86 owed checks, 13 sessions): a pass, a fail through the real mark dialog, an arrow-key move and a full reload showed the resume notice, the attention list and the summary line "observed in part (step 2 fail so far)". The copy's ledger took the two writes; Your Trainer's own ledger was not touched.

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated
- requirements: updated
- tasks: updated
- issues: not-applicable
- tests: updated
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new
- snapshot: updated

## Follow-ups
- [ ] Edwin's own walk of the page (Your Trainer TASK-0923, criterion D4) and the verification in TASK-0631, which waits on Your Trainer TASK-0960.
