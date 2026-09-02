---
type: "[[change]]"
id: CHG-20260902-Five-Failing-Tests-Were-Measuring-The-Wrong-Thing
aliases: ["CHG-20260902-Five-Failing-Tests-Were-Measuring-The-Wrong-Thing"]
title: "The suite is green: five failures were tests measuring by proxy, and the per-check payload now carries the staleness its own sort used"
status: merged
owner: user:edwin
created: 2026-09-02
updated: "2026-09-02"
source: ["Edwin, 2026-09-02: \"Fix the 5 tests ... we cannot let tests fail\""]
commit: ""
pr: ""
impacts: ["tests/conftest.py", "tests/test_checks_view.py", "tests/test_tests_view.py", "tests/test_fleet_validate.py", "src/project_os_cockpit/cockpit.py"]
issues: ["[[ISS-0275]]", "[[ISS-0276]]"]
features: []
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[ISS-0274]]"]
---

# Five failing tests were measuring the wrong thing

## Summary

The suite is green. None of the five failures had found a defect — the code they guard was correct in every case, and each test was pinning its property by a proxy that had drifted.

One product change came out of it: a check's `stale` flag is now on the per-check nav payload item.

## What changed

**`tests/conftest.py` gains `js_function_body`.** It bounds a JS function by its own closing brace instead of by a guessed character count. It walks the parameter list by paren depth first, then counts braces — because taking the first `{` after the signature grabs a destructured parameter, which is what `test_release_page._body_of` does and why the first attempt returned an 84-character body.

**`test_checks_view.py::test_the_address_still_wins_on_navigation`** uses it. It had asserted over 3000 characters of `renderChecksPage` for a guard sitting at offset 3002.

**`src/project_os_cockpit/cockpit.py` — `_surface_rows` puts `stale` on each check item.** `_is_incomplete` counts a stale tick as owed and every sort, bar and percentage uses it; the item carried only `mark`, so the sort key was invisible to everything downstream. The renderer drew a stale `pass` identically to one that stands, and any test checking the order had to invent a second predicate.

**`test_tests_view.py::test_the_nav_leads_with_what_is_owed`** uses that flag instead of its own definition. It went red on `your-trainer`'s `History & analytics`, where `TST-0089` is `mark: pass` and stale — the product sorted it as owed and the test called it settled.

**`test_fleet_validate.py::_clone_repo` materialises `HEAD` with `git archive`** instead of copying the working tree. Three tests there assert the clone validates `ok`, so they failed for any uncommitted documentation edit; one unregistered note failed all three. `HEAD` is the basis CI and a fresh clone use.

**`test_the_cold_pass_command_never_carries_fix_metrics` builds its clone before installing its spy.** The spy replaces `subprocess.run`, `git archive` is a `subprocess.run`, and its argv was reaching an assertion about the validator's.

## Verification

Every fix was mutation-checked — guard removed, test confirmed red:

| Mutation | Goes red |
| --- | --- |
| `renderChecksPage` loses `if (!keepFilters)` | `test_the_address_still_wins_on_navigation` |
| surface items sorted by id only | `test_the_nav_leads_with_what_is_owed` |
| `_is_incomplete` stops counting stale as owed | `test_the_nav_leads_with_what_is_owed` |
| `summarise` always reports `state: ok` | 3 fleet tests |
| `summarise` always reports `errors: 0` | `test_a_drifting_repo_reports_its_own_error_count` |

The two fleet mutants are the ones that matter: they show the `HEAD` fixture removed the working-tree coupling without removing the teeth. The `_is_incomplete` mutant shows the realigned band predicate now pins a property the old one could not express at all.

The fleet fixture was also confirmed immune to the condition that broke it — 16/16 pass with an unregistered note sitting in `docs/`, which previously failed three.

## Not changed

21 fixed-window slices remain elsewhere in the suite, tracked as [[ISS-0276]] rather than swept in. `js_function_body` is not a drop-in for them — several anchor on a statement rather than a function signature — and converting a guard without studying what it pins is how a test gets quietly weakened.
