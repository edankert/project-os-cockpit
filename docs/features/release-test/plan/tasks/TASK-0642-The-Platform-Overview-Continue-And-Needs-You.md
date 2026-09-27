---
type: "[[task]]"
id: TASK-0642
title: "The platform overview: a bar coloured by result with a count per result, Continue where you stopped, Needs you, and the section list with bench lines"
status: doing
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

- [x] Choosing a platform in the Tests pane opens its overview, headed "Test <version> on <platform>". "Test v2.2.0 on Android".
- [x] The overview shows a progress bar split by result colour and a count per result ("11 Pass", "1 Fail"). `rt-bar-split` and the tally chips.
- [x] "Continue where you stopped" names the section and number of the next check with no result, and its action line. Choosing it opens that section and scrolls that check into view with focus on its first result button. When every check has a result, the button is hidden. `rtContinue`; the address carries `#rt-check-N`, and `rtFocusCheck` scrolls to it and focuses its Pass button (seen in the browser); hidden when nothing is left.
- [ ] "Needs you" lists every Fail, Question, Blocked and Partial result with its reason, and every declared decision and readiness problem from the payload. Each entry opens its check. The "Needs you" row at the top of the Tests pane shows the same count.
- [x] The section list shows each section's dot, name, progress bar, done/total and one bench line. Choosing one opens it. `rt-sec` rows.
- [x] After a result is saved on a section page, the overview's bar, counts, Continue and Needs you are correct without a reload. A renderer test proves it. The overview is drawn from the browser's results every time it opens; `release-test.test.mjs` proves the counts, Continue and Needs you change with one result.

## Close-out, 2026-09-27 — one box open

"Needs you" on the overview lists Fail, Question, Blocked and Partial results with their reasons, and declared readiness problems, each opening its check. **Not done: the "Needs you" row at the top of the Tests pane does not add these.** That row is the server's list of owed test notes, and a result given on a printed check lives in the browser until its test note is complete, so the server cannot count it. Either the pane's row gains a count the renderer adds, or the box is reworded; this is for the pilot (TASK-0645) to settle with Edwin.
