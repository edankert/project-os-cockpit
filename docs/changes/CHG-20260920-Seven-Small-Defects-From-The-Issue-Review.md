---
type: "[[change]]"
id: CHG-20260920-Seven-Small-Defects-From-The-Issue-Review
title: "Seven small defects from the issue review: six fixed, the security one made and waiting for Edwin"
status: merged
owner: user:edwin
created: 2026-09-20
updated: 2026-09-20
source: ["[[ISS-0313-Seven-Small-Defects-From-The-Issue-Review-Are-Still-In-The-Cockpit]], the work order", "project-os-dev PHASE-0007 step 3"]
commit: ""
pr: ""
impacts: ["[[SUR-0001]]"]
issues: ["[[ISS-0313-Seven-Small-Defects-From-The-Issue-Review-Are-Still-In-The-Cockpit]]", "[[ISS-0184-Clicking-A-Checkbox-In-The-Acceptance-Suite-Writes-To-A-Different-Row]]", "[[ISS-0266-Five-Mutants-Survive-The-Guards-Written-For-Them]]", "[[ISS-0271-Five-Tasks-Joined-A-Feature-That-Was-Done-And-Reviewed]]", "[[ISS-0278-The-Recorded-Stale-Verdict-Count-Is-Out-Of-Date]]", "[[ISS-0279-A-List-Valued-Type-Field-Loses-Its-Type]]", "[[ISS-0292-The-Status-Vocabulary-Is-Not-Served-So-Every-Client-Keeps-A-Copy]]", "[[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints]]"]
features: []
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0632-Fix-The-Seven-Defects-From-The-Issue-Review]]", "[[REFERENCE-CAPABILITY-REGISTER]]", "[[RISK-0008-The-Sandbox-Is-The-Only-Boundary]]"]
tags: [change, issue-review]
---

# Seven small defects from the issue review

## Summary

The 2026-09-19 review checked every open issue in this repo against the code and found seven that were real, still present and small. Six are now fixed with a test that fails when the fix is reverted. The seventh is a security change: the code is committed and [[ISS-0301]] stays `open` until Edwin has looked at it, which is what its work order asked for.

## Impact

- **A checkbox click is refused when it cannot name its own row.** A task list that opens on the line after a paragraph draws no checkbox, so the file holds rows the page does not, and every click below the first one wrote to the row above the one clicked — reporting success. The write now refuses when the page's count and the file's count disagree, and again when the prose on the clicked box is not the prose on the line about to change. A refusal is the point: where the address cannot be established the box is not writable, and the reader is told so ([[ISS-0184]]).
- **A note whose `type:` is a YAML list gets its type back.** Obsidian writes a property set through its editor as a list, so 99 of the 407 notes in Edwin's vault indexed untyped and the Library drew no Character, Page, Location, Chapter or Story group. The first usable element of the list is now the type ([[ISS-0279]]).
- **A second application can ask for the vocabularies instead of copying them.** `GET /api/cockpit/vocabulary` serves the status bands with their members and CSS tokens, the completed set, the legacy band mapping, the severity ranking, the severities a write will accept, and the callout types. project-os-deck copied the bands and put three statuses in the wrong one within two days; it can now drop its copy and offer a severity picker instead of a text box ([[ISS-0292]]).
- **A write whose `Content-Type` is not `application/json` is refused with 415.** A page the viewer frames runs on this machine, so the loopback guard passes it, and the body was parsed whatever the header said — which is the shape a browser sends cross-origin with no permission asked first. Every client was checked first and every one already sends the header, so nothing broke ([[ISS-0301]]).
- [[SUR-0001]]: **nothing a person sees changes from the test work.** Three fixes Edwin reported could have been undone by a one-line edit with every test passing; they now fail a named test. No product code changed for that ([[ISS-0266]]).
- **`docs/changes/` now records why the release page, the checks page and the gate changed on 2026-08-30**, and `CLAUDE.md` no longer tells every session a stale-verdict figure that was half the real one ([[ISS-0271]], [[ISS-0278]]).

## Documentation Coverage (All Types Considered)

- features: updated — [[FEAT-0143]]'s `acceptance_exception:` is narrowed to the eight migration tasks it actually covers.
- requirements: not-applicable — no requirement boundary moved. [[REQ-0027]] is applied more completely by the `Content-Type` refusal, not changed by it.
- tasks: new — [[TASK-0632-Fix-The-Seven-Defects-From-The-Issue-Review]], which this work hangs off.
- issues: updated — six of the seven are `fixed`; [[ISS-0301]] carries the fix and stays `open` for Edwin; [[ISS-0313]] is `fixed` with its boxes ticked or answered.
- tests: updated — four new test files or blocks, listed below. No `TST-*` acceptance check changed.
- workflows: not-applicable.
- decisions: not-applicable — no ADR is added or amended. [[ADR-0042]] and [[RISK-0008]] are both worth re-reading against the `Content-Type` refusal and neither is edited here.
- risks: not-applicable — no new dependency, environment variable, artifact path, long-running step, credential or licence. The risk scan's negative result is stated below.
- changes: new — this note, and [[CHG-20260830-Five-Fixes-To-The-Release-Page-The-Checks-Page-And-The-Gate]], which is the note [[ISS-0271]] says was owed and never written.
- snapshot: updated — `focus` moves off this work; the seven issues and the task carry their own statuses.

## The tests

Every one was run twice: once with the fix, once with it reverted. A test that did not fail on the revert would not have counted.

| fix | test | with the fix | reverted |
| --- | --- | --- | --- |
| [[ISS-0279]] | `tests/test_index.py` — two cases through `Index.build` and `type_counts()` | 18 passed | 2 failed |
| [[ISS-0184]] | `tests/test_check_toggle.py` — three, one on a file with three absorbed rows and two drawn | 13 passed | 3 failed |
| [[ISS-0292]] | `tests/test_vocabulary_route.py` — four over the live route | 4 passed | 4 failed |
| [[ISS-0266]] | six assertions across three existing files | 75 passed | each of five mutants fails a named test |
| [[ISS-0301]] | `tests/test_write_content_type.py` — nine, including a sweep over every guarded POST route | 9 passed | 7 failed |

## The suite and the validator

`2194 passed, 6 skipped` (`pytest -q -p no:randomly`, which includes the Node desktop suite), and `validate-docs.sh` is OK. `npx tsc --noEmit` is clean and `desktop/dist/renderer` is rebuilt, which is the artifact the app loads — the TypeScript change alone would have shipped nothing.

**Three failures during the work were fixed rather than reported around.** Two were terminal notes left in `PHASE-999-Future`, the parking lot: closing [[ISS-0184]] and [[ISS-0278]] stranded them there, which makes the phase strip draw shipped work as unplanned. Both now carry an empty `phase:`, as the other five issues in this order do. The third was a broken wikilink in the new task note. A pre-existing failure in `test_release.py` seen once on the first baseline run did not reproduce on any later run and is not a live failure.

## Risk scan: nothing new

No new external dependency or version constraint. No new environment variable or configuration surface. No directory layout or artifact path change. One new long-ish step, stated rather than skipped: the checkbox guard renders the note's body to count what the page draws, measured at **66 ms** on the largest checklist in the fleet. That is a click, not a page load, and there is no cheaper honest answer — pymdownx.tasklist's rules are the only authority on what draws a box. No credential or licence exposure. The one security-relevant change *narrows* a surface rather than widening it, and is carried by [[ISS-0301]] rather than by a new `RISK-*`.

## Follow-ups
- [ ] **Edwin reads [[ISS-0301]] and its curl.** Until then that issue stays `open`. This is the only thing this work is waiting on.
- [ ] project-os-deck drops `desktop/src/shared/statuses.ts` and its recorded fixture, and reads `/api/cockpit/vocabulary` instead. Work in that repo, tracked by [[ISS-0292]].
- [ ] `onOwnedPage` moves somewhere `desktop/tests/*.test.mjs` can execute it, so its guard stops being a source read. Recorded in [[ISS-0266]] as cut, not done.
