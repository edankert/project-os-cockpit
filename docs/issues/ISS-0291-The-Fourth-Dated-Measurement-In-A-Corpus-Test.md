---
type: "[[issue]]"
id: ISS-0291
aliases: ["ISS-0291"]
title: "A corpus test pinned the baseline tag as a literal, so it went red the day your-trainer shipped v2.1.8 — the fourth time a dated measurement has been written into an assertion about a live repo"
status: fixed
phase: ""
owner: user:edwin
created: 2026-09-08
updated: 2026-09-08
source: ["Found 2026-09-08 running the full suite while fixing ISS-0288; Edwin: 'fix the stale test'"]
severity: medium
component: tests
parent: ""
related: ["[[ISS-0283-A-Test-Pins-Another-Repos-Blocking-Count]]", "[[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]]"]
tests: []
---

# The docstring said not to, three lines above the line that did

## Problem

`test_the_delta_against_your_trainers_real_tags` asserted `delta["baseline"] == "v2.1.6"`. `../your-trainer` shipped v2.1.8 on 2026-09-07, the baseline moved with it, and the test went red — **a passing test turning red because the corpus it watches moved forward correctly**, which is the worst available failure signal.

Its own docstring names the rule it broke:

> Asserted as invariants, not as absolute counts, and that is a lesson paid for three times in one session. […] A test pinning "60 blocking" fails the moment the tool it is testing is used successfully.

[[ISS-0283-A-Test-Pins-Another-Repos-Blocking-Count]] fixed three assertions of this class. This is the fourth, and it survived because it is not a count — it is a tag — so it did not look like the thing that was being swept up.

## Fix

The expectation is derived from the corpus instead of typed: the newest `released` note's version, read out of frontmatter, and the baseline must be that version's tag.

**Deliberately not `baseline_ref`.** A test that calls the function it is checking asserts nothing. The test walks the release notes the long way round; the code under test matches versions against real git tags. Two routes to one answer is what makes the assertion worth having.

## Adequacy

Verified by breaking it: `baseline_ref` made to return the oldest tag instead of the newest shipped release fails the test with *"the baseline is the newest released tag, which is now v2.1.8"*. Restored, `tests/test_gate_delta.py` is 32 passed, 1 skipped.
