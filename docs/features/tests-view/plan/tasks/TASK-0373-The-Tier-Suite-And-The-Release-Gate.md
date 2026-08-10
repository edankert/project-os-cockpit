---
type: "[[task]]"
id: TASK-0373
aliases: ["TASK-0373"]
title: "The Tier 1/2/3 suite is instantiated for this repo and an unchecked Tier 1 test blocks a release note"
status: done
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[FEAT-0086-Tests-Becomes-A-View]]"]
parent: "[[FEAT-0086-Tests-Becomes-A-View]]"
effort: L
due: ""
depends: ["[[TASK-0371-The-Tests-View-And-Its-Register]]"]
blocks: []
related: ["[[FEAT-0072-The-Release-Surface]]", "[[TASK-0317-The-Gate-Band]]", "[[FEAT-0064-The-Acceptance-Gate]]", "[[REL-0001-The-Human-Has-Levers]]"]
tests: []
---

# The tier suite and the release gate

## Definition of Done
- [x] An acceptance-tests instance exists for this repo, from the template, with Tier 1 populated — `docs/tests/ACCEPTANCE_TESTS.md`, **27 Tier 1 items across 14 areas**, every one naming the features it covers (`test_this_repo_has_a_suite_with_tier_one_populated`)
- [x] Tests carry their tier, and the view renders by tier — three tier groups beneath the test-note groups, kept as a separate population (`test_the_tiers_render_in_the_tests_view`)
- [x] A release note lists its unchecked Tier 1/2 tests as a blocking band, in the template's own wording — `mountReleaseGate`, with the rule sent by the server rather than restated (`test_the_gate_states_the_contracts_own_rule`)
- [x] **The gate fires** — and it is firing on [[REL-0001]] right now, on the live suite, not a fixture (`test_the_gate_fires_on_this_repo_right_now`)
- [x] Tier 2 tests reference the `ISS-*` that created them, per the contract — 7 of 7 (`test_every_tier_two_item_names_the_issue_that_created_it`), and every id the suite names resolves in the corpus (`test_every_id_the_suite_names_exists`)

## Steps
- [x] Instantiate `docs/__templates__/acceptance-tests.md`; classify the existing 23 tests
- [x] Decide how tier is carried — a frontmatter field on the `TST-*` or membership in the suite document — and record why
- [x] Render the gate band on the release note
- [x] Prove the gate with a deliberately unchecked test, then restore

## Notes
The contract has existed since the template was written — Tier 1/2/3, the re-run rule, *"a release is blocked while any Tier 1/2 test is unchecked"* — and **no repo has ever instantiated it**. 85 features, 23 tests, zero tier classification. This is the task that makes the gate real, and it is `L` because classifying is judgment, not typing.

Coordinate with [[FEAT-0064]]: the acceptance gate is per-feature (`acceptance: requested`), this is per-release. Two gates, different scopes, and they must not be conflated into one field.

## Done 2026-08-10

### The step that was wrong: "classify the existing 23 tests"

The step assumed the `TST-*` notes are the things that get tiered. They are not, and following it would have produced a broken suite.

Measured: **22 of this repo's 23 test notes are automated pytest modules** that CI runs on every commit. Tier 1 is *"one or more per feature, verifying core user-facing capabilities"*; Tier 2 *"guards previously-broken behavior"*. `TESTING.md` is explicit that the two systems coexist — *"`TST-*` notes for formal test tracking, `ACCEPTANCE_TESTS.md` for the release checklist"* — and the gate reads the **checkbox**, which a note has nowhere to put.

Tiering the notes would also have made the gate meaningless in the other direction: 23 of 23 are `passing`, so a suite built from them would have been fully checked on the day it was created and the gate would have reported clear having verified nothing.

**So tier lives in the suite document, and the suite is authored from the surfaces.** 27 Tier 1 items across 14 areas — the render server, the shell, the navigator, the note page, the overview, design, tests, capture, the terminal, agents, health, history, close-out, obligations — each naming the `FEAT-*` ids it covers. 7 Tier 2 items, each naming the `ISS-*` that created it. 2 Tier 3, for what landed today.

That is the decision the step asked for, recorded in the suite itself and in `acceptance.py`'s module docstring, because a `tier:` frontmatter field is what the next reader will think of first.

### Every box is unchecked, and that is the point

Nothing in the suite has been walked. So the gate is **blocking [[REL-0001]] right now** — 34 unchecked Tier 1/2 items — which is the first time in this project's history that the release gate has been able to say anything at all.

`test_the_gate_fires_on_this_repo_right_now` asserts against the live suite rather than a fixture, deliberately. A fixture proves the code works; the live assertion proves the *project* is gated. If someone walks all 34, that test starts passing for the right reason and the note about it is here.

The DoD's "prove the gate with a deliberately unchecked test, then restore" is `test_an_unchecked_tier_one_test_blocks_and_checking_it_clears` — the same fixture with one box flipped, blocked then clear.

### Absent is not passing — the assertion the task turns on

A repo with no suite has no Tier 1/2 items, so `blocking()` is empty and any naive gate reports **clear**. That was every repo's state until today: a green light nobody earned, indistinguishable from a walked checklist.

So `gate_payload` reports `exists` alongside `blocked`, and the band has **three** states — blocked, clear, and *"no acceptance suite in this repo — the gate cannot be evaluated"*. `test_a_repo_with_no_suite_is_unknown_not_clear` asserts both the payload and the ordering in the renderer, because deciding `blocked` before `exists` would collapse the third state back into the second.

This is also the one thing [[TASK-0317]]'s DoD would have missed — it specified two states — so that task is closed here rather than duplicated.

### Two populations in one view

The Tests view now carries test notes *and* suite checkboxes. They are separate groups, and `test_the_tiers_render_in_the_tests_view` asserts no id appears in both. [[ISS-0068]] forbids one item having two homes; it does not forbid two populations sharing a surface, and merging these would put an automated contract test beside *"click each stat tile"* as though a person owed both.

Only the gating tiers carry `needs_human`. Tier 3 never does — `TESTING.md`: *"Tier 3 tests do not gate releases (they are verification aids, not requirements)."*

### Verification

`910 passed, 2 skipped`; `validate-docs: OK`; desktop `tsc --noEmit` clean and `dist/` rebuilt. Twelve new assertions.

Adequacy by mutation, each applied and reverted:

| mutation | killed by |
|---|---|
| `GATING_TIERS = (1, 2, 3)` | `test_tier_three_never_gates` + 3 others |
| every checkbox parses as checked | `test_the_gate_fires_on_this_repo_right_now` |
| a missing suite reports `exists=True` | `test_a_repo_with_no_suite_is_unknown_not_clear` |
| drop the "nothing above the first tier heading" guard | `test_nothing_above_the_first_tier_heading_is_a_test` |

The last of those **survived on the first attempt**, and the fixture was the reason: its preamble had a numbered list and prose, neither of which matches the checkbox pattern, so the guard was never exercised and the test passed either way. The fixture now carries a checkbox above the first tier heading — the case that would otherwise become an unchecked Tier 0 item and block every release forever on the strength of the rules text.

That is the second test of mine this feature's mutation pass has caught before the code. Both were the same shape: a case written to describe the guard rather than to trip it.

### Not verified: the pixels, again

The band and the tier groups are asserted through their payloads and their source. Nobody has looked at either. That is filed as Tier 3 §3.1 in the suite this task created — which is the first time in this project that "somebody still has to look at this" has had a place to live that a release gate reads.
