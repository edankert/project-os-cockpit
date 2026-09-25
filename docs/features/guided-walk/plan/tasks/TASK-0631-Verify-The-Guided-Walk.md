---
type: "[[task]]"
id: TASK-0631
title: "Verify the guided release walk against the text sheet and ledger"
status: doing
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-16
updated: 2026-09-25
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
- [x] A browser walk shows the next action, setup transition, exception, pause and evidence comparison without opening a check note.

## Steps

- [x] Expand agreement and write-path fixtures.
- [x] Walk the page in a real browser against a fixture workspace.
- [x] Record remaining human and hardware exceptions in the feature note.

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

## Handoff, 2026-09-23

This task remains `doing`; its outstanding guided-walk checks are unchanged. Edwin requested a review of Codex integration and next steps toward Claude Code parity. The findings are recorded in [the Codex parity review](../../../../reference/codex-parity-review-2026-09-23.md). The review ran focused agent-integration checks and changed no walk code or ledger. Resume this task from the progress and open checks above; the Codex review does not provide new guided-walk verification.

## Plan, 2026-09-25

Your Trainer TASK-0960 is done, so this task resumes. Its procedure audits (A3, A5, A6, A8) were the reason D2 and D3 waited.

D2 still owes one clause: unchanged procedures produce the same verdicts as the previous flow. So far only selected FREE ride steps have been compared. The next test walks every sitting on both platforms, every step, through the built renderer's own step control. It confirms preparation readiness and saves a note and build wherever a step asks for evidence, as a walker would. It then compares the ledger requests with a direct Pass on each check, and applies both to copies of the working ledgers. A check held by a declared decision or missing equipment must get no verdict from the steps and must stay owed.

D3 is an audit of boundaries rather than new behaviour. It is checked by running `walk-sheet.py --check` on Your Trainer for both platforms, and by reading the walk code for prose inference, a stored per-release worklist, a new ledger field, a time estimate or a bulk pass.

## Result, 2026-09-25

**D2 and D3 are met, and this task is done.** Your Trainer TASK-0960 finished its procedure audits on 2026-09-24. Every owed check on both platforms now sits in a procedure: 86 of 86 on Android and 333 of 333 on iOS, with no procedure problem reported.

**D2, unchanged procedures.** A new test walks every sitting on both platforms through the built renderer's own step control: 13 sittings and 351 steps on Android, 14 sittings and 872 steps on iOS. It confirms each `preparation` readiness and saves a note and build at each evidence prompt first, as a walker would. It then compares the requests with a direct Pass on each check. They are identical for every check the steps can record: 84 on Android and 282 on iOS. The other 2 Android and 51 iOS checks sit behind a declared decision or missing equipment. Their steps wrote nothing, and they stay owed. Both request sets were applied to a copy of each working ledger, and the owed set left over is exactly those held checks. Two deliberate breaks in the built renderer each failed the test: removing the readiness gate, and writing a check before all its citing steps had a mark. The test is `test_every_real_sitting_walked_by_steps_matches_direct_check_verdicts` in `tests/test_guided_walk_ledger_copy.py`, with its node half in `desktop/tests/walk-page.test.mjs`.

**D3, existing boundaries.** `walk-sheet.py --check` exits 0 for both platforms on Your Trainer, using this repository's generator and Your Trainer's own, which are byte-identical. It prints 528 remarks about old change notes with no `## Impact` list, and no problems. The ledger module has not changed since FEAT-0151 began, and its `evidence` field dates from 2026-08-19. Every verdict the walk writes goes through `postCheckVerdict`, one check at a time. A step writes only the checks whose citing steps all have a mark. Nothing in the walk estimates a duration. The payload builder reads declared frontmatter such as `after:`, and does not infer an order from prose.

**Browser walk.** The walk page ran in a separate headless Chrome against a copy of Your Trainer's current docs, git tags and ledgers, through a sidecar started for the purpose. Edwin's app was not touched. On Android it showed the 14-screen survey first, then step 1 with its required state and **Pass and next**. After one pass the setup folded and the page moved to step 2. A reload resumed at the saved step and named the app state to restore. At sitting 2, step 18, the page showed "Needs a decision" with the authored reason and disabled Pass. **I can't perform this** offered TST-0652 and recorded nothing. A note and build saved at sitting 3's step 32 appeared at step 46 with platform, release, build, state and time. **Something wrong…** offered only Partial, Fail and Question, and a Fail wrote one event in the existing format to the copy's ledger. The page stayed on the step and read "2 of 7 done · 1 needs attention". The iOS page said there is no earlier iOS release to compare against, and used iOS wording in its setup and actions. Your Trainer's own ledgers were not written.

The walk found two display defects, both fixed here ([[CHG-20260925-Walk-Setup-Reads-As-A-List]]). The full suite then found two more, also fixed in that change: FEAT-0151's own lines printed a stored mark raw ("na"), and six surface notes had earned this repository a Surfaces group in Library. The setup printed its Markdown list as text, so 12 of 13 Android sittings showed items starting with "- ". The mark dialog's title repeated the screen label the card already leaves off.

It also found one thing left as it is. 176 quoted expectations (76 Android, 100 iOS) show their `**` bold markers on the card. The review of 2026-09-14 decided the card shows the generator's quote exactly as validated, and a test says so. Changing that is Edwin's call.

**Human and hardware exceptions.** Edwin's own walk of the checks is Your Trainer D4 (TASK-0923). The 53 held checks need a product decision, dual-sided pedals, a real cadence sensor or iOS parity work before anyone can walk them, as Your Trainer's procedures declare. None of them is this page's to resolve.

## Reopened, 2026-09-25: review fixes

FEAT-0151's round-1 review returned changes-requested. The five findings listed in the feature's `## Review` section are fixed under this task, because they are about the verification and the code it checked. The task closes again when they are fixed and round 2 has verified them.

## Handoff, 2026-09-25, round 2 running

**Done.** All five round-1 findings are fixed and committed (868e7ef, notes in de76ae3 and 321a027). The desktop suite passes 241 of 243 with 2 corpus skips, and the Python suite 2,199 with 6 skipped.

**Next.** One round-2 reviewer is verifying the fixes from `review-packet.py FEAT-0151 --round 2 --since 0a2fcab`. If it answers *fixed* for the refuted claim: set this task `done`, write `review_round: 2` and its verdict on FEAT-0151, set FEAT-0151 `done` and REQ-0066 to REQ-0069 `implemented`, close PHASE-043 if nothing under it is open, and return focus to TASK-0633. If it answers *not fixed*, there is no round 3: the disagreement is adjudicated (QUALITY.md).

**Set aside.** Showing quoted expectations without their `**` markers waits for Edwin (see FEAT-0151's handoff).

