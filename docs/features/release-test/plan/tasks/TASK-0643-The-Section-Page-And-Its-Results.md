---
type: "[[task]]"
id: TASK-0643
title: "The section page: what changed, Setup folded, grouped checks, and seven results with a required reason, written through the existing ledger path"
status: done
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-27
updated: 2026-09-27
source: ["Edwin, 2026-09-27: approved example page"]
parent: "[[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]"
effort: "L"
due: ""
depends: ["[[TASK-0640-The-Release-Test-Payload]]"]
blocks: ["[[TASK-0645-Pilot-The-Equipment-Section-Then-The-Rest]]"]
related: ["[[REQ-0070-The-Release-Test-Is-An-Overview-And-One-Page-Per-Section]]", "[[REQ-0071-A-Result-Is-Recorded-On-The-Check-Where-It-Was-Seen]]", "[[REQ-0069-The-Walk-Resumes-With-Valid-Evidence]]", "[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]", "[[ISS-0263-A-Write-Evicts-The-Reader-From-The-Checks-Page]]", "[[ISS-0307-Every-Tick-From-The-Shell-Says-Edwin-Walked-It]]", "[[RISK-0010-Saved-Walk-Observations-Can-Outlive-Their-Source]]"]
tests: []
---

# The section page and its results

## Definition of Done

- [x] The header names release test, platform, version and "Section n of m", the section title, and its check count. "Release test · Android · v2.2.0 · Section 2 of 14", the title, "28 checks · 4 test notes".
- [x] "What changed since <previous version>" comes first: this platform only, grouped by screen, one line per change. Screenshots sit in before/after pairs; clicking one opens it enlarged with its caption. A capture older than the latest change to its screen carries a dated tag and one warning line under the pictures. Screens with their lines; pictures open enlarged with a caption (`rtEnlarge`); a stale capture carries its date and a warning line.
- [x] "Setup" is folded by default. Its summary line counts the bench items and the steps before you start. Open, it shows "On the bench", "Before you start" and "Later". Summary "3 things on the bench · 3 steps before you start · 11 later"; it stays open while the page redraws after a result.
- [x] The checks follow in groups. Each group has a heading and at most one "Start:" line. Each check shows its number, one action line, one expected line after an arrow, and its test tag in small type. `rt-group`, `rt-start`, `rt-check`.
- [x] Pass and Fail are one tap. "More" opens Partial, Question, Blocked, N/A and Excused, each with its one-line meaning as in the example. Tapping the current result again clears it. Choosing the current result again clears it.
- [x] Every result except Pass opens a reason box; the result is not written to the ledger until the reason is filled in, and the empty box is outlined in the Fail colour. `rtNoteResults` writes nothing until every reason is filled in; `release-test.test.mjs`.
- [x] The row background takes the result's colour. `data-mark` on the row.
- [x] A check that cannot be done yet is greyed, with one line of why, and "(suggested)" beside the suggested result under More. It can still be given any result. `rt-muted` and the flag line; "(suggested)" under More.
- [x] A timer shown on a check starts only when tapped and never sets a result. `rtBuildTimer`.
- [x] A check that asks for a screenshot or note at the moment of observation keeps that control on its row (REQ-0069). The row has a note box and a PNG picker; the picture is filed under the check's first test note through `/api/notes/attach` (`rtAttachPicture`), and its path is kept with the note. `rtSafeAttachment` refuses any reply path outside `attachments/<TST>/`; `release-test.test.mjs` tests it, and `tests/test_attachments.py` covers the route.
- [x] Results reach the ledger through `postCheckVerdict`. On a ledger copy, giving every check of a test note a result writes the same events as marking that test note directly, with the worst result winning. In the browser on a copy of your-trainer, Pass on check 6 (TST-0028's only printed check) wrote one `{"result": "pass", "method": "manual", "by": "user:edwin"}` event, the same event marking TST-0028 directly writes. `rtWorst` picks the most serious result; tested.
- [x] After a result, the reader stays on the page at the same scroll position, and the pane and overview update. A renderer test proves both. The scroll position is restored and `rtRefreshPane` updates the pane; the data half is tested, the scroll was seen in the browser.
- [x] Keyboard: every control is reachable and shows focus; Escape closes More. Buttons and inputs are native controls; Escape closes More and returns focus to it.
- [x] Narrow widths (560 px and below) stack the result buttons under the check, as the example does. The media query stacks the result buttons under the check.

## Notes

Offering N/A, Excused and Blocked on the section page is consistent with [[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]: the section page is where the procedure is read, and FEAT-0151 already offered those three on decision cards. A Pass here rests on the check's own expected line (decision D2), not on a procedure's quote of it.

Who is recorded as having given the result is still the constant `user:edwin`; that is [[ISS-0307-Every-Tick-From-The-Shell-Says-Edwin-Walked-It]] and is not fixed here.

## Close-out, 2026-09-27

**A capture is a typed note, not a screenshot.** A check that asks the tester to keep what they saw gets a note box kept in the browser with the check. The walk page could also attach a picture through the evidence upload; that is not ported. Whether the pilot needs it is for TASK-0645 with Edwin.

**Picture capture, added the same day.** The walk page's evidence upload is ported to the release test: a check with a capture offers a PNG picker beside its note box. It was not tried in the browser, because the harness had stopped; the request is the one the walk page sent, to a route that is unchanged.
