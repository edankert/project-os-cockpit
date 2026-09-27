---
type: "[[task]]"
id: TASK-0644
title: "Retire the walk page from the Publication view, point the release page at the Tests pane, and supersede the notes the release test replaces"
status: doing
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-27
updated: 2026-09-27
source: ["Edwin, 2026-09-27: the Tests pane entry replaces the ~walk page in the Publication view"]
parent: "[[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]"
effort: "M"
due: ""
depends: ["[[TASK-0641-The-Release-Test-In-The-Tests-Pane]]", "[[TASK-0642-The-Platform-Overview-Continue-And-Needs-You]]", "[[TASK-0645-Pilot-The-Equipment-Section-Then-The-Rest]]"]
blocks: []
related: ["[[FEAT-0149-The-Walk-Page]]", "[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]", "[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]", "[[TST-0088-The-Walk-Page-Hands-Over-The-Owed-Checks]]", "[[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]]", "[[SUR-0004-The-Release-Walk]]"]
tests: []
---

# Retire the walk page in the Publication view

## Definition of Done

- [x] The Publication view no longer draws a walk page. `publication: ['~release', '~walk']` in the renderer's owned pages loses `~walk`. `publication: ['~release']`.
- [x] Any `~walk` or `~walk/<platform>` address opens the release test overview in the Tests pane for that platform (the redirect from TASK-0639), and a renderer test proves it. Redirect in `navigateToInner`; `rtAddressFor` tested.
- [x] The release page's gate section, the checks page header and the obligation link that said "Walk them" link to the Tests pane entry instead. "Open the release test", "test them", "Test them", all to `~release-test/<platform>`.
- [x] The step-card code the old page used, and its tests, are removed, not left unreachable. Removed with its tests (`walk-page.test.mjs`, seven Python files).
- [x] [[TST-0088-The-Walk-Page-Hands-Over-The-Owed-Checks]] and [[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]] are `retired`, each naming [[TST-0092-A-Release-Test-Section-Is-Tested-From-The-Tests-Pane]] as the check that replaces it. Both `retired`, each naming TST-0092.
- [ ] [[FEAT-0149-The-Walk-Page]], [[FEAT-0150-The-Walk-Page-Reads-As-A-Script]] and [[FEAT-0151-The-Release-Walk-Has-One-Next-Action]] are `superseded` with `superseded_by: [[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]`. [[REQ-0066-The-Release-Walk-Keeps-Observation-Context]] and [[REQ-0068-The-Walk-Records-One-Clear-Observation-At-A-Time]] are `superseded` by REQ-0070 and REQ-0071. REQ-0067 and REQ-0069 stay `implemented`.
- [x] SUR-0004 describes the release test as it now is. Title and body rewritten.
- [x] A change note records the removal and the new address. [[CHG-20260927-The-Walk-Page-Is-The-Release-Test-In-The-Tests-View]].

## Notes

This task runs after the pilot, so the old page stays usable until the new one has been compared with the example on a real section.

## Progress, 2026-09-27

Done early, with TASK-0639: removing the route left the old page unreachable, and the dead-code test refuses unreachable functions, so the page could not stay usable until the pilot as planned. **Open: marking FEAT-0149, FEAT-0150 and FEAT-0151 `superseded`, and REQ-0066 and REQ-0068 superseded by REQ-0070 and REQ-0071.** Those two requirements are still drafts that Edwin has not approved, and this task's own note says the supersession follows the pilot.
