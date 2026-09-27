---
type: "[[change]]"
id: CHG-20260927-The-Walk-Page-Is-The-Release-Test-In-The-Tests-View
title: "The walk page is gone; the release test opens from the Tests pane, one platform overview and one page per section"
status: merged
owner: user:edwin
created: 2026-09-27
updated: 2026-09-27
source: ["[[TASK-0639-Rename-The-Walk-To-The-Release-Test]]", "[[TASK-0640-The-Release-Test-Payload]]", "[[TASK-0641-The-Release-Test-In-The-Tests-Pane]]", "[[TASK-0642-The-Platform-Overview-Continue-And-Needs-You]]", "[[TASK-0643-The-Section-Page-And-Its-Results]]", "[[TASK-0644-Retire-The-Walk-Page-In-The-Publication-View]]"]
commit: ""
pr: ""
impacts: ["desktop/src/renderer/release-test.ts", "desktop/src/renderer/renderer.ts", "desktop/src/renderer/renderer.css", "src/project_os_cockpit/acceptance.py", "src/project_os_cockpit/server.py", "src/project_os_cockpit/cockpit.py", "src/project_os_cockpit/ledger.py", "src/project_os_cockpit/release_test_bundled.py"]
platforms: [macos]
issues: []
features: ["[[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TST-0092-A-Release-Test-Section-Is-Tested-From-The-Tests-Pane]]", "[[TST-0088-The-Walk-Page-Hands-Over-The-Owed-Checks]]", "[[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]]"]
---

# The walk page is the release test, in the Tests view

## Summary

Edwin now tests a release from the Tests pane: "Release test · v2.2.0" lists each platform and its sections with their progress, a platform opens an overview with Continue and Needs you, and a section opens a page shaped like the approved example. The walk page in the Publication view is removed, and its addresses open the new page.

## Impact

- [[SUR-0004]]: the walk page is replaced by the release test: a Tests-pane group, a platform overview and a page per section, where each check is one action and one expected line with Pass, Fail and More.

What changed for someone using or building on it:

- **Addresses.** `~release-test`, `~release-test/<platform>` and `~release-test/<platform>/<section>`. `~walk` and `~walk/<platform>` open them.
- **API.** `/api/cockpit/release-test` replaces `/api/cockpit/walk`. Its body is the template generator's own page data (TESTING.md rule 10) plus the open ledger's `results` and each section's `progress`; COCKPIT-API.md has the shape. The page shows what the open release owed, so a check stays after its result is recorded.
- **Results.** Kept in the browser per printed check, keyed by its tags and action. When every printed check of one test note has a result, and every result but Pass has a reason, one ledger event is written through `postCheckVerdict`, the most serious result winning.
- **Ledger key.** New entries store the result under `result`; entries under `mark` are still read.
- **Browser storage.** The walk page's five keys are moved to `release-test-*` names once, and its saved step results carried onto the checks with the same tags.
- **Names.** The bundle is `release_test_bundled.py`; `walkOneCheck` is `markOneCheck`; the three test kinds are `kind_of`, `KIND_FEATURE` and the like. A test refuses the old words in code.
- **Removed.** The walk page's 70 renderer functions, its CSS, and eight test files that tested it. TST-0088 and TST-0089 are retired in favour of TST-0092.

## Documentation Coverage (All Types Considered)

- features: updated (FEAT-0155 tasks; FEAT-0149 to FEAT-0151 are superseded after the pilot)
- requirements: not-applicable (REQ-0070 and REQ-0071 await Edwin's approval)
- tasks: updated (TASK-0639 to TASK-0644)
- issues: not-applicable
- tests: updated (TST-0088 and TST-0089 retired; TST-0092 is the check to test)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable (a route and storage keys changed; both have a redirect or a migration)
- changes: new
- snapshot: updated

## Follow-ups

- [ ] TASK-0645, the pilot: Edwin compares the Equipment section with the approved example.
- [ ] TASK-0642: the pane's top "Needs you" row does not count results that live in the browser.
- [ ] TASK-0643: a capture takes a note, not a picture.
