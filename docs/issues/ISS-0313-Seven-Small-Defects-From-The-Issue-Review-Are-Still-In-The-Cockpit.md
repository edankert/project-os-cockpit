---
type: "[[issue]]"
id: ISS-0313
aliases: ["ISS-0313"]
title: "Seven real defects found by the 2026-09-19 issue review are still in the cockpit, each small enough to fix with one test"
status: fixed
phase: []
owner: user:edwin
created: 2026-09-19
updated: 2026-09-20
source: ["The issue review of 2026-09-19 (project-os-dev FEAT-0036, TASK-0141)", "Edwin, 2026-09-19: 'Do all 5 steps in the suggested order'"]
reported_by: review
question: ""
severity: medium
component: "multiple"
parent: ""
related: []
tests: []
fixed_by: "[[TASK-0632-Fix-The-Seven-Defects-From-The-Issue-Review]]"
tasks: ["[[TASK-0632]]"]
---

# Seven small defects from the issue review are still in the cockpit

## Problem

On 2026-09-19 every open issue in this repo was checked against the code. Seven are real, still present, and small: each is a few lines in one place, and a test can prove it. **This ticket is the work order for fixing them.** Each line links the issue that holds the evidence.

## How to work this ticket

1. **One issue at a time.** Read its note first. Its section headed "Checked against the code, 2026-09-19" gives the evidence and the fix.
2. **Make the fix, with a test that fails without it.** Run the test with the fix, then with the fix removed, and record both results in the issue note. A test that cannot fail does not count. A docs-only item needs no test.
3. **Close the issue.** Set it to `fixed`, and add a section saying what changed, which test guards it, and the commit.
4. **Tick the box below** and commit, naming the paths.
5. **If a fix turns out to be bigger than described**, or changes something Edwin should see first, do not force it. Note that in the issue, leave it open and move on.

## The Seven

- [x] [[ISS-0184-Clicking-A-Checkbox-In-The-Acceptance-Suite-Writes-To-A-Different-Row|ISS-0184]]: ticking a checkbox on a page can tick a different box in the file, when the page and the file hold a different number of boxes. Send the box's text with its position (`renderer.ts:2851`), and have `_toggle_task_at` (`server.py:4266`) refuse when they disagree, as the labelling path already does with `data-raw`. Test the refusal.
- [x] [[ISS-0279-A-List-Valued-Type-Field-Loses-Its-Type|ISS-0279]]: a note whose `type:` is a list shows as untyped. `_normalise_type` (`index.py:657`) returns None for anything but a string; take the first string in a list, with a unit test.
- [~] [[ISS-0301-A-Framed-Page-Can-Post-To-The-Loopback-Write-Endpoints|ISS-0301]]: a page shown in the cockpit's frame can post to its write endpoints. Refuse a write whose `Content-Type` is not `application/json` in `_read_json_body` (`server.py:1889`), after checking that Deck and `cockpit signal` send that header. Test a `text/plain` post is refused. *Security: show Edwin before closing.*
- [x] [[ISS-0292-The-Status-Vocabulary-Is-Not-Served-So-Every-Client-Keeps-A-Copy|ISS-0292]]: Deck keeps its own copy of the status groups, severities and note types. Serve them from one `/api` route built from `statuses.py`, with a test of the payload.
- [x] [[ISS-0266-Five-Mutants-Survive-The-Guards-Written-For-Them|ISS-0266]]: three guards can be broken with every test still passing (mutants B1, B2, C2). Add a test asserting `keepFilters: true` in `repaintChecksPage`, one covering the rest of `onOwnedPage`, and one for the mark dialog's readable verdict.
- [x] [[ISS-0271-Five-Tasks-Joined-A-Feature-That-Was-Done-And-Reviewed|ISS-0271]]: docs only. Write the change note for the five page fixes under FEAT-0143, and narrow its `acceptance_exception:`, which says it has no user-facing surface.
- [x] [[ISS-0278-The-Recorded-Stale-Verdict-Count-Is-Out-Of-Date|ISS-0278]]: docs only. `CLAUDE.md:115` says 49 notes and 43 finished carry stale verdicts; today it is 89 and 76. Update the figures with the command that counts them.

This ticket closes when every box is ticked, or its issue says why it was left.

## Worked 2026-09-20 under [[TASK-0632-Fix-The-Seven-Defects-From-The-Issue-Review]]

Six of the seven are `fixed`. **ISS-0301 is made and left `open`**, which is what its box being `- [~]` records: the ticket marks it *"Security: show Edwin before closing"*, so the code is committed and the status waits on Edwin.

| issue | outcome | the test that guards it | commit |
| --- | --- | --- | --- |
| [[ISS-0279]] | fixed | `tests/test_index.py::test_a_type_written_as_a_list_is_the_same_type_as_the_string` and `::test_the_first_usable_element_of_a_type_list_wins` | `2c6059a` |
| [[ISS-0184]] | fixed | `tests/test_check_toggle.py` — three, the first on a file with three absorbed rows and two drawn ones | `8ac3c76` |
| [[ISS-0292]] | fixed | `tests/test_vocabulary_route.py` — four over the live route | `c5256c9` |
| [[ISS-0266]] | fixed | six assertions across `test_checks_view.py`, `test_mark_check_is_readable.py` and `test_release_contents.py`; all five mutants re-run and killed | `1f6ba29` |
| [[ISS-0301]] | **made, left open for Edwin** | `tests/test_write_content_type.py` — nine, including a sweep over every guarded POST route | `56ab147` |
| [[ISS-0278]] | fixed | none — docs only | `9445a09` |
| [[ISS-0271]] | fixed | none — docs only | `4416d29` |

**Every fix was run both ways.** Each issue note records the pass with the fix and the failure with it reverted; nothing was asserted without being run.

**Two turned out larger than the one-line description and were still done in one place.** [[ISS-0184]] needed a refusal on the *counts*, not only on the text, because the text is unavailable in exactly the case that breaks — a document whose counts disagree carries no `data-raw` at all. [[ISS-0301]] needed five more handlers than the report named: each had its own copy of the body reader and would have kept the hole open.

**What was found and not fixed**, each recorded in its own issue rather than here: `onOwnedPage` still lives where only a source-reading test can reach it ([[ISS-0266]]); the `Origin` check and the shell-only token are not made ([[ISS-0301]]); the five tasks keep their parent ([[ISS-0271]]); Deck still carries the copy this cockpit now serves ([[ISS-0292]]).
