---
type: "[[task]]"
id: TASK-0642
title: "The platform overview: a bar coloured by result with a count per result, Continue where you stopped, Needs you, and the section list with bench lines"
status: backlog
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-27
updated: 2026-09-27
source: ["Edwin, 2026-09-27: approved example page"]
parent: "[[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]"
effort: "M"
due: ""
depends: ["[[TASK-0640-The-Release-Test-Payload]]", "[[TASK-0641-The-Release-Test-In-The-Tests-Pane]]"]
blocks: ["[[TASK-0644-Retire-The-Walk-Page-In-The-Publication-View]]"]
related: ["[[REQ-0070-The-Release-Test-Is-An-Overview-And-One-Page-Per-Section]]", "[[REQ-0071-A-Result-Is-Recorded-On-The-Check-Where-It-Was-Seen]]", "[[REQ-0069-The-Walk-Resumes-With-Valid-Evidence]]"]
tests: []
---

# The platform overview, Continue and Needs you

## Definition of Done

- [ ] Choosing a platform in the Tests pane opens its overview, headed "Test <version> on <platform>".
- [ ] The overview shows a progress bar split by result colour and a count per result ("11 Pass", "1 Fail").
- [ ] "Continue where you stopped" names the section and number of the next check with no result, and its action line. Choosing it opens that section and scrolls that check into view with focus on its first result button. When every check has a result, the button is hidden.
- [ ] "Needs you" lists every Fail, Question, Blocked and Partial result with its reason, and every declared decision and readiness problem from the payload. Each entry opens its check. The "Needs you" row at the top of the Tests pane shows the same count.
- [ ] The section list shows each section's dot, name, progress bar, done/total and one bench line. Choosing one opens it.
- [ ] After a result is saved on a section page, the overview's bar, counts, Continue and Needs you are correct without a reload. A renderer test proves it.
