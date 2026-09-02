---
type: "[[issue]]"
id: ISS-0276
aliases: ["ISS-0276"]
title: "21 tests still assert over a fixed character window, an idiom that has now failed in both directions in this suite"
status: open
owner: user:edwin
created: 2026-09-02
updated: "2026-09-02"
severity: low
component: tooling
phase:
source: ["Split out of [[ISS-0275]], 2026-09-02"]
related: ["[[ISS-0275]]"]
tests: []
---

# 21 tests still measure a character distance

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
