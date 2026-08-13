---
type: "[[task]]"
id: TASK-0416
aliases: ["TASK-0416"]
title: "Generalise the note-less obligation — one walk that yields a count and its rows, with standing documents as its first caller"
status: done
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
phase: "[[PHASE-030-Obligations-Go-Home]]"
source: ["[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]"]
parent: "[[FEAT-0100-Unpushed-Work-Needs-A-Person]]"
effort: M
depends: []
blocks: ["[[TASK-0417-Publication-Enters-The-Registry]]"]
related: ["[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[FEAT-0091]]"]
tests: []
---

# Generalise the note-less obligation

The registry enumerates by note type, which is its best idea and stays. But one obligation already has no note behind it — the standing document, whose subject is a manifest entry — and it is carried by **two special cases**: an addition inside `counts_by_kind()`, and a second inside `_needs_you_group()` because `owed_items()` yields no rows for it.

That seam has already failed: *"Intent's group came out 3 against a badge of 5."* Publication would be the second note-less obligation, and adding it the same way makes the third and fourth places for a number to disagree with itself.

## Definition of Done

- [x] `NoteLessObligation` is declared once and yields count **and** rows from one walk — `counts_by_kind` now counts `len()` of the very list `owed_items` returns.
- [x] The standing document is expressed through it and **both bolt-ons are gone**: the addition inside `counts_by_kind` and the row-scraping inside `_needs_you_group`.
- [x] The completeness test has its sibling (`test_every_note_less_source_is_declared_and_enumerable`): every declared source must name a noun, a verb, a known view, and actually enumerate.
- [x] `badges_payload`'s total still equals the sum of the badges, note-less sources included.
- [x] Vocabulary ships from the server; the renderer picks a string and owns no plural rule.

## It simplified standing, which was the test of the shape

The DoD said *if it does not simplify standing, it is the wrong shape.* It did, in a way not anticipated: the duplication was not only in the counting.

`cockpit._standing_group` was resolving manifest paths and choosing between the `/docs/<rel>` and `~root/<file>` routes **itself**, while `obligations` counted findings separately — two derivations that agreed by coincidence. Both now read `standing.entries()`, one walk that resolves and describes, and the group asks the registry which entries are *owed* rather than re-deriving it from `STANDING_OWED_KINDS`. One predicate, one verb table, one route.

**Two test carve-outs were deleted, which is the real evidence.** `test_the_counted_group_with_no_rows_is_the_standing_one` asserted that a counted group with no rows was legal *if* it was the standing kind; it is now `test_no_counted_group_is_left_without_its_rows`, asserting the list is empty. And `test_owed_items_and_counts_agree_kind_by_kind` had an exception excluding the standing kind — *the exception was exactly where the two functions had drifted, by five against three* — and it is gone.

Both now run against `owed_corpus`, which manufactures the neglect this repo no longer has; against the live corpus they would pass vacuously.

## Two things it dragged in

- **`owed_corpus` moved to `tests/conftest.py`.** A second module needed it, and copying it would have been the same mistake this task removes from the production code.
- **`pyproject.toml` gained pytest config.** Adding that conftest changed how pytest resolves the rootdir, and a bare `pytest` started walking into `desktop/python-runtime/` — the bundled interpreter — colliding on `test_tools.py`. Collection had been scoped by the *absence* of a conftest, which is not a configuration. `testpaths` and `norecursedirs` now are.
