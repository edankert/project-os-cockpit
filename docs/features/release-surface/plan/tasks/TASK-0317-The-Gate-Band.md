---
type: "[[task]]"
id: TASK-0317
aliases: ["TASK-0317"]
title: "The acceptance-tests release gate finally renders"
status: done
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-10
source: ["[[FEAT-0072-The-Release-Surface]]"]
parent: "[[FEAT-0072-The-Release-Surface]]"
effort: S
depends: ["[[TASK-0315]]"]
blocks: []
related: ["[[TASK-0373-The-Tier-Suite-And-The-Release-Gate]]", "[[FEAT-0086-Tests-Becomes-A-View]]"]
tests: []
---

# The acceptance-tests release gate finally renders

## Definition of Done

- A REL note's view lists unchecked Tier 1/2 boxes from the acceptance suite with the template's own words as a warning band; checked suites render one quiet line.

## Done 2026-08-10 — by [[TASK-0373]], which needed the same band

[[FEAT-0086]] had to make the gate **fire**, and a gate that fires with nowhere to say so is not a gate. So the band was built there: `mountReleaseGate` renders on any `release` note, listing every unchecked Tier 1/2 item and stating the rule in the contract's own words (sent by the server from `acceptance.gate_payload`, so nothing paraphrases it).

Three states, not two — and the third is the one this task's DoD would have missed. *"Checked suites render one quiet line"* covers clear and blocked; it does not cover **no suite at all**, which was every repo's situation until today. An absent suite has no Tier 1/2 items, so a naive gate reports "clear": a green light nobody earned. The band says *"the gate cannot be evaluated"* instead, and `test_a_repo_with_no_suite_is_unknown_not_clear` pins the ordering that keeps it that way.

Marked `done` rather than `superseded`: the work described here exists and behaves as specified. [[FEAT-0072]]'s other two tasks — the UNRELEASED card and Draft-release — are untouched and still `backlog`.
