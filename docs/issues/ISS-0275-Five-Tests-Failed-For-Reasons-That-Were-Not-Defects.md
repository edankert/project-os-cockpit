---
type: "[[issue]]"
id: ISS-0275
aliases: ["ISS-0275"]
title: "Five tests failed and none of them had found a defect — two measured a character distance, one held a second definition of settled, and three read the author's uncommitted working tree"
status: fixed
owner: user:edwin
created: 2026-09-02
updated: "2026-09-02"
severity: medium
component: tooling
phase:
source: ["Edwin, 2026-09-02: \"Fix the 5 tests ... we cannot let tests fail\""]
related: ["[[ISS-0274]]", "[[CHG-20260902-Five-Failing-Tests-Were-Measuring-The-Wrong-Thing]]"]
tests: []
---

# Five tests failed for reasons that were not defects

## Problem

`pytest` reported five failures on `main`. Every one of them was green code and a test measuring the wrong thing. They are filed together because they are one shape: **a test that pins a property by proxy fails when the proxy moves and the property does not.**

## 1 and 2 — a window is a guess about a distance

`test_checks_view.py::test_the_address_still_wins_on_navigation` read `src[i:i + 3000]` from the start of `renderChecksPage` and looked for `if (!keepFilters) {`.

That guard sits at **offset 3002**. The function grew by two characters and the test went red with the behaviour fully intact.

The same idiom had already failed in the opposite direction and it is written down: `test_release_held_back.py:373` records a `src[i:i + 2600]` window over a file that runs 469,293 characters past its anchor, where independent review placed a live `askForMark` call at anchor + 2621 and the test passed. Too short reports a regression that did not happen; too long misses one that did.

**21 more call sites still use it.** They are listed in `## Still open` below.

The replacement is `conftest.js_function_body`, which counts braces. Writing it surfaced a bug in `test_release_page._body_of`, the function it was lifted from: **it takes the first `{` after the signature**, which for `renderChecksPage(tier, area, { keepFilters = false } = {})` is the destructured parameter, not the body. The "body" came back 84 characters long and the test failed again, for a new reason, wearing the old one's message. The shared helper walks the parameter list by paren depth first.

## 3 — a second definition of settled

`test_tests_view.py::test_the_nav_leads_with_what_is_owed` asserts that within a surface, checks that are still owed sort above ones that are settled. It computed *settled* as `mark in {pass, partial, na, excused}`.

The product computes it in `cockpit._is_incomplete`, whose docstring says: *"One predicate, shared by the percentage, the bar and every sort below. A second definition is how a surface's number and its position come to disagree about the same set."* The test wrote the second definition.

They differ on **stale**. A stale tick stands over evidence a change overtook, and `_is_incomplete` counts it as owed — the rule that stopped `your-trainer`'s honest 113 reading as 60. It went red on that repo's `History & analytics`, where `TST-0089` is `mark: pass` and stale: the payload sorted it into the owed band, the test called it settled, and **the product was right**.

The test could not have got this right, because `_surface_rows` put only `mark` on each item. The sort key was invisible to everything reading the payload — including the renderer, which drew a stale `pass` identically to one that stands. `stale` is on the item now, so there is one predicate.

## 4, 5 and 6 — three tests that read the author's uncommitted work

`test_fleet_validate.py`'s `_clone_repo` copied `SNAPSHOT.yaml`, `docs/` and `tools/` **off disk** and three tests assert the clone validates `ok`.

So all three failed for any uncommitted documentation edit — including the most ordinary mid-session state there is, a note written before the snapshot has caught up. Measured 2026-09-02: adding one unregistered `ISS-*` note failed all three, and none of them is about notes, snapshots or membership.

This is why they looked intermittent. They failed during the [[ISS-0274]] session while its notes were in flight, and passed an hour later once the commit had run `sync-snapshot.py` — with no code change between the two runs.

`_clone_repo` now materialises `HEAD` with `git archive`. That is the basis CI and a fresh clone use, and it is the gap `LIFECYCLE.md` opens its *"a local pass is not a CI pass"* section with; `validate-docs.sh --as-committed` already does the same thing for the same reason.

Hoisting that fixture exposed one more: `test_the_cold_pass_command_never_carries_fix_metrics` spies on `subprocess.run` to capture the validator's argv, and `_clone_repo` was called **inside** the spied region, so `git archive`'s argv reached the `--repo-root` assertion and failed it. The clone is built before the spy is installed.

## Evidence

Every fix was checked by mutation — the guard removed, the test confirmed red.

| Mutation | Test that goes red |
| --- | --- |
| `renderChecksPage` loses its `if (!keepFilters)` guard | `test_the_address_still_wins_on_navigation` |
| surface items sorted by id only | `test_the_nav_leads_with_what_is_owed` |
| `_is_incomplete` stops counting stale as owed | `test_the_nav_leads_with_what_is_owed` |
| `summarise` always reports `state: ok` | 3 fleet tests |
| `summarise` always reports `errors: 0` | `test_a_drifting_repo_reports_its_own_error_count` |

The two fleet mutants matter most here: they show the `HEAD` fixture removed the coupling **without** removing the teeth.

## Still open

21 fixed-window slices remain across `test_checks_view.py`, `test_observed_coverage.py`, `test_release_page.py`, `test_release_contents.py`, `test_release_held_back.py`, `test_review_stale.py`, `test_surface_orphan.py` and `test_tests_view.py`. Each is the same latent failure, in both directions. They are not converted here because `js_function_body` is not a drop-in for all of them — several anchor on a statement rather than a function — and rewriting a guard I have not studied is how a test gets quietly weakened. Tracked as [[ISS-0276]].
