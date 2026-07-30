---
type: "[[issue]]"
id: ISS-0066
aliases: ["ISS-0066"]
title: "A TST note's ## Coverage list is a hand-maintained register of its own assertions, and drift in it is indistinguishable from a false claim — TST-0022 took four review rounds to describe 27 assertions accurately"
status: open
phase: "[[PHASE-011-Unproven-Claims]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["independent review of PHASE-010, rounds 1–4 (2026-07-29..30)"]
severity: medium
component: docs-system
related: ["[[TST-0022-Surface-Ownership]]", "[[ISS-0065-Record-Column-Lost-Its-Source]]", "[[REQ-0025-No-Type-Loses-Its-Surface]]", "[[ADR-0009]]", "[[ADR-0010]]"]
tests: []
---

# Coverage registers drift by hand

## Problem

A `TST-*` note carries a `## Coverage` section: a numbered prose list of what its suite asserts. Nothing derives it from the suite, nothing checks it against the suite, and other notes cite its entries as evidence. [[REQ-0025]]'s criteria and [[PHASE-010]]'s exit criteria both name individual tests, and a reader checks those names against the Coverage register.

Across four independent-review rounds on [[TST-0022]], **every round found the register describing the suite inaccurately**, and each was a different instance of one class — the register claiming more, less, or other than the tests deliver:

| Round | Finding |
|---|---|
| 1 | [[REQ-0025]] criterion 5 ticked with an evidence pointer that did not resolve, against a claim that was false ([[ISS-0065]]) |
| 2 | Coverage listed 11 items for a 24-assertion file, omitting all four new guards; Evidence figures stale; item 9 credited a corpus test with a property only its synthetic companion has |
| 3 | Item 8 attributed a test living in `tests/test_cockpit.py` to this file — one round after item 9 was corrected for exactly that |
| 4 | Nothing wrong with anything claimed — verdict `approved`. The instances shrank by roughly an order of magnitude per round, which the reviewer read as convergence rather than a treadmill |

Two entries were missing for **three consecutive rounds** while being cited by name elsewhere: `test_the_skip_set_is_not_derived_from_the_empty_tuple` (cited by criterion 8; it guards against the entire Library reduction being undone) and the three stat-tile assertions (cited by criterion 2 and exit criterion 3, covering [[ISS-0063]], which the note declares in `verifies:`).

## Why this is a format problem, not an author problem

Each individual fix was correct and cheap. What did not happen, at any point, was the register becoming reliable — because keeping it accurate means hand-syncing prose to code on every test change, and nothing fails when that is skipped.

This repo has already decided this question twice, in the same direction:

- **[[ADR-0009]]** — statuses are authored once in the note and *derived* into `SNAPSHOT.yaml`, because the dual-write drifted. `counters` and `metrics.counts` likewise.
- **[[ADR-0010]]** — a test's `passing`/`failing` is written by the runner from an exit code, never asserted by an author, because an authored status claims verification that nothing performed.

A hand-written list of what a suite asserts is the same shape as both: a human-authored second copy of machine-readable truth. `## Coverage` is to the test file what a hand-copied status was to the snapshot.

And the failure mode is worse than staleness. A Coverage entry is *evidence* — criteria are ticked against it. An entry naming a test that does not exist, lives elsewhere, or asserts less than claimed is a false verification claim, which is precisely what ADR-0010 was written to make impossible.

## Evidence

```
$ .venv/bin/pytest tests/test_surface_ownership.py -q
27 passed

$ grep -c '^[0-9]\+\. \*\*' docs/features/library-reduction/plan/tests/TST-0022-Surface-Ownership.md
18
```

18 prose items for 27 assertions, after four rounds of correction. The mismatch is not itself a defect — one item can cover a parametrised test — but nothing distinguishes "one item covers three assertions" from "three assertions are undocumented", which is exactly how items 17 and 18 stayed missing.

## The reviewer's version of this is stronger than the original framing

Round four disagreed with half of the hypothesis and improved the rest, and the correction matters: **the register is not too large.** Eighteen items is readable. The problem is that it *duplicates what the test file's docstrings already say*, so the two can drift and only one of them is checked by anything. Every gap in rounds three and four was a drift between file and note, not a misunderstanding of either.

And the decisive evidence is not from the author's side. The reviewer's own round-two finding enumerated the Coverage omissions as "the four ISS-0065 guards" and **missed the stat tiles and the skip-set entirely** — the two entries that then stayed missing for another round. So the register drifted, and the independent enumeration of that drift was itself incomplete. **Two hand-maintained enumerations of the same file, wrong in different places, is a much better argument that neither should be hand-maintained** than any number of authoring slips.

It also names the cheapest sufficient check, which it ran by hand in round four: *every test collected from the `path:` file is either named in `## Coverage` or covered by an item that says which other file it lives in.* That single assertion would have caught both round-three items with no human involved.

## Expected

Either the register is derived from the suite, or it stops being cited as evidence.

## Next Actions

- [ ] Decide the shape. Sketches, cheapest first:
  - **Derive it.** Collect test names + first docstring lines from the `path:` file and render `## Coverage` in a managed block, the way `sync-snapshot.py` manages derived snapshot fields. Prose rationale stays hand-written *beside* each entry; the list of what exists does not.
  - **Check it (recommended — the reviewer's, and it ran by hand).** One assertion: every test collected from the `path:` file is either named in `## Coverage` or covered by an item that states which other file it lives in; and every test *named* in a Coverage entry or a requirement's evidence pointer exists where it is claimed to. Catches every round-two, -three and -four finding without generating anything, and needs no managed block.
  - **Demote it.** Keep Coverage as narrative and forbid citing it as evidence — criteria point at test names directly, which a validator can resolve.
- [ ] Whichever wins, add the rule to `QUALITY.md` and the `test-authoring` skill, and consider upstreaming: the format is template-owned, so every fleet repo has it.

## Notes

Raised by the reviewer's own invitation. It explicitly declined to allocate an ID — "a planning call, not a reviewer's" — which is the right line and is why this note exists rather than a verdict comment.

It is a finding about the *review process* as much as the format: four rounds converged on the code quickly (the record-column defect was found in round one and fixed in round two) while the prose describing it needed all four. That asymmetry is the signal — the code had tests, the register had a reader.

Filed against [[PHASE-999-Future]] rather than [[PHASE-010]] deliberately — PHASE-010 is `done`, and re-opening a closed phase to hold a finding about the documentation format would confuse "this phase's work is incomplete" with "this system has a gap the phase exposed". The second is true.
