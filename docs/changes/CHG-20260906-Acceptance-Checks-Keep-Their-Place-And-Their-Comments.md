---
type: "[[change]]"
id: CHG-20260906-Acceptance-Checks-Keep-Their-Place-And-Their-Comments
aliases: ["CHG-20260906-Acceptance-Checks-Keep-Their-Place-And-Their-Comments"]
title: "The acceptance checks page keeps the walk: a failing verdict is no longer erased, every comment on a check is reachable, and returning to a project resumes where you were"
status: merged
owner: user:edwin
created: 2026-09-06
updated: 2026-09-06
source: ["Edwin, 2026-09-06, three reports while walking v2.1.x's suite in ../your-trainer"]
commit: ""
pr: ""
impacts: ["src/project_os_cockpit/acceptance.py", "src/project_os_cockpit/ledger.py", "desktop/src/renderer/renderer.ts", "desktop/src/renderer/renderer.css", "docs/reference/cockpit-capability-register.md"]
issues: ["[[ISS-0280-The-Checks-Page-Does-Not-Survive-Leaving-The-Project]]", "[[ISS-0281-A-Failing-Verdict-Is-Erased-From-The-Checks-View]]", "[[ISS-0282-The-Mark-Dialog-Hides-The-Check-It-Marks]]", "[[ISS-0284-The-Tier-Chips-Filter-Nothing]]"]
features: []
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]", "[[REFERENCE-CAPABILITY-REGISTER]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ISS-0262-Marking-A-Check-Clears-The-Filter-You-Are-Walking]]"]
---

# The checks page keeps the walk

## Summary

A check somebody marked `fail` used to appear on `~checks` as one nobody had walked, and the sentence they wrote explaining the failure was not on the screen anywhere. That is fixed, along with two other losses on the same page: every comment a check carries is now reachable from the mark dialog, and coming back to a project puts the reader back on the page and the filters they left.

Nobody was told the wrong answer about *whether a release could ship* — a failing check blocked the gate throughout, because a `fail` and an unwalked check both block. What was wrong is everything a person needs in order to act: which check failed, and why.

## The four, and what each one does now

**A verdict that does not clear reaches the row.** `acceptance.apply_ledger` resolves a check against every platform's ledger when no platform is named. It kept a verdict only when every platform cleared it, so a `fail`, a `blocked` or a `question` was dropped and the row fell back to `todo` with an empty reason. `~checks` always takes that branch — it fetches `/api/cockpit/acceptance` with no platform. Measured on `../your-trainer` on 2026-09-06: the ledger resolved two `fail` and one `question`, and the page showed none of the three, including one Edwin had recorded that morning. Clearing still takes every platform and still reports the earliest verdict, which is [[DES-0012]] D4 unchanged. What is new is that a check which does *not* clear now reports the most recent non-clearing verdict rather than silence.

**A check's comments are reachable.** The ledger is append-only and keeps every event, so a check marked `fail` with a paragraph and later marked `pass` still holds the paragraph — and nothing read one back. The acceptance payload now carries `view.history`: every event per check, newest first, with its mark, date, platform, author, method and comment. The mark dialog shows them; the row says how many a check carries when the current verdict is not the only one. On the row itself the comment moved out of the meta line, where it was the second clause after a timestamp in 11px grey, onto a line of its own marked as a quotation — **except the migration's**, which is one identical paragraph on 512 of `your-trainer`'s 624 checks and would have buried the 99 a person wrote under five hundred copies of itself. `_row` carries `verdict_method` so the row can tell them apart.

**The walk survives leaving the project.** Switching workspace cleared the page (`openWorkspace` clears `currentRel`, so the Tests view lands on its own `~tests` landing) and the filters (`checkFilters` was module state nothing persisted). Both are now stored per workspace under `cockpit:checks-place:<workspaceId>` and restored when the sidecar comes up, provided nothing else has claimed the centre pane — a cross-repo jump or a clicked note still wins.

**The tier chips select something that exists.** Found while verifying the fix above in the live harness, and fixed here rather than filed ([[ISS-0284]]). The tier facet carries the section key — `feature`, `regression`, `automated` — and `checkMatches` compared the tier number, so every chip in that row selected a value no row could match: clicking one changed nothing, and on a bare `~checks` it emptied the page. It is fixed here because [[ISS-0280]] persists the filter set, and a per-session bug a reader clicks past becomes a stored state they return to.

**The mark dialog shows a check a person can read.** It is given the note's address and renders the body through `/api/render` — the path the centre pane and the review pane already use, so no second Markdown dialect and `[[wikilinks]]` resolve as they do everywhere else. The plain text is mounted first and stays if the fetch fails. The card, the body and the comment list are each bounded, because the first cut set `textContent` on an unbounded card: `TST-0062`'s 2,230-character body made a 1,245px card in a 963px window, centred from -141px to 1,104px, with the title above the screen and **Save below it**. Edwin, on that cut: *"The dialog only shows the main title/description not the actual tst details."*

## What a reader will notice

- A failed or blocked check reads as failed or blocked, with its date and the reason, instead of as unwalked.
- The comment behind a verdict is a line of its own under the check's description.
- A row whose check has more comments than the one on screen says so: `2 comments`.
- Opening the mark dialog shows the check's body rendered — headings, lists, bold, code — and every comment the check carries above the buttons, newest first, with Save always on screen.
- Switching projects and coming back returns to the same checks page with the same filters.
- Clicking a tier chip adds or removes that section, instead of doing nothing.

## Compatibility

The payload gains `view.history` and loses nothing. A repo with no ledger — nine of twelve in the fleet — gets `{}` there and is otherwise untouched: its verdicts still come from the note, and no history is synthesised from a single scalar. The migration backfill's per-check boilerplate (584 entries in `your-trainer`) is counted in a closing line rather than shown as a comment.

## Deliberate exception to a standing rule

[[ISS-0262]] says the address decides the filters and a repaint does not. Restoring a workspace is a third case: the reader typed no address and no write happened. It is carried by `pendingChecksFilters`, consumed by exactly one render, so an ordinary navigation after a restore still clears the axes the address does not name. Two of the five filter axes fit in an address and three — mark, covers, automation — do not, and `mark` is the one a walker uses, so restoring the address alone would have brought back the page without the walk.

## Verification

`tests/test_ledger.py` gains five guards (a non-clearing verdict survives the platform-less view; the worst verdict wins when platforms disagree; absence is still `todo`; the history carries a superseded comment, newest first; a ledger-less repo offers no history). `tests/test_checks_view.py` gains fourteen (the place is per workspace, the landing reads it, a restore is neither a navigation nor a repaint, the dialog is given the check and renders it, the migration backfill is not shown as a comment, the comment is its own line on the row, the tier predicate consults both vocabularies from both ends, the payload does not survive a workspace switch, the dialog renders the body rather than printing it, the card and its long blocks are bounded, the migration boilerplate is not quoted on every row, and the payload says how each verdict was recorded).

All four were driven in the live harness against `../your-trainer`'s real payload, not only asserted in the suite: the dialog opened on `TST-0603` showing its prose and both comments — including the `fail` Edwin wrote on 2026-09-05 that no surface could reach — the stored place came back as `~checks/tier/1` across a reload, and the Regression chip added and removed its section.

Full suite: 2173 passed, 5 skipped, three failures that predate this work and are unrelated to it — `test_the_measured_repo_still_reports_what_this_phase_measured` and `test_gate_delta.py`'s two chronic-row tests, all three asserting that `../your-trainer` still owes work that Edwin has since walked. Filed as [[ISS-0283-A-Test-Pins-Another-Repos-Blocking-Count]] and each verified independent of this change by stashing it. `test_desktop_build_is_not_stale` also failed and is fixed here by rebuilding `desktop/dist`.

**To see this, the app must be restarted.** The shell loads `desktop/dist` at launch and spawns one Python sidecar per workspace, so a session started before this commit holds both the old bundle and the old sidecars: the dialog's render call, `view.history` and `verdict_method` are all absent until it comes back up.
