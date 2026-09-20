---
type: "[[task]]"
id: TASK-0631
title: "Verify the guided release walk against the text sheet and ledger"
status: doing
phase: ""
owner: user:edwin
created: 2026-09-16
updated: 2026-09-17
source: ["Your Trainer FEAT-0122, 2026-09-16"]
parent: "[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"
effort: "Medium"
depends: ["[[TASK-0630-Record-And-Resume-Walk-Observations]]"]
blocks: []
related: ["[[SUR-0004-The-Release-Walk]]"]
tests: []
---

# Verify the guided release walk against the text sheet and ledger

## Definition of Done

- [x] Android and iOS payloads match the generated text sheet on survey, session order, setup, preparation, observations and owed checks.
- [x] Ledger-copy tests cover pass, partial, fail, question, correction and a check interrupted between observations.
- [ ] A browser walk shows the next action, setup transition, exception, pause and evidence comparison without opening a check note.

## Steps

- [x] Expand agreement and write-path fixtures.
- [ ] Walk the page in a real browser against a fixture workspace.
- [ ] Record remaining human and hardware exceptions in the feature note.

## Progress, 2026-09-17

The current Android and iOS payloads match the generated sheet's survey, session order, setup, preparation, step actions, required state and owed set in the six-case agreement suite. The built renderer produces requests for pass, partial, fail, question, correction and a check interrupted between two observations. The Python integration test applies those exact requests to separate copies of the Android and iOS ledgers and checks the resulting mark, owed state and event history. The interruption writes no event after the first observation. Four ledger-copy cases pass, and the source ledgers remain byte-identical. The browser and Edwin walk remain open until they have direct evidence.

A disposable Chrome session rendered the current Your Trainer Android payload with the actual walk card. It displayed the required state and evidence prompt on a preparation step. A later comparison showed the saved synthetic note, build, state, platform, release and source step. Pass was disabled while the second observation was missing and enabled once it was saved. A step with an unresolved product decision showed the reason, disabled Pass and offered the affected check under **I can't perform this**; opening that choice wrote no verdict. This narrows the browser gap but does not close it: the standalone harness stubbed server writes and did not exercise the full cockpit, setup transition or pause route.

An isolated Electron app now uses a disposable copy of Your Trainer's docs, git release tags and Android/iOS ledgers. The actual Android route showed the eight-screen survey, a current action, a collapsed later setup, a disabled Pass on an unavailable in-ride switch, an interrupted one-minute timer, restored local progress after reload, and a synthetic PNG uploaded through the sidecar and displayed at the later comparison. The app's step picker jumped without a verdict. Source ledgers were untouched. Review results initially hid ten expired REL-0016 excuses; it now lists all 39 owed Android checks. The iOS route loads 327 owed rows, but there is no open iOS release id in the current Your Trainer repository. Edwin's human walk, full iOS release context and unchanged real-procedure verdict equivalence remain open. [[CHG-20260917-Show-expired-excuses-in-the-release-walk-review]] records the summary correction.

After those renderer changes, the full desktop test suite passed. All 47 focused Python walk payload, route, sheet agreement and copied-ledger tests passed with loopback access. The docs-first gate, documentation validator and `git diff --check` passed. The isolated browser's copied Android and iOS working ledgers still match the source ledgers byte for byte; its synthetic two-pixel PNG was written only under the disposable workspace.

The iOS browser survey initially compared against Android REL-0001/v1.1.0 and showed Android Developer Options text and capture. Your Trainer now marks REL-0001 as Android. The live generator and isolated Electron page return zero iOS survey cards, explain that no previous iOS release can be compared, and keep 327 owed checks accessible. The focused renderer suite passes 80 cases. The platform still has no open iOS release id, so release-specific resume and the human walk remain open.

The real-procedure equivalence test now reads Your Trainer's current FREE ride sitting on both platforms and compares the built renderer's step requests with direct check requests. Both request sets agree and clear the selected checks on separate copies of the working ledgers; the source ledgers are unchanged. Android preparation steps write nothing. The iOS selection now includes TST-0370's two steps: the first does not settle the check, the timed second refuses a mark without its requested evidence, and a saved note and build permit the same final pass request as the direct check path. The broader unchanged-procedure audit and Edwin's walk remain open.

The fallback renderer now holds a declared iOS decision card behind **I can't perform this**. A focused test proves the Pass control is absent, a forged Pass result writes no verdict, and an explicit Not applicable decision uses the iOS platform. A preparation card requires its ready confirmation. The live iOS payload carries eight Settings and backup decision reasons while retaining its 327 owed checks. The 82 passing focused renderer cases and ten generator agreement and bundle cases support this path; the full human walk remains open. [[CHG-20260917-Show-readiness-on-unscripted-walk-cards]] records the correction.

## Handoff, 2026-09-20

**This task did not move today and its state is exactly as the 2026-09-17 progress above describes it.** The browser walk of the full cockpit, the iOS release context and Edwin's own walk are still the three open items.

The session that wrote this line worked on something else: Edwin asked for the cockpit to be re-cut by level of abstraction, and the answer is [[DES-0016-Levels-Of-Abstraction]], proposed under [[PHASE-045-The-Cockpit-In-Layers]] with five new decisions for him (D6 to D10) and nothing built. It touched no walk code and no ledger. The focus stays here because this task is still the work in flight.
