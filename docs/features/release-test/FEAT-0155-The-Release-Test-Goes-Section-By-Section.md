---
type: "[[feature]]"
id: FEAT-0155
aliases: ["FEAT-0155"]
title: "The release test is opened from the Tests pane and read one section at a time, with a platform overview that says where to continue and what needs you"
status: done
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-27
updated: 2026-09-27
source: ["Edwin, 2026-09-27: 'We have a problem with the amount of text the walk procedure has. It is just a wall of text, there are no clear paragraphs or headings and all together it is just way too much. [...] This is now a lot worse (more difficult to parse), engage with. Than the original feature tests page ... Review and suggest how to make this more human friendly. More concise and better formatting to start with!!'", "Edwin, 2026-09-27: 'At first I want to see concise information about what has changed for the section we plan to test (including the before/after screen-shots), then I want to see the setup for the section (but this can be hidden away behind a open/close option) and then I would like to see the actual checks as concise and complete as possible.'", "Edwin, 2026-09-27: 'on the checks, I need to be able to record not just pass and fail, so please add back the other options as well (but I really like the background changing and the overall look and feel of the page, this works for me!)'", "Edwin, 2026-09-27: 'I have said this before I don't like calling this a walk, can we think about what this is and how we present this / how to open this in the cockpit?'", "Edwin, 2026-09-27: 'Can we have that in the left pane under the acceptance tests section, that would make it easier to browse and see the actual overview?'", "Edwin, 2026-09-27, approving the example page (copied beside this note, __attachments__/release-test-example/index.html): 'That works for me. How do we create this?'", "Edwin, 2026-09-27, decisions D2 (1: the short expected text lives in the test notes) and D1 (2: rename internal names too), and D3: '1. do as recommended. 2. rename all in one go. (to avoid confusion later on) ... if this cannot be fully automated, I have no problem if we would use an LLM agent / skill to hand edit some of this info when going to a release?'", "Edwin, 2026-09-27, choosing the recommended answers: rename the old meaning of section to test kinds; rename the ledger key mark to result"]
goal: "A person testing a release opens it from the Tests pane, sees per platform how far they are and what needs them, and works through one short section page at a time: what changed, setup folded away, then numbered checks, each one action with the expected line of each part it cites, and a one-tap result."
requirements: ["[[REQ-0070-The-Release-Test-Is-An-Overview-And-One-Page-Per-Section]]", "[[REQ-0071-A-Result-Is-Recorded-On-The-Check-Where-It-Was-Seen]]", "[[REQ-0072-The-Walk-Is-Called-The-Release-Test-Everywhere]]"]
tasks: ["[[TASK-0639]]", "[[TASK-0640]]", "[[TASK-0641]]", "[[TASK-0642]]", "[[TASK-0643]]", "[[TASK-0644]]", "[[TASK-0645]]"]
release: ""
acceptance_exception: ""
acceptance: ""
design: ""
reviewed_by: "model:claude-opus-5-5 (two reviewers, fresh contexts)"
review_date: 2026-09-27
review_verdict: "approved"
review_round: "2"
related: ["[[FEAT-0149-The-Walk-Page]]", "[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]", "[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]", "[[SUR-0004-The-Release-Walk]]", "[[SUR-0001-The-Tests-View]]", "[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]", "[[ISS-0263-A-Write-Evicts-The-Reader-From-The-Checks-Page]]", "[[ISS-0309-A-Procedure-Quote-Is-Unchecked-Where-The-Check-States-No-Expect]]", "[[RISK-0010-Saved-Walk-Observations-Can-Outlive-Their-Source]]", "[[RISK-0011-Renaming-The-Walk-Drops-Links-And-Saved-Progress]]"]
---

# The release test goes section by section

## Goal

The page for testing a release by hand moves from the Publication view into the Tests pane and is split into short pages. Edwin approved the new layout on 2026-09-27 from an example page (*"That works for me. How do we create this?"*), which is copied beside this note at `__attachments__/release-test-example/index.html` and is the specification. Read the whole file, including its script.

The page the tooling calls the "walk" today is too long to work from. On Your Trainer's Android v2.2.0 release, 86 owed checks became 353 steps and 37,254 words on one page. The same starting-state paragraph was repeated above most steps, and the list of changed screens came before the first step.

## The shared finish line

Edwin set one goal for this feature, project-os-dev FEAT-0040, project-os-cockpit FEAT-0155 and your-trainer FEAT-0129 on 2026-09-27: **Edwin can test v2.2.0 on Android and iOS from the cockpit's Tests pane, every section opens in the approved layout, and one `release-test-prep` request prepared all of them.** your-trainer FEAT-0129, "The shared finish line for all three features", states the seven conditions and the nine stages. The three features finish together.

## Vocabulary

Edwin renamed the terms on 2026-09-27 (decision D1): *"I have said this before I don't like calling this a walk"*, and *"rename all in one go. (to avoid confusion later on)"*. The new words are used here and in every note, label, route and code name this feature touches:

| Old word | New word | What it is |
| --- | --- | --- |
| walk | release test | testing one release on one platform by hand |
| sitting | section | a group of checks done with the same things on the bench |
| survey | what changed | the screens this release changed, shown before the checks |
| mark or verdict, as shown to a person | result | Pass, Fail, Partial, Question, Blocked, N/A or Excused |
| check | check (unchanged) | one numbered line: an action and what you should see |

The values stored in the release ledger do not change (`pass`, `fail`, `partial`, `question`, `blocked`, `na`, `excused`). Closed ADRs, change notes and archived notes are history and keep the old words.

## Scope

**The Tests pane.** The Tests pane has a new group, "Release test · <version>", placed right after "Needs you" and above "Feature tests" and "Regression tests". Under it is one row per platform with its progress. Under each platform are its sections, each with a status dot and a count such as 11/28. The dot is empty before any result, half filled when part done, filled when done, and red when the section holds a Fail, Question or Blocked result. This entry replaces the `~walk/<platform>` page in the Publication view.

**The platform overview** opens by default when a platform row is chosen. It shows:

- a progress bar coloured by result, with a count per result;
- a "Continue where you stopped" button that names the next check with no result and jumps to it;
- "Needs you": every Fail, Question, Blocked and Partial result with its reason, plus declared decisions and readiness problems, each jumping to its check;
- the section list, each with its progress and one line saying what it needs on the bench.

**The section page** has three parts, in this order:

1. What changed since the previous release, for this platform only. Changes are grouped by screen, one line per change. Before and after screenshots enlarge on click. A warning appears when a screenshot is older than the latest change to its screen.
2. Setup, folded by default, in three parts: "On the bench", "Before you start" and "Later" (things needed by one check only).
3. The checks, in groups. Each group has a heading and, where it needs one, a "Start:" line saying the state to begin from, written once. Each check is a number, one action line, the expected line of each check part it cites after an arrow, and small test tags such as `TST-0657.1`.

**Results.** Pass and Fail are one tap each. Partial, Question, Blocked, N/A and Excused sit under "More", each with a one-line meaning. Every result except Pass opens a reason box. The result shows on the page at once, and it is written to the ledger only when its reason is filled in. The row background takes the result's colour. A check that cannot be done yet is greyed, with one line saying why and which result is suggested. Results reach the release ledger through the existing write path (`postCheckVerdict`), one ledger event per test note under the existing combination rule. Marking a check updates the pane, the overview, the Continue button and Needs you at once, and never moves the reader to another page ([[ISS-0263-A-Write-Evicts-The-Reader-From-The-Checks-Page]]).

**The rename (D1)** in this repository: the `~walk` route, `/api/cockpit/walk`, `acceptance.walk_payload`, the bundled generator `walk_sheet_bundled.py`, labels, CSS classes, browser storage keys, tests, and the live notes' wording. The old `~walk/<platform>` address keeps working by opening the new overview, because release notes in other repositories link to it.

**Out of scope.**

- The generator that works out sections, groups, "Start:" lines, bench lists, what changed and readiness. It lives in project-os-dev and is bundled here byte for byte: project-os-dev FEAT-0040 and ADR-0050, the release test generator, the vocabulary decision and the release-prep skill.
- Rewriting Your Trainer's procedures and test notes, including shortening the `## Expect` lines (D2): your-trainer FEAT-0129, the rewrite of the procedures and test notes with the Equipment section pilot.
- The ledger format and its stored values.
- Time estimates of any kind.

## Rollout

1. Pilot one section end to end: Your Trainer, Android, the Equipment Hub section. Compare it with the example page side by side.
2. Then the other Android sections.
3. Then iOS.

Complexity, judged by how much existing behaviour it touches: High overall, because it replaces a page, renames a route, an API and storage keys, and retires two acceptance checks. The pilot alone is Medium.

## What this replaces

This feature replaces the step-by-step page built by [[FEAT-0149-The-Walk-Page]], [[FEAT-0150-The-Walk-Page-Reads-As-A-Script]] and [[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]. Those features stay `done` until this one lands; [[TASK-0644-Retire-The-Walk-Page-In-The-Publication-View]] then marks them `superseded`.

- [[REQ-0066-The-Release-Walk-Keeps-Observation-Context]] and [[REQ-0068-The-Walk-Records-One-Clear-Observation-At-A-Time]] ask for one current action at a time. The section page shows all of a section's checks at once, so both are superseded by [[REQ-0070-The-Release-Test-Is-An-Overview-And-One-Page-Per-Section]] and [[REQ-0071-A-Result-Is-Recorded-On-The-Check-Where-It-Was-Seen]] when this feature lands.
- [[REQ-0067-The-Walk-Keeps-Required-Actions-And-Only-Relevant-Setup]] still holds: only relevant setup is shown, and no owed check is dropped. Preparation now appears as a group's "Start:" line or in Setup, not as a step card.
- [[REQ-0069-The-Walk-Resumes-With-Valid-Evidence]] still holds: saved results survive a restart, and changed checks do not inherit old results. Assumption: a check that asks for a screenshot or note at the moment of observation keeps that control on its row. The example page does not show one.
- [[ISS-0309-A-Procedure-Quote-Is-Unchecked-Where-The-Check-States-No-Expect]] loses its cause for rewritten checks: the page prints the check's own words instead of a procedure's quote of them (D2).

## Questions Edwin answered on 2026-09-27

- **"Section" gets one meaning.** [[ADR-0039-Three-Sections-Derived-Not-Filed]] called "Feature tests", "Regression tests" and "Automated tests" sections, and the code says `section_of`, `SECTION_FEATURE` and `MANUAL_SECTIONS`. Edwin chose to rename that old meaning in the same rename: those three are "test kinds" (`kind_of`, `KIND_FEATURE`, `MANUAL_KINDS` and the like). "Section" then means only a release test section, and the code names it `section`, not `release_section`. project-os-dev ADR-0050 records the decision.
- **The ledger's stored key becomes `result`.** New entries write `result`, and every reader in the cockpit keeps accepting `mark`.

## Impact analysis and risk scan, 2026-09-27

Checked against FEAT-0149, FEAT-0150, FEAT-0151, REQ-0066 to REQ-0069, ADR-0035, ADR-0037, ADR-0039, ADR-0041, ISS-0263, ISS-0285, ISS-0286, ISS-0307, ISS-0309, RISK-0010, SUR-0001, SUR-0004, and the proposed designs DES-0015 and DES-0016. The conflicts are the ones listed under "What this replaces" and the "section" question Edwin answered above. ADR-0041 is not in conflict: the three results that settle scope (N/A, Excused, Blocked) were already offered where the procedure is read. DES-0015 and DES-0016 are proposed and change nothing the Tests pane entry needs.

Risk scan: the route, API path, bundled file name and browser storage keys change, which is [[RISK-0011-Renaming-The-Walk-Drops-Links-And-Saved-Progress]]. No other trigger applies: no new dependency, environment variable, long-running step, or credential or licence exposure.

## Acceptance

- [x] The Tests pane shows "Release test · <version>" right after "Needs you" and above "Feature tests" and "Regression tests", one row per platform with its progress, and under each platform its sections with a status dot and a done/total count. — TST-0092 step 1. *Corrected on review, 2026-09-27: this said "under Acceptance tests", a heading the pane has never had.*
- [x] Choosing a platform opens its overview: a bar coloured by result with a count per result, a Continue button naming the next check with no result, Needs you, and the section list with one bench line each. — TST-0092 step 2 ([[TASK-0642-The-Platform-Overview-Continue-And-Needs-You]]).
- [x] Continue opens the section holding the next check with no result and scrolls that check into view. — TST-0092 step 3 (`rtContinue`, `rtFocusCheck`).
- [x] Needs you lists every Fail, Question, Blocked and Partial result with its reason, and every declared decision and readiness problem. Each entry opens its check. — TST-0092 steps 6 and 7. The row of the platform whose page was opened in this session also carries the count (`rtSetNavNeeds`); another platform's row has none until its page is opened.
- [x] A section page shows, in order: what changed for this platform grouped by screen, with screenshots that enlarge on click and a warning on a stale capture; Setup folded by default in three parts; then the checks in groups, each with a heading and at most one "Start:" line. — TST-0092 step 4 ([[TASK-0643-The-Section-Page-And-Its-Results]]).
- [x] Each check shows a number, one action line, the expected line of each check part it cites after an arrow, and its tags. It shows nothing else unless it is greyed with a reason, or its procedure declares a timer, a capture, a comparison or a start state for it. — TST-0092 step 4; `rtBuildCheck`. *Corrected on review, 2026-09-27: this said "one expected line". A procedure step may cite several parts of one check, and the approved example has a timer; on REL-0017, 17 Android checks cite more than one part.*
- [x] Pass and Fail take one tap. The other five results are under More with their one-line meanings. A result shows at once on the page, and every result except Pass is written to the ledger only when its reason is filled in; until then its box is outlined in the Fail colour. — TST-0092 steps 5 and 8; `rtNoteResults`. *Corrected on review, 2026-09-27: this said "before it is saved"; what waits for the reason is the ledger write.*
- [x] A result reaches the release ledger through `postCheckVerdict`. On a ledger copy, results on every check of a test note write the same events as marking that test note directly. — TST-0092 step 8 on a scratch ledger; `release-test.test.mjs` (`rtWorst`).
- [x] After a result, the pane dot and count, the overview bar, Continue and Needs you all change without a reload, and the reader stays on the section page at the same scroll position. — TST-0092 step 6. `release-test.test.mjs` tests `rtRedraw`, and checks in the built code that `rtRecord` calls it and `renderWsNav` calls `rtReapplyPane`.
- [x] No route, API path, payload function, bundled file name, label, CSS class or storage key in `src/` or `desktop/src/` contains "walk", "sitting" or "survey" in the old sense. Saved results under the old storage keys are carried over, not lost. — `tests/test_release_test_names.py` ([[TASK-0639-Rename-The-Walk-To-The-Release-Test]]); the storage move is tested in `release-test.test.mjs`.
- [x] Opening `~walk/<platform>` shows the new overview for that platform. The Publication view no longer has a walk page, and the release page's link points at the Tests pane entry. — TST-0092 step 9; TASK-0644.
- [x] The Your Trainer Android Equipment Hub section, rendered by the cockpit, matches the example page section for section; the differences are listed in [[TASK-0645-Pilot-The-Equipment-Section-Then-The-Rest]]. — [[TASK-0645-Pilot-The-Equipment-Section-Then-The-Rest]]; Edwin compared it in the desktop app and said the overall setup is really good.

## Verification

Full run, 2026-09-27: `.venv/bin/python -m pytest -q` passed 2,136 tests with 11 skipped; the 15 desktop test files under `desktop/tests/` pass one by one with `node --test`, including `release-test.test.mjs` (17 tests).

[[TST-0092-A-Release-Test-Section-Is-Tested-From-The-Tests-Pane]] was tested end to end on 2026-09-27, by an agent in the live harness on a scratch copy of your-trainer, and its result is in the macOS ledger. Edwin used the same pages in the desktop app that day: *"It looks great, I think we can now fully close out the cockpit phase-0010 and the release test functionality."*

## Links

- Requirements: [[REQ-0070-The-Release-Test-Is-An-Overview-And-One-Page-Per-Section]], [[REQ-0071-A-Result-Is-Recorded-On-The-Check-Where-It-Was-Seen]], [[REQ-0072-The-Walk-Is-Called-The-Release-Test-Everywhere]].
- Tasks: [[TASK-0639-Rename-The-Walk-To-The-Release-Test]], [[TASK-0640-The-Release-Test-Payload]], [[TASK-0641-The-Release-Test-In-The-Tests-Pane]], [[TASK-0642-The-Platform-Overview-Continue-And-Needs-You]], [[TASK-0643-The-Section-Page-And-Its-Results]], [[TASK-0644-Retire-The-Walk-Page-In-The-Publication-View]], [[TASK-0645-Pilot-The-Equipment-Section-Then-The-Rest]].
- Acceptance check: [[TST-0092-A-Release-Test-Section-Is-Tested-From-The-Tests-Pane]].
- Specification: `__attachments__/release-test-example/index.html` (the approved example, with its screenshots in `img/`).
- Other repositories: project-os-dev FEAT-0040 and ADR-0050, the release test generator, the vocabulary decision and the release-prep skill. your-trainer FEAT-0129, the rewrite of the procedures and test notes with the Equipment section pilot.

## Review

Round 1, 2026-09-27. Two independent reviewers (model:claude-opus-5-5, fresh contexts) reviewed the packet for ef1e21f..3f46b4a. Combined verdict: **changes-requested**.

| Claim | Combined | What was done |
|---|---|---|
| 1. The pane shows the release test "under Acceptance tests" | refuted as worded | The pane has no such heading, and the group sits after Needs you. The criterion and the Scope now say where it is. |
| 2, 3, 4, 8 | holds | — |
| 5. Section page order | holds; the stale warning and enlarge were not checked | — |
| 6. "One expected line" per check | refuted | A step citing several parts of one check prints each part's line, as TESTING.md rule 9 says, and the approved example has a timer. The criterion now says so. |
| 7. A reason "before it is saved" | partly refuted | The result shows at once; the ledger write waits for the reason. The criterion now says so. |
| 9. The pane updates and the scroll is kept after a result | refuted as tested | `rtRedraw` now holds these steps, and a test fails if either is removed. A server rebuild of the pane dropped the browser's counts; `renderWsNav` now calls `rtReapplyPane`. |
| 10. No name says walk; saved results carry over | partly refuted | A new key, `release-test-walk-steps`, named the walk, three moved keys had no reader, `walk-ready` was missed, and the moved place never matched. Now: step results are carried from the old key itself; focus, completed, place and ready are removed; the typed evidence is left where it is, because this page has nothing to show it against. The name test's allowlist is narrowed to the exact lines. |
| 11. `~walk` opens the new overview | holds, not guarded | The route is decided by `rtRoute`, which the renderer calls for every release test address, and a test covers the redirect. |
| 12. Equipment section matches the example | not checked | Edwin's comparison, 2026-09-27. |
| A1. The row's count equals Needs you | partly refuted | A test now fails if the wiring is removed. The count shows for the platform whose page was opened in this session; the other platform's row has no count until its page is opened, because the browser holds its results but not its page. |
| A2. A picture is filed under the first test note | holds | The refusal of an unexpected path happens after the server wrote the file, so it could leave a stray PNG; the server always returns the safe path, so this is defence only. |

Observations kept as they are, with the reason:

- A test note is written to the ledger only when every printed check citing it has a result in this browser, so a check showing only a ledger result must be marked again here before the note is rewritten. That is deliberate: a new result for a note comes from its checks on this release.
- Clearing a local result shows the ledger's recorded result for that check again, which is the true state.
- The pane label uses one version for every platform when a platform falls back to another's open release (TASK-0640, tested).
- Continue said "Start" when nothing was marked in this browser but the ledger already held results; it now says "Continue where you stopped" then.
- `rtAttachPicture` checks the file name; the server checks the PNG itself.
- The two reviewers removed guards in the same working tree at the same time, and each saw the other's change. The independent-review skill should tell a reviewer to break guards in its own copy (reported to project-os-dev as an observation, not filed).

Round 2, 2026-09-27. Two reviewers, each breaking guards in their own worktree. Both returned **changes-requested**, for these items only. Every code fix held.

- The Scope, the goal and two criteria still carried round one's refuted wording, or claimed the count on every platform row. All are corrected.
- Removing the call from `rtRecord` to `rtRedraw`, the call from `renderWsNav` to `rtReapplyPane`, or the renderer's `route.moved` branch broke no test. `release-test.test.mjs` now reads each of these three functions from the built code and fails if the call is gone.
- The comment above `rtAdoptSavedState` still said "rename"; it now says the old view state is removed.

Round 2 completed, 2026-09-27. A third reviewer checked the round-two list against 9e7f663, breaking each call in its own worktree: each guard fails when its call is removed, and the wording is corrected. Verdict: **approved**. No separate packet was written for this completion pass; its scope was the round-two list above.
