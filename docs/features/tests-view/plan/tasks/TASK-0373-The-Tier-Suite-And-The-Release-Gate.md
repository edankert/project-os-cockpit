---
type: "[[task]]"
id: TASK-0373
aliases: ["TASK-0373"]
title: "The Tier 1/2/3 suite is instantiated for this repo and an unchecked Tier 1 test blocks a release note"
status: backlog
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
related: ["[[FEAT-0072-The-Release-Surface]]", "[[FEAT-0064-The-Acceptance-Gate]]"]
tests: []
---

# The tier suite and the release gate

## Definition of Done
- [ ] An acceptance-tests instance exists for this repo, from the template, with Tier 1 populated
- [ ] Tests carry their tier, and the view renders by tier
- [ ] A release note lists its unchecked Tier 1/2 tests as a blocking band, in the template's own wording
- [ ] **The gate fires** — an unchecked Tier 1 test demonstrably blocks a draft release note
- [ ] Tier 2 tests reference the `ISS-*` that created them, per the contract

## Steps
- [ ] Instantiate `docs/__templates__/acceptance-tests.md`; classify the existing 23 tests
- [ ] Decide how tier is carried — a frontmatter field on the `TST-*` or membership in the suite document — and record why
- [ ] Render the gate band on the release note
- [ ] Prove the gate with a deliberately unchecked test, then restore

## Notes
The contract has existed since the template was written — Tier 1/2/3, the re-run rule, *"a release is blocked while any Tier 1/2 test is unchecked"* — and **no repo has ever instantiated it**. 85 features, 23 tests, zero tier classification. This is the task that makes the gate real, and it is `L` because classifying is judgment, not typing.

Coordinate with [[FEAT-0064]]: the acceptance gate is per-feature (`acceptance: requested`), this is per-release. Two gates, different scopes, and they must not be conflated into one field.
