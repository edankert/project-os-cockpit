---
type: "[[issue]]"
id: ISS-0283
aliases: ["ISS-0283"]
title: "Three tests pin ../your-trainer's outstanding work — a blocking count of 40 or more and the existence of chronic rows — so walking the release down turns the suite red; the assertions measure how much is left in another repo, not this code"
status: triage
phase: "[[PHASE-999-Future]]"
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

## Next Actions

- [ ] Edwin picks a reading, and it applies to all three. The same walk should check the rest of `test_release_gate_campaign.py` and `test_gate_delta.py` for other assertions pinned to `your-trainer`'s size — `@needs_trainer` marks the population to look at.
