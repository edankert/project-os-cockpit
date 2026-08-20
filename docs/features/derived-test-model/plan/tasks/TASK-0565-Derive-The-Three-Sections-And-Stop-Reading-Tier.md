---
type: "[[task]]"
id: TASK-0565
aliases: ["TASK-0565"]
title: "Derive the three sections and stop reading `tier:`"
status: done
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: []
parent: "[[FEAT-0140-Sections-Are-Derived-Not-Filed]]"
effort: "M"
due: ""
depends: []
blocks: []
related: []
tests: []
---

# Derive the three sections and stop reading `tier:`

## Definition of Done
- [ ] One predicate returns the section for a note
- [ ] `GATING_TIERS`, `PERMANENT_TIERS` and `TIER_LABELS` are deleted
- [ ] `tier:` appears in no read path
- [ ] Exactly one section per check, asserted

## Steps
- [ ] Write the predicate: `command:` wins, then `covers:` naming an `ISS-*`, else Feature tests
- [ ] Replace the tier grouping in `acceptance.py`'s payload and in `_acceptance_tier_groups`
- [ ] Replace `blocking_for`'s tier test with: an unsettled manual check blocks

## Notes

Precedence is deliberate — an automated regression check is *Automated tests*, because Edwin's question was *does a machine do this* and there is one answer.

The existing `test_every_test_appears_in_exactly_one_group` guard is the model for the one-section assertion. *(This line named it `test_exactly_one_group_per_test` — a test that has never existed; the same phantom was cited in `cockpit.py` and [[FEAT-0128]]. Corrected 2026-08-20.)*
