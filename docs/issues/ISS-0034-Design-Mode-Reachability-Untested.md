---
type: "[[issue]]"
id: ISS-0034
aliases: ["ISS-0034"]
title: "Nothing tests that the design mode reaches the design surface — two mutations survive"
status: fixed
severity: high
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["independent review 2026-07-28 (FEAT-0043)"]
related: ["[[TASK-0224-Design-Mode-In-The-Strip]]", "[[FEAT-0043-Design-Top-Level-Surface]]"]
fixed_by: []
---

# The mode's reachability is unguarded

## What the review demonstrated

Two mutations, each making the design mode permanently unreachable by click, leave all 70 tests in `tests/test_design_bench.py` green:

1. Invert the guard to `if (currentRel && currentRel.startsWith('~design'))` → 70 passed.
2. Delete the `navigateTo('~design', { replace: false })` call, keeping the branch and its comments → 70 passed.

The three tests that look like coverage are source-greps that both mutants satisfy. `test_the_mode_has_a_button_an_icon_and_a_server_that_serves_it` asserts the button, the icon and the server mode — three *endpoints* of the path, never the wire between them — while its docstring claims "this asserts the whole path". Writing a stronger claim in a docstring than the assertions carry is the ISS-0024 pattern again, in a test rather than a guard.

## Why it matters

The route as written is correct. Being correct today is not the property that was needed: the design bench shipped unreachable twice with passing tests, and this task existed to end that. An unguarded route is exactly the state that allowed it both times.

## Fix direction

Assert the wire, not the endpoints: the guard's polarity (a design-mode selection with no `~design` page open must navigate) and the presence of the navigation, in a form a mutation would break. A grep for a comment is not coverage.

## Resolution (2026-07-28)

Three tests added that fail against the exact mutations the review demonstrated, re-run to confirm:

| Mutation | Before | After |
|---|---|---|
| Invert the guard to `if (currentRel && currentRel.startsWith('~design'))` | 70 passed | **1 failed**, 73 passed |
| Delete the `navigateTo('~design')` call, keep the branch | 70 passed | **1 failed**, 73 passed |

`test_the_guard_polarity_is_the_one_that_navigates` extracts the guard *expression* around the navigation and asserts it is the negated form — which a grep for `startsWith` could not distinguish. `test_the_branch_actually_navigates` asserts the call itself. `test_the_route_the_mode_navigates_to_is_one_the_router_handles` checks the target string against the router's own literal and against `extractRel`, which had already discarded `~design/...` once.

The overclaiming docstring on `test_the_mode_has_a_button_an_icon_and_a_server_that_serves_it` was the real defect — it said "this asserts the whole path" while asserting three endpoints. That is ISS-0024's pattern (a guard describing itself more widely than it checks) relocated into a test, where it is worse: a guard that overclaims still guards something, while a test that overclaims is read as coverage that does not exist.
