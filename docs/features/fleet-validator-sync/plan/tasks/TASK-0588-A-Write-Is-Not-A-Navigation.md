---
type: "[[task]]"
id: TASK-0588
aliases: ["TASK-0588"]
title: "A write on `~checks` repaints without re-reading the address, so the reader's filters survive a mark"
status: done
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
owner: user:edwin
created: 2026-08-30
updated: "2026-08-30"
reviewed_by: model:claude-opus-5
review_date: 2026-08-30
review_verdict: changes-requested
source: ["[[ISS-0262-Marking-A-Check-Clears-The-Filter-You-Are-Walking]]"]
parent: "FEAT-0143"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[ISS-0203-The-Tier-Filter-Was-Sticky]]", "[[ISS-0188-The-Scroll-Fix-That-Did-Nothing]]"]
tests: []
---

# A write is not a navigation

## What changed

`renderChecksPage` gains `{ keepFilters }`, defaulting to `false` so navigation is untouched. `repaintChecksPage()` wraps it for the post-write path, and both `markCheckRow` and `retireCheckRow` use it.

`tsc --noEmit` is clean and `desktop/dist/renderer` is rebuilt, which is the artifact the app actually loads — the source change alone would have shipped nothing.

## Guards

`test_marking_a_check_does_not_clear_the_readers_filters` asserts on the repaint **callback**, not on the filter-reset lines: the reset is correct where it lives and the defect is which function is used as a repaint. Reverting the callback to `renderChecksPage` fails it, which was run rather than assumed.

`test_every_write_on_the_checks_page_repaints_the_same_way` forbids a bare `renderChecksPage()` anywhere in the file. Naming the two call sites would pass while a third write path copied the original mistake, which is the shape that produced this bug.

`test_the_address_still_wins_on_navigation` pins the other side, so the fix cannot drift into [[ISS-0203]]'s sticky filter.

## Independent review, 2026-08-30 — changes-requested

`tsc --noEmit` is clean, verified. Finding: [[ISS-0266]] — *"Reverting the callback to `renderChecksPage` fails it, which was run rather than assumed"* holds only for that spelling. The equivalent revert one line lower, inside `repaintChecksPage`, passes the full suite. Assert on the body of `repaintChecksPage`, not only on the call site.

Reviewed from a clean context (the notes and the diff, no authoring transcript) by `model:claude-opus-5`, the same model family as the author and a different session. Mutants were applied one at a time in a worktree at `c861414` and the full suite re-run; corpus figures were recomputed against `git archive fb99a751`, the `../your-trainer` state as of these commits.
