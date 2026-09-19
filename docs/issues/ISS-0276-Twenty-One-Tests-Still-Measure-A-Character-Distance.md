---
type: "[[issue]]"
id: ISS-0276
aliases: ["ISS-0276"]
title: "About 21 tests read a guessed number of characters after an anchor, so they can stay green while the code they guard is broken"
status: open
owner: user:edwin
reported_by: agent
created: 2026-09-02
updated: "2026-09-19"
severity: low
component: tooling
phase:
source: ["Split out of [[ISS-0275]], 2026-09-02"]
related: ["[[ISS-0275]]"]
tests: []
---

# About 21 tests can pass while the code they guard is broken

About 21 tests check source code by reading a fixed number of characters after an anchor, and that pattern has already let one real regression through with the test green.

## Problem

`src[i:i + N]` appears 21 more times across the suite after [[ISS-0275]] fixed the two that were failing. Each one asserts a property of some code by slicing a guessed number of characters after an anchor.

The idiom has now failed in both directions here, and both are recorded:

- **Too short** reports a regression that did not happen. `test_the_address_still_wins_on_navigation` looked for a guard at offset 3002 inside a 3000-character window ([[ISS-0275]]).
- **Too long** misses one that did. `test_release_held_back.py:373` records independent review placing a live `askForMark` call at anchor + 2621 inside a 2600-character window that ran 469,293 characters past its anchor, with the test still green.

## Where

`test_checks_view.py` (350, 501, 549, 562), `test_observed_coverage.py` (814), `test_release_page.py` (520, 552), `test_release_contents.py` (128, 181, 192, 212), `test_release_held_back.py` (284, 295, 307), `test_review_stale.py` (86, 198), `test_surface_orphan.py` (186), `test_tests_view.py` (2563, 2590), `test_acceptance_marks.py` (343, a 4-**line** window).

## Why not fixed with ISS-0275

`conftest.js_function_body` is not a drop-in. Several of these anchor on a statement (`for (const area of areas)`) rather than a function signature, so they need a different boundary — the enclosing block, or the next top-level declaration, which is what `test_release_held_back.py` already does by hand.

Converting a guard without studying what it pins is how a test gets quietly weakened, and this repo has the scar: [[ISS-0275]]'s own first attempt at a brace-matched helper latched onto a destructured parameter and returned an 84-character "body" that would have made several assertions vacuous rather than red.

## Next Actions

- [ ] Give `js_function_body` a sibling that bounds a statement by its enclosing block
- [ ] Convert the 21 call sites one at a time, mutation-checking each
- [ ] Consider a suite-level check that fails on a new fixed-window slice

## Checked against the code, 2026-09-19: still true, kept

**What a user notices:** A change can break a guarded behaviour in the renderer and the suite still passes, because the test looked at the wrong stretch of text. The opposite also happens: a correct change fails a test because the code moved a few characters.

Evidence: `grep -rnE "\[[a-z_]+ *: *[a-z_]+ *\+ *[0-9]{3,}\]" tests/*.py` returns 24 lines, three of them comments or docstrings (`conftest.py:27`, `test_checks_view.py:551`, `test_release_held_back.py:405`), leaving 21 live slices, e.g. `test_checks_view.py:371` (`src[i:i + 2200]`), `test_tests_view.py:2680` (`src[i:i + 6000]`), `test_release_held_back.py:295` (`src[i:i + 2600]`). `conftest.py:24` still offers only `js_function_body`, with no statement-bounded sibling.

**Belongs to:** no feature. **Next:** Bigger: add a statement-bounded helper next to `js_function_body`, then convert the sites one at a time with a mutation check each.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).
