---
type: "[[task]]"
id: TASK-0371
aliases: ["TASK-0371"]
title: "A Tests view listing every test in the corpus, with its manual-run obligation"
status: backlog
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[FEAT-0086-Tests-Becomes-A-View]]"]
parent: "[[FEAT-0086-Tests-Becomes-A-View]]"
effort: M
due: ""
depends: ["[[TASK-0369-The-Obligation-Registry]]"]
blocks: ["[[TASK-0372-The-Runner-Moves]]", "[[TASK-0373-The-Tier-Suite-And-The-Release-Gate]]"]
related: ["[[FEAT-0018-Verification-Health-Surface]]"]
tests: []
---

# The Tests view and its register

## Definition of Done
- [ ] A Tests view lists every `TST-*`, grouped so what is verified and what is not is legible at a glance
- [ ] Both storage locations appear — feature-scoped `plan/tests/` and system-wide `docs/tests/` — without the split leaking into the reader's mental model
- [ ] `test @ ready` and manual is the view's obligation, from the registry, with the badge
- [ ] Staleness uses the project's existing threshold and config source, not a second one

## Steps
- [ ] Add the view and its nav mode; reuse `_tests_register`, which already reads the whole corpus
- [ ] Group by verification state first, then by owning feature
- [ ] Point the overview's Tests stat tile here instead of `~review`

## Notes
23 tests across 16 feature directories plus `docs/tests/`, and until now no surface that simply shows them. The register already exists on the desk and moves whole.

Inventing a parallel staleness rule is [[ISS-0024]]/[[ISS-0069]]; use the configured threshold.
