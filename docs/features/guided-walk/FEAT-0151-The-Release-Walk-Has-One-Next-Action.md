---
type: "[[feature]]"
id: FEAT-0151
aliases: ["FEAT-0151"]
title: "The release walk has one clear next action"
status: doing
phase: ""
owner: user:edwin
created: 2026-09-16
updated: 2026-09-17
source: ["Your Trainer FEAT-0122, 2026-09-16: implement and test the guided release walk fully"]
goal: "A person can perform, record and resume each owed release observation from one focused page with its necessary preparation."
requirements: ["[[REQ-0066-The-Release-Walk-Keeps-Observation-Context]]"]
tasks: ["[[TASK-0629-Show-One-Walk-Action-And-Its-Readiness]]", "[[TASK-0630-Record-And-Resume-Walk-Observations]]", "[[TASK-0631-Verify-The-Guided-Walk]]"]
release: ""
acceptance_exception: ""
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

The detailed product scenarios and acceptance criteria are in Your Trainer FEAT-0122. This feature owns the cockpit implementation of those criteria for any project-os workspace.

## Acceptance

- [ ] A fresh walk begins with the changed-screen review, and Continue returns to the saved screen or step for the same workspace, release and platform.
- [ ] The current step shows its screen, authored action, exact owed expectations, required state and one primary Pass and next control. A preparation action has Continue and produces no verdict.
- [ ] The page exposes relevant setup and readiness before execution. A blocked action remains visible with its affected checks, while independent work stays reachable.
- [ ] Fail, Partial, Question and inability to perform are available with their required reasons and do not bulk-clear checks. Failed local or ledger writes stay visible and can be retried.
- [ ] Saved observations, corrections and attachments survive a same-workspace restart. Edited actions or expectations do not silently inherit a mark; another release or platform does not inherit position or evidence.
- [ ] A later comparison can open evidence captured earlier with its platform and source state. A user-started timer assists an authored wait and never marks a result.
- [ ] The text sheet and page agree on both platforms, including the survey hierarchy, preparation, setup and owed set. Ledger-copy tests cover completion, interruption, correction and unresolved outcomes.

## Links

- Requirement: [[REQ-0066-The-Release-Walk-Keeps-Observation-Context]].
- Tasks: [[TASK-0629-Show-One-Walk-Action-And-Its-Readiness]], [[TASK-0630-Record-And-Resume-Walk-Observations]], [[TASK-0631-Verify-The-Guided-Walk]].

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
