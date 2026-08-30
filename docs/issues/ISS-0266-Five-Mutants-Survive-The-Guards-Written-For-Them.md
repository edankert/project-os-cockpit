---
type: "[[issue]]"
id: ISS-0266
aliases: ["ISS-0266"]
title: "Five mutants survive the guards written for them — the renderer fixes are pinned by source-text greps, so a one-token edit restores ISS-0262 and ISS-0263 with the full suite green"
status: triage
owner: user:edwin
created: 2026-08-30
updated: "2026-08-30"
severity: high
component: tests
phase:
source: ["Independent review of 46d6593..c861414, 2026-08-30, model:claude-opus-5, fresh context"]
related: ["[[ISS-0262-Marking-A-Check-Clears-The-Filter-You-Are-Walking]]", "[[ISS-0263-A-Write-Evicts-The-Reader-From-The-Checks-Page]]", "[[ISS-0264-A-Write-Is-Not-Readable-By-The-Next-Request]]", "[[ISS-0261-A-Release-Is-Offered-Features-Its-Platform-Cannot-Ship]]", "[[TASK-0588-A-Write-Is-Not-A-Navigation]]", "[[TASK-0589-A-View-Knows-Which-Pages-It-Owns]]", "[[TASK-0590-A-Write-Is-Readable-When-It-Answers]]", "[[TASK-0587-The-Derived-Set-Is-This-Releases-Platforms]]"]
tests: []
---

# Five mutants survive the guards written for them

## What was measured

Every fix in `46d6593..c861414` was mutated one at a time in a clean worktree at `c861414` and the suite re-run. Ten mutants; five die, **five survive**. Three of the survivors restore the exact defect the note says was fixed.

| # | mutant | outcome |
|---|---|---|
| A1 | `shipping_in` returns `rows` unfiltered | **killed** — `test_an_android_release_is_not_offered_ios_features` |
| A2 | `_ships_on` → `return f == r` | **killed** — `test_cross_platform_spellings_are_not_dropped` *and* the pre-existing claimed-by-another-release test, exactly as TASK-0587 says |
| A3 | `_publication_groups` back on `unreleased_payload` | **killed** — `test_the_navigator_and_the_page_derive_the_same_set` |
| **A4** | `release_payload`: `derived_rows = unshipped["items"]` | **SURVIVES the full suite** |
| **A5** | `release_payload`: `"count": int(unshipped["count"])` | **SURVIVES the full suite** |
| **B1** | `repaintChecksPage` → `return renderChecksPage('', '');` | **SURVIVES** |
| **B2** | `onOwnedPage` → `return false;` after the `~${navMode}` test | **SURVIVES** |
| B3 | `VIEW_OWNED_PAGES.tests = []` | killed — `test_a_write_does_not_evict_the_reader_from_the_checks_page` |
| C1 | `mark-check` stops calling `_reindex` | killed — both tests in `test_mark_check_is_readable.py` |
| **C2** | `retire-check` stops calling `_reindex` | **SURVIVES** |
| D1/D2/D3 | the retired filter removed from either branch, or keyed on `mark` | killed — both `ISS-0265` guards, on both branches |

## The three that matter

**B1 restores [[ISS-0262]].** `repaintChecksPage()` is the whole of that fix, and nothing asserts what it *passes*. `test_marking_a_check_does_not_clear_the_readers_filters` greps for the string `walkOneCheck(item, repaintChecksPage)`; `test_the_address_still_wins_on_navigation` greps inside `renderChecksPage` for `keepFilters = false` and `if (!keepFilters) {`; `test_every_write_on_the_checks_page_repaints_the_same_way` forbids the literal `renderChecksPage()`. Change one line inside `repaintChecksPage` from `renderChecksPage('', '', { keepFilters: true })` to `renderChecksPage('', '')` and all three still pass while every tick clears the reader's tier and area again. TASK-0588 says *"Reverting the callback to `renderChecksPage` fails it, which was run rather than assumed"* — true of that one spelling, and only of that one.

**B2 restores [[ISS-0263]].** `onOwnedPage` reduced to its first two lines is exactly the equality test the fix replaced; `VIEW_OWNED_PAGES` stays in the file, the call site stays in `loadWsNav`, and the two guards keep passing because they check that the constant exists and that the call is spelled that way. The reader is evicted from `~checks` on every mark again.

**C2.** TASK-0590 says *"Removing the `_reindex` call fails both. Run, not assumed."* Removing it from `_serve_retire_check` fails nothing — `test_mark_check_is_readable.py` exercises `mark-check` only. The retire path repaints immediately after the response for the same reason the mark path does, so the call is load-bearing and unguarded.

**A4 is the reported surface.** [[ISS-0261]] is about a release *page* listing ten features it cannot ship. `release_payload` is that page. Reverting its one changed line to the unfiltered set passes **2126 tests** — the whole suite, with the two worktree-path failures and the one pre-existing corpus failure deselected. The guards cover `shipping_in` (the helper) and `_publication_groups` (the navigator); the page reads `shipping_in` and nothing checks that it does.

## The agreement assertion does not assert agreement

`test_the_navigator_and_the_page_derive_the_same_set` closes with:

```python
assert on_the_page <= in_the_pane or in_the_pane <= on_the_page
```

TASK-0587 describes this as asserting *"they AGREE rather than asserting a fact about either, so it fails whichever one moves next"*. A subset relation in **either** direction satisfies it, so it passes when the navigator drops rows, when it gains rows, and when it returns nothing at all. Only a crossing divergence fails it. The test's actual load-bearing line is the one above it — `assert "FEAT-0002" not in in_the_pane` — which is a fact about one side, the thing the note says it deliberately avoided. In the fixture the two sets are exactly equal, so `assert on_the_page == in_the_pane` would work and would mean what the note claims.

## Why the greps are not enough, in this repo's own words

`tests/test_desktop_node_suite.py` opens: *"Every other desktop guard in this repo reads TypeScript source and asserts that a string appears in it. Both design-bench reviewers walked through one of those independently (ISS-0055's closing observation): a rename, or a hoist, and the guard still passes while the behaviour it names is gone."* B1 and B2 are that observation arriving a third time, on a fix whose note says it was mutation-tested.

## Next Actions

- [ ] Assert inside `repaintChecksPage`'s body that it passes `keepFilters: true`, and inside `onOwnedPage`'s body that it consults `VIEW_OWNED_PAGES[navMode]` — both kill their mutant without a new harness.
- [ ] Guard `release_payload`'s derived rows and count directly (the fixture in `test_release_contents.py` already has everything needed).
- [ ] Extend `test_mark_check_is_readable.py` to `retire-check`.
- [ ] Make the navigator/page assertion an equality.
- [ ] Longer term: `onOwnedPage` is a pure function and belongs where `desktop/tests/*.test.mjs` can run it.
