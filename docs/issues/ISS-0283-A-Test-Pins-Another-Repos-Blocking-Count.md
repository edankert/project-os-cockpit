---
type: "[[issue]]"
id: ISS-0283
aliases: ["ISS-0283"]
title: "Three tests pin ../your-trainer's outstanding work — a blocking count of 40 or more and the existence of chronic rows — so walking the release down turns the suite red; the assertions measure how much is left in another repo, not this code"
status: fixed
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-09-06
updated: 2026-09-06
source: ["Found while running the suite for CHG-20260906-Acceptance-Checks-Keep-Their-Place-And-Their-Comments"]
severity: medium
component: tests
parent: ""
related: ["[[ISS-0281-A-Failing-Verdict-Is-Erased-From-The-Checks-View]]", "[[CHG-20260902-Five-Failing-Tests-Were-Measuring-The-Wrong-Thing]]"]
tests: []
---

# Three tests pin another repo's outstanding work

## Problem

`tests/test_release_gate_campaign.py::test_the_measured_repo_still_reports_what_this_phase_measured` fails, and nothing in this repository caused it. It asserts `len(gate["blocking"]) >= 40` against `~/Dev/repos/your-trainer/docs`. Edwin has walked that release: the gate reports **3**.

```
E       AssertionError: 3
E       assert 3 >= 40
```

The assertion succeeds while a release is unwalked and fails once it has been walked — so it is red exactly when the work it describes has gone well, and it will be red from now until somebody adds forty checks to another repository.

### Two more of the same shape, found the same day

`tests/test_gate_delta.py` fails twice on the same premise, and both are about *chronic* rows — checks that have been blocking across several releases:

```
test_chronic_rows_carry_the_tag_they_have_been_open_since
    assert since, "the corpus has chronic rows"        # []
test_the_oldest_chronic_row_carries_its_release_count
    max(chronic, key=...)                              # ValueError: empty
```

Edwin cleared the last of them during the session that found this. The second does not even fail on an assertion — it raises `ValueError` out of `max()` on an empty list, which is the same premise one step less defended.

So this is a family of three, not one test: **an assertion that another repository still owes work.** Each is red precisely because the work got done.

## Not caused by the fixes filed beside it

Verified by stashing the change and re-running: all three fail identically with `src/project_os_cockpit/acceptance.py` and `ledger.py` at `HEAD`. [[ISS-0281]]'s fix cannot lower a blocking count — it moves checks from `todo` to `fail`, and both block.

## Why it is worth filing rather than fixing here

The intent is sound and is stated in the test's own docstring: *"the numbers PHASE-034 stands on, re-taken rather than re-asserted"*. A measurement re-taken against a live corpus is better than one copied into a note. But the threshold is a floor under someone else's backlog, and the same file's other assertions may have the same shape.

Three readings, and the choice is Edwin's:

1. Assert the **shape** rather than the size — the gate exists, it is blocked or not, and its rows carry an area and a reason — so the test survives the corpus being worked.
2. Move the pinned figure into the phase note as a dated measurement, where a number that was true on a date belongs, and delete the assertion.
3. Skip when the measured repo's suite has moved on, which keeps the number and stops the red.

## What was done

Edwin, 2026-09-06: *"I don't care when they were introduced tests need to run green."* So all three were fixed rather than parked, and reading 1 was taken — assert the property, not the size — with the corpus-dependent half moved onto fixtures.

**`test_gate_delta.py`, the two chronic tests.** The arithmetic they protected — a row already open at the oldest tag is dated to *that* tag, not a later one it was also open at, and its release count is the number of tags cut after it — now runs on a three-tag fixture repository, so it holds whatever any other repository owes. A second fixture test carries the half that makes the first mean something: a row present at no tag gets **no** date rather than the oldest one. A new `_repo_with_tags` helper generalises the file's existing single-tag `_repo_with_tag`, with `--allow-empty` commits, because a tag cut over an unchanged suite is exactly the case a chronic row is about. The live-corpus test stays as a **consistency** check — whatever chronic rows exist today name a real tag and agree with history — and asserts nothing when there are none. `test_the_oldest_chronic_row_carries_its_release_count` skips on an empty list instead of raising out of `max()`.

**`test_release_gate_campaign.py`.** The `>= 40` floor is gone. Kept: every blocking row names its subject (0 of 60 did before [[ISS-0173]]), and a new consistency assertion that `blocked` agrees with the rows carried. The size floor moved onto the **suite** — blocking plus settled — which only grows, so it still catches a loader that has broken while never failing because a release was walked.

The file's own docstring already stated this rule: *"The shapes … are pinned on fixtures, because they must hold whatever the fleet looks like next month."* These three were the exceptions to it.

## Next Actions

- [x] Fix all three: property on fixtures, consistency against the live corpus, no floor under another repo's backlog.
- [ ] The rest of the `@needs_trainer` population has not been audited for the same shape. Worth one pass; nothing is red today.
