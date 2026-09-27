---
type: "[[task]]"
id: TASK-0643
title: "The section page: what changed, Setup folded, grouped checks, and seven results with a required reason, written through the existing ledger path"
status: backlog
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

- [ ] The header names release test, platform, version and "Section n of m", the section title, and its check count.
- [ ] "What changed since <previous version>" comes first: this platform only, grouped by screen, one line per change. Screenshots sit in before/after pairs; clicking one opens it enlarged with its caption. A capture older than the latest change to its screen carries a dated tag and one warning line under the pictures.
- [ ] "Setup" is folded by default. Its summary line counts the bench items and the steps before you start. Open, it shows "On the bench", "Before you start" and "Later".
- [ ] The checks follow in groups. Each group has a heading and at most one "Start:" line. Each check shows its number, one action line, one expected line after an arrow, and its test tag in small type.
- [ ] Pass and Fail are one tap. "More" opens Partial, Question, Blocked, N/A and Excused, each with its one-line meaning as in the example. Tapping the current result again clears it.
- [ ] Every result except Pass opens a reason box; the result is not written to the ledger until the reason is filled in, and the empty box is outlined in the Fail colour.
- [ ] The row background takes the result's colour.
- [ ] A check that cannot be done yet is greyed, with one line of why, and "(suggested)" beside the suggested result under More. It can still be given any result.
- [ ] A timer shown on a check starts only when tapped and never sets a result.
- [ ] A check that asks for a screenshot or note at the moment of observation keeps that control on its row (REQ-0069).
- [ ] Results reach the ledger through `postCheckVerdict`. On a ledger copy, giving every check of a test note a result writes the same events as marking that test note directly, with the worst result winning.
- [ ] After a result, the reader stays on the page at the same scroll position, and the pane and overview update. A renderer test proves both.
- [ ] Keyboard: every control is reachable and shows focus; Escape closes More.
- [ ] Narrow widths (560 px and below) stack the result buttons under the check, as the example does.

## Notes

Offering N/A, Excused and Blocked on the section page is consistent with [[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]: the section page is where the procedure is read, and FEAT-0151 already offered those three on decision cards. A Pass here rests on the check's own expected line (decision D2), not on a procedure's quote of it.

Who is recorded as having given the result is still the constant `user:edwin`; that is [[ISS-0307-Every-Tick-From-The-Shell-Says-Edwin-Walked-It]] and is not fixed here.
