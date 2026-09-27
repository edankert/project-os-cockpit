---
type: "[[feature]]"
id: FEAT-0151
aliases: ["FEAT-0151"]
title: "The release walk has one clear next action"
status: superseded
superseded_by: "[[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]"
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-16
updated: 2026-09-27
source: ["Your Trainer FEAT-0122, 2026-09-16: implement and test the guided release walk fully"]
goal: "A person can perform, record and resume each owed release observation from one focused page with its necessary preparation."
requirements: ["[[REQ-0066-The-Release-Walk-Keeps-Observation-Context]]", "[[REQ-0067-The-Walk-Keeps-Required-Actions-And-Only-Relevant-Setup]]", "[[REQ-0068-The-Walk-Records-One-Clear-Observation-At-A-Time]]", "[[REQ-0069-The-Walk-Resumes-With-Valid-Evidence]]"]
tasks: ["[[TASK-0629-Show-One-Walk-Action-And-Its-Readiness]]", "[[TASK-0630-Record-And-Resume-Walk-Observations]]", "[[TASK-0631-Verify-The-Guided-Walk]]"]
release: ""
acceptance_exception: "The walk that accepts this page is Edwin walking Your Trainer's owed checks through it: criterion D4, Your Trainer TASK-0923. This repository has no release walk of its own to host that check. The browser walk of Your Trainer's corpus on 2026-09-25 is recorded in TASK-0631."
reviewed_by: "model:claude-opus-5 (two independent-reviewer subagents, clean context)"
review_date: 2026-09-25
review_round: 2
review_verdict: approved
related: ["[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]", "[[RISK-0010-Saved-Walk-Observations-Can-Outlive-Their-Source]]", "[[SUR-0004-The-Release-Walk]]"]
---

# The release walk has one clear next action

## Goal

Edwin can open a release walk and see the next screen or action, the exact result to look for, and the control that records it. He can pause and resume without guessing the app state or repeating a valid observation.

## Scope

The page uses the shared walk generator's survey, preparation, setup, platform and owed-check data. It opens with changed screens, then shows one current session step. Nearby steps, full setup, source links and check tags remain available on demand. It records marks where observations happen, retains evidence and reports failures without clearing unresolved work. The ledger schema and combination rule stay as they are.

When an authored check tag cannot be read, the page must show the procedure error and the complete per-check fallback. Another valid tag on that card cannot make the invalid one disappear without a warning.

The current action must show the most recent authored required state for its platform, including after an earlier step was omitted from the owed walk. The reminder describes what to restore; it does not say the app has been inspected.

When the source action begins with the same screen name and `SUR` id already shown in the card heading, the visible action starts after that label. The authored line remains available in the source procedure, and exact expected results remain unchanged.

The detailed criteria moved here from Your Trainer FEAT-0122 on 2026-09-24; they are listed under "Detailed criteria" below. This feature owns the page that meets them, for any project-os workspace.

## Acceptance

- [x] A fresh walk begins with the changed-screen review, and Continue returns to the saved screen or step for the same workspace, release and platform.
- [x] The current step shows its screen, authored action, exact owed expectations, required state and one primary Pass and next control. A preparation action has Continue and produces no verdict.
- [x] The page exposes relevant setup and readiness before execution. A blocked action remains visible with its affected checks, while independent work stays reachable.
- [x] Fail, Partial, Question and inability to perform are available with their required reasons and do not bulk-clear checks. Failed local or ledger writes stay visible and can be retried.
- [x] Saved observations, corrections and attachments survive a same-workspace restart. Edited actions or expectations do not silently inherit a mark; another release or platform does not inherit position or evidence.
- [x] A later comparison can open evidence captured earlier with its platform and source state. A user-started timer assists an authored wait and never marks a result.
- [x] The text sheet and page agree on both platforms, including the survey hierarchy, preparation, setup and owed set. Ledger-copy tests cover completion, interruption, correction and unresolved outcomes.

The first six are met by the detailed criteria below (evidence, 2026-09-24). The seventh is met by D1 and D2 (evidence, 2026-09-25).

## Links

- Requirements: [[REQ-0066-The-Release-Walk-Keeps-Observation-Context]], [[REQ-0067-The-Walk-Keeps-Required-Actions-And-Only-Relevant-Setup]], [[REQ-0068-The-Walk-Records-One-Clear-Observation-At-A-Time]], [[REQ-0069-The-Walk-Resumes-With-Valid-Evidence]]. REQ-0067 to REQ-0069 were Your Trainer REQ-0209 to REQ-0211 until 2026-09-24.
- Tasks: [[TASK-0629-Show-One-Walk-Action-And-Its-Readiness]], [[TASK-0630-Record-And-Resume-Walk-Observations]], [[TASK-0631-Verify-The-Guided-Walk]].

## Detailed criteria (moved from Your Trainer FEAT-0122, 2026-09-24)

Your Trainer FEAT-0122 wrote these criteria on 2026-09-16 and tracked them there until 2026-09-24. They describe the page and the generator, not Your Trainer, so they are checked here now. The letters are unchanged, so earlier evidence and change notes still point at the right criterion. The ticks are copied as they stood. The evidence for each met criterion is in Your Trainer FEAT-0122 under "Implementation evidence", and in this note's own evidence section below.

Some criteria stayed in Your Trainer because only its procedure notes can meet them. A3, A5, A6 and A8 are the procedure audits in Your Trainer TASK-0960, and A7 is already met there. D4, Edwin's walk of Your Trainer's checks, is Your Trainer TASK-0923. This page is finished when every criterion below is met. The walk as a whole is finished when those Your Trainer criteria are met too.

A1, A2 and A4 are delivered by the shared generator in project-os-dev FEAT-0033 (TASK-0125). This page only shows what the generator produces.

### Instructions and readiness

- [x] **A1 — Complete route to each observation.** With only the FREE-rides procedure's current steps 3 and 6 owed, the generated walk includes starting Sweet Spot Base and reaching its end. Those preparation actions write no verdict for settled checks.
- [x] **A2 — Relevant setup.** With only the final language sweep owed, its setup contains no AI key, translation fixture, mail account or hosted-redirect requirement solely needed by omitted tests. Every remaining prerequisite can be traced to retained work.
- [x] **A4 — Declared prerequisites.** Missing or cyclic dependencies are detected. The walk retains valid preparation in authored order and cannot silently drop an owed observation when its preparation is invalid.

### Presentation and recording

- [x] **B1 — Survey first, without extra bookkeeping.** A fresh walk starts with changed screens and one selected comparison. Continue to tests requires no per-image reviewed ticks. Returning restores the last viewed screen when appropriate.
- [x] **B2 — Correct comparison.** Child screens have the correct parent even when only the child changed. Distinct changes remain discoverable, before and after images are equally sized, and missing evidence is stated. Relevant images can also be opened beside the test step.
- [x] **B3 — Clear context and progress.** The page names release and platform. Start and Continue reflect saved position. The current session shows consecutive display positions, completed actions and the number needing attention, with source numbers and remaining check count secondary.
- [x] **B4 — Flexible focus.** One session step is expanded by default. Full setup, nearby steps and the full session are reachable without losing place or saved work. The main path contains no duplicate setup prose.
- [x] **B5 — One action for success.** Screen, action and exact owed expectations are visible beside Pass and next. One activation saves that step and advances. Next, Previous, preparation completion and keyboard navigation alone create no test verdict.
- [x] **B6 — Exceptions with context.** Something wrong reveals Fail, Partial and Question with required reasons. I can't perform this carries the affected checks and reason into the existing decision flow and returns to the same context. It cannot automatically pass, excuse or mark a check not applicable.
- [x] **B7 — Details remain accessible.** Check ids and titles, change note links, capture metadata, procedure paths, omitted-step explanations and per-check waiting information are available on demand. An actionable failure or unresolved question remains visible in the main path.
- [x] **B8 — Correctable recording.** A saved step can be corrected, including after it contributed to a ledger verdict. History is preserved, accidental repeated activation produces no duplicate verdict event, and an intentional new run remains available.
- [x] **B9 — Honest completion.** Recording all runnable observations while another check is failed, questioned or unavailable leaves a needs-attention state and a clear unresolved summary. Viewing the survey or finishing navigation never clears the release gate.

### Resume and evidence

- [x] **C1 — Restart without repeating valid observations.** Leave midway through a check cited by several steps, restart the cockpit and return. Its saved observations, evidence and selected step survive in the same workspace and storage context; the check is not passed prematurely.
- [x] **C2 — Restore required app state.** After changing the app's rider, trainer or workout while away, resume shows the state needed for the selected step and how to restore it. It does not claim to have verified the live state automatically.
- [x] **C3 — Recognise changed work.** Editing a step's action or expectation without changing its tags flags affected saved observations for review. A different platform or release cannot inherit them. A candidate change follows the existing invalidation rules and does not silently reuse invalid evidence.
- [x] **C4 — Report persistence failures.** Refused local storage and a failed ledger write each produce a visible failure and retry path. The page distinguishes locally saved progress from a recorded verdict and does not advance past an unsaved observation as if successful.
- [x] **C5 — Evidence at the point of observation.** A procedure that currently asks for a note or screenshot to be recalled later collects it at that step. The later comparison displays the evidence with its originating state, build and platform. Resume retains it; its presence does not automatically pass the comparison.
- [x] **C6 — Timers assist observations.** A timed instruction offers a timer using the authored duration. Starting, finishing or interrupting it creates no verdict. The user can tell whether the required continuous observation needs restarting.
- [x] **C7 — Stable navigation.** Saving a mark does not unexpectedly move the reader, renumber the active card or hide a problem. When regenerated instructions alter the sequence, the page explains the change and restores the nearest valid position.

### Agreement

- [x] **D1 — One computed walk.** The cockpit and generated sheet agree on the survey hierarchy, session order, required preparation, observation steps, platform variants and owed checks for both platforms. Retained preparation does not enlarge the ledger's owed set.
- [x] **D2 — Verdict equivalence.** On ledger copies, run pass, partial, fail, question, correction and interrupted-check scenarios. Each yields the expected events under the existing combination rule; no incomplete multi-step check passes. Unchanged procedures produce the same verdicts as the previous flow.
- [x] **D3 — Existing boundaries.** No runtime prose inference, per-release authored worklist, new ledger schema, session time estimate or bulk pass is introduced. Required expectation wording remains validated against the source notes after corrections.

## Implementation evidence and remaining work

A real Chrome render of the Android payload on 2026-09-16 showed too many navigation controls above the current action. TASK-0629 moved occasional navigation under Walk options and moved repeated sitting state and equipment into required setup. The action card remains the main path. The focused renderer suite passes 77 cases, and a standalone Chrome harness rendered the current Android payload at 1100 and 700 pixels wide. A full Electron and Edwin walk remain open.

The same render found a surface id where a screen name belonged. The shared generator and both consumers now show Quick Ride cockpit in the action heading while keeping `SUR-0033` as its link target. The cockpit agreement fixture and another narrow Chrome render confirm it.

The authored `state_for` reminder now carries to later applicable steps and changes only at the next declaration, including when the declaration's own step is omitted. The current card displays it in a short line above the action. A narrow Chrome render of the current Android payload also found the screen and `SUR` id repeated at the start of the action; the visible action now begins with the instruction, while its original source and exact check quote remain intact. The built renderer's 78 focused tests pass. Full Electron and Edwin walks remain open.

The focused renderer now shows one changed screen, then one session step with the authored action, exact owed expectation and direct Pass and next control. Relevant setup, known readiness problems, required state, source detail, nearby steps and full session are available without opening a check note. Preparation produces no verdict. The shared generator provides declared prerequisites, setup, platform action wording, evidence links, timers and readiness; its two cockpit copies remain byte-identical.

The current browser tests cover survey focus, preparation, readiness dependencies, saved note comparison after restart, optional timer interruption, failed local storage, failed ledger write and retry, changed instructions, candidate invalidation, correction and duplicate suppression. The real Your Trainer Android and iOS corpus agrees with the sheet in the payload test. Ledger-copy tests cover pass, partial, fail, question and correction without touching the release ledger.

The renderer's step verdict requests now run against copies of both platform ledgers in an integration test. Pass, partial, fail, question, correction and an interrupted two-step check produce the expected ledger marks and history; the interrupted check writes nothing after its first observation. Four copied-ledger test cases pass. The browser and Edwin walk remain open.

A disposable Chrome session using the current Android payload confirmed the evidence comparison and unresolved-decision presentation. The later card showed a saved synthetic observation with its build and required state, blocked Pass while another source observation was missing, and enabled Pass after it was saved. A decision step showed its reason and affected check without recording a verdict when **I can't perform this** was opened. The harness stubbed server writes; full cockpit and human walks remain open. [[CHG-20260917-Verify-guided-walk-comparison-and-exception-in-Chrome]] records the scope.

The feature remains doing. The correction section rebuilds completed steps from the current authored procedure after their checks leave the owed payload. A changed step asks for a new run, an invalid procedure shows its check instructions and repair reason, and a failed correction returns to the owed walk. Focused renderer tests cover restart, duplicate suppression, intentional rerun and storage failure; the API fixture confirms the owed count does not change. At a source observation, the page saves a user-entered build and optional PNG; the later comparison shows both, and a verdict posted after attachment references the PNG. Focused renderer and HTTP route tests cover this flow. Full platform-specific corpus cleanup, a real browser walk and Edwin's human D4 walk still need evidence. Details and current risk are in [[RISK-0010-Saved-Walk-Observations-Can-Outlive-Their-Source]].

The isolated Electron walk now runs against copies of Your Trainer's docs and ledgers. It showed the eight-screen Android survey, advanced from the first action with one synthetic local observation, and restored step 2 after a renderer reload without writing a check verdict. At a later blocked step, Pass was disabled and **I can't perform this** showed its affected check. A one-minute timer was interrupted by a reload and requested a fresh continuous observation. A synthetic PNG uploaded at the data-only HR-Zone step appeared at the later KICKR comparison beside its source step, platform, release, build and state. The source Android and iOS ledgers were not written. [[CHG-20260917-Keep-guided-walk-readiness-quiet-after-start-and-add-step-picker]] folds the repeated session warning list once work begins and adds direct step selection; the focused renderer suite passes 80 cases. This covers more of the real browser path, while Edwin's human walk remains open.

The same real browser walk found a release-gate mismatch in **Review results**. The current Android payload owed 39 checks, but the summary listed 29 because it treated ten REL-0016 excuses as if they still cleared REL-0017. Excuses expire when their ledger seals. [[CHG-20260917-Show-expired-excuses-in-the-release-walk-review]] now uses the current owed rows and labels prior excuses as expired; a check with a newer rerun reason keeps that reason. The isolated Electron summary lists all 39 rows. The iOS route currently has 327 owed rows but no open iOS release id, so its heading and release-specific resume still need a platform decision before the full cross-platform walk can close.

The isolated iOS survey initially showed Android Developer Options copy and an Android capture. Your Trainer now declares REL-0001 as Android, so its live iOS payload has no previous release tag and no Android survey cards. [[CHG-20260917-Explain-unavailable-survey-when-a-platform-has-no-prior-release]] makes the empty survey say that comparison is unavailable and that the 327 owed checks remain accessible. The isolated Electron page confirms this state. A real iOS release and its screen evidence are still needed for the release-specific human walk; FEAT-0122 A8 remains open for the wider platform-path audit.

The renderer now reads current Your Trainer FREE ride procedure payloads for both platforms and emits pass requests from selected authored steps. Those requests equal marking the same checks directly, and both paths clear the checks on disposable copies of each platform's working ledger. The Android selection includes retained preparation with no verdict. The iOS selection includes TST-0370's two observation steps: the first does not settle it, the timed second refuses a mark without its saved note and build, and saving that evidence lets the final request match the direct check path. The full human route and broader unchanged-procedure audit remain open. [[CHG-20260917-Compare-a-real-walk-procedure-with-direct-check-verdicts]] and [[CHG-20260917-Verify-a-real-evidence-required-walk-verdict]] record the tests.

Fallback cards now read declared readiness from unscripted acceptance checks. A decision card shows its reason and offers only Blocked, Excused or Not applicable; a preparation card asks for confirmation before exposing the normal mark. The live iOS payload still owes 327 checks and now names eight Android-only Settings or backup decisions. The focused renderer suite passes 82 cases, with one integration-only case skipped, and the ten generator agreement and bundle tests pass. [[CHG-20260917-Show-readiness-on-unscripted-walk-cards]] records the UI change. Edwin's human walk remains open.

### Evidence, 2026-09-24: B1, B3 to B7, B9, C1 to C3, C7

TASK-0629 and TASK-0630 were finished against the detailed criteria on 2026-09-24, and [[CHG-20260924-The-Walk-Keeps-Problems-In-View-And-Says-Where-You-Resume]] records the page changes. Each criterion ticked that day has its own test in `desktop/tests/walk-page.test.mjs`, named by its letter (`B1: …`, `C7: …`). B6, B7 and part of C7 share one test. Each test drives the built page through its own controls. Each of the eleven new behaviours was broken on purpose in the built bundle and failed its test. The desktop suite passes 236 of 237 tests with one integration-only skip.

The page was also rendered in Chrome against a copy of Your Trainer's REL-0017 Android walk, which has 86 owed checks in 13 sessions. A pass, a fail through the real mark dialog, an arrow-key move and a full reload showed the resume notice, the "Needs attention" list, the "2 of 6 done · 1 needs attention" count and a summary line reading "observed in part (step 2 fail so far)". Only the copy's ledger was written.

D2 and D3 were still open that day; they are met below.

### Evidence, 2026-09-25: D2, D3

TASK-0631 met both on 2026-09-25, after Your Trainer TASK-0960 finished its procedure audits. The full account is in [[TASK-0631-Verify-The-Guided-Walk]] under "Result, 2026-09-25".

D2's last clause was that unchanged procedures produce the verdicts the previous flow did. A new test now walks every sitting on both platforms step by step through the built renderer: 1,223 steps in 27 sittings. It compares each sitting's requests with a direct Pass on each check. The two agree for all 366 checks the steps can record. The other 53 checks are held by a declared readiness problem, get no verdict from their steps, and stay owed on a ledger copy. Removing the readiness gate or the holding rule in the built renderer fails the test.

D3 was checked by audit. `walk-sheet.py --check` passes on Your Trainer for both platforms. The ledger module and its event format have not changed since this feature began. Every walk write is one check through `postCheckVerdict`. The walk has no time estimate and reads no rule from prose.

A browser walk against a copy of Your Trainer's current corpus showed the next action, the setup folding away after the first step, a decision-held step with **I can't perform this**, a resume after reload, and an evidence comparison. None of it needed a check note to be opened. A Fail through the real dialog wrote one event to the copy's ledger. The walk found two display defects, fixed in [[CHG-20260925-Walk-Setup-Reads-As-A-List]].

Every criterion in this note is now met. The walk as a whole is finished when Your Trainer's own criteria are met too: A3, A5, A6 and A8 in TASK-0960 are done, and D4, Edwin's walk, is Your Trainer TASK-0923.

## Verification

Full runs on 2026-09-25, after the last change:

- `node --test desktop/tests/*.test.mjs` (from `desktop/`, after `npm run build`, run after the round-1 fixes): 243 tests, 241 pass, 0 fail, 2 skipped. The two skips are the corpus tests that only run when the Python side hands them a payload.
- `.venv/bin/python -m pytest -q -p no:randomly` (the whole Python suite, run after the round-1 fixes): 2,199 passed, 6 skipped. The first run failed two guard tests, and both were fixed in [[CHG-20260925-Walk-Setup-Reads-As-A-List]].
- `.venv/bin/python -m pytest -q -p no:randomly tests/test_guided_walk_ledger_copy.py tests/test_walk_agreement.py tests/test_walk_bundle.py tests/test_walk_links.py tests/test_walk_payload.py tests/test_walk_route.py tests/test_walk_step_verdicts.py tests/test_walk_survey.py`: 83 passed.

## Handoff, 2026-09-25

**What was done.** TASK-0631 is done, and every criterion in this note and in REQ-0066 to REQ-0069 is ticked (0a2fcab, 42558af). The feature stays `doing` and the requirements stay `approved` until the independent review returns.

**What is next.** Two independent reviewers were started on a packet built from this feature's four source commits (476ee97, 9a8c73a, cda73d7, 0a2fcab). The packet leaves out the template syncs and the Codex commit that the packet tool picked up by subject, and the walk generator, which is reviewed upstream. Its diff is 5,834 lines, over the 1,500-line guideline. The author chose one review at that size rather than a split. Combine the two reports into a `## Review` section here, fix every finding about code this feature changed, then set this note `done` and the four requirements `implemented`. Close PHASE-043 again once nothing under it is open.

**Set aside.** Showing quoted expectations without their `**` bold markers was built and then reverted. The 2026-09-14 review decided the card shows the quote exactly as validated, and a test enforces it. The question is Edwin's: 176 quotes on Your Trainer's walk show the markers.

## Review

Round 1, 2026-09-25. Two independent reviewers worked from the same packet: this feature's four source commits, 5,834 diff lines. Both said the budget left most per-letter criteria *not checked*. Neither found fault with those criteria; they were not probed.

**Combined verdict: changes-requested.** One author claim is refuted.

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 1 | A step held by a declared readiness never writes a verdict for any check it cites, even when that check's other citing steps are all marked. | **refuted** | Reviewer B marked step 3 of a check cited by steps 1 and 3 while nothing was held. The procedure then gained `requires: {3: [4]}` and a readiness on step 4, so step 3 was held. Marking step 1 posted `pass` for the check. `markWalkStep` asks `walkUnready` only about the step being marked, and the settle loop asks only whether each citing step has a mark. `stepSignature` does not include `requires`, so the earlier mark survives the edit. Reviewer A's *holds* came from the corpus test, which never marks a step before its hold appears. |
| 2 | Walking a real sitting step by step with Pass sends exactly the same mark-check bodies as marking each check Pass directly. | holds | Both reviewers: the corpus test's `deepEqual` passes on both platforms, and `tests/test_guided_walk_ledger_copy.py` passes (8). |
| 3 | The text sheet and page agree on both platforms; ledger-copy tests cover completion, interruption, correction and unresolved outcomes. | holds | Reviewer B: `_compare` runs on both platforms for the fixture and the Your Trainer corpus; the scenario set is required on both. 18 tests pass. |
| 4 | The page exposes setup and readiness; a blocked action stays visible while independent work stays reachable. | holds | Reviewer B: `walk-page.test.mjs` "readiness holds dependent actions…" and `renderer.ts` keep the blocked card drawn. |
| 5 | Failed local or ledger writes stay visible and can be retried. | holds | Reviewer B: the two early returns in `markWalkStep` with their retry messages. |
| 6 | An edited action or expectation does not inherit a mark. | holds | Reviewer B: `stepSignature` keys the mark on the head, state, evidence prompts, timer, readiness and every expectation line. |
| 7 | Guards: the holding rule and the evidence gate each have a failing test when removed. | holds | Both reviewers broke them in the built bundle; the node suite failed (11 tests for the holding rule). |

Findings to act on, all in code this feature changed:

1. **A hold arriving after a mark does not stop the check being written** (claim 1). Fix: the settle loop skips a check while any of its citing steps is held.
2. **Only the corpus test guards the readiness gate, and it skips without Your Trainer** (both reviewers). A synthetic test that runs anywhere should fail when the gate is removed.
3. **The corpus test decides which checks are held with `walkUnready`, the function under test** (reviewer B). It should work that out from the payload itself.
4. **A step whose whole action is its screen label shows an empty action** (reviewer B). `walkVisibleAction` should keep the text when trimming would leave nothing; the mark dialog's title uses it since this feature's last commit.
5. **The corpus test's comment speaks of an `equipment` readiness**; the type has only `preparation` and `decision` (reviewer A).

Noted and left as they are: the readiness panel names the waiting steps, and the checks they affect are named under **I can't perform this** (reviewer B). `stepSignature` does not cover `requires` (reviewer B); fix 1 makes that harmless, because a held step blocks the write whether or not its old mark survives. Reviewer A saw the built bundle change during its run; that was reviewer B rebuilding, and nothing in the test path builds `dist/`.

### Round 1 fixes

All five findings are fixed in `desktop/src/renderer/renderer.ts` and `desktop/tests/walk-page.test.mjs` (868e7ef). Each new or changed test was checked by breaking its code in a copy of the built bundle; each break failed it.

1. A new `walkCheckHeld` says whether any step citing a check is held now. The settle loop in `markWalkStep` skips such a check, and so do the correction route's completed list and `walkStepNeedsLedgerRetry`. The test "a hold declared after a step was marked still holds its check" is reviewer B's reproduction.
2. "a step held by a decision records nothing, here or in the ledger" drives `markWalkStep` on a synthetic procedure. It fails when the readiness gate is removed, with or without Your Trainer present.
3. The corpus test works out the held steps from the payload's own `readiness` and `requires`. Making `walkUnready` stop holding decisions now fails it on both platforms.
4. `walkVisibleAction` keeps the label when trimming would leave nothing ("a step whose whole action is its screen label keeps the label").
5. The corpus test's comment names only the two readiness kinds the type has.

### Round 2

2026-09-25, one reviewer, clean context, 14 of 15 calls. **Verdict: approved.**

| # | Round-1 finding | Verdict | Evidence |
|---|---|---|---|
| 1 | A hold arriving after a mark does not stop the check being written | fixed | Making `walkCheckHeld` return false fails "a hold declared after a step was marked still holds its check" and nothing else; the test also asserts `walkStepNeedsLedgerRetry` is false. |
| 2 | Only the corpus test guards the readiness gate | fixed | "a step held by a decision records nothing…" runs with both corpus tests skipped, and deleting the gate fails it alone. |
| 3 | The corpus test decides held checks with the function under test | fixed by inspection | `heldStepsFromPayload` derives them from `readiness` and `requires`. The reviewer had no Your Trainer payload to run it; the author's own break of the decision hold failed it on both platforms before round 2. |
| 4 | A label-only action shows empty | fixed | Changing `return rest \|\| text` to `return rest` fails its test alone. |
| 5 | A readiness kind the type does not have | fixed | The corpus docblock names only `preparation` and `decision`. |

Both wording notes were applied: the reproduction test no longer says "needs equipment", and the corpus test's docblock says it depends on the loop confirming every `preparation` readiness. The reviewer also noted that the node tests read the built bundle, so a source edit without `npm run build` is tested against the old bundle. That is how this suite has always worked; it is recorded here, not changed.

## Superseded 2026-09-27

The walk page this describes was replaced by the release test in the Tests pane, which Edwin approved on 2026-09-27. [[FEAT-0155-The-Release-Test-Goes-Section-By-Section]] carries it on ([[TASK-0644-Retire-The-Walk-Page-In-The-Publication-View]]).
