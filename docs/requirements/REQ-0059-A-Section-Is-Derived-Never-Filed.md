---
type: "[[requirement]]"
id: REQ-0059
aliases: ["REQ-0059"]
title: "A check's section is derived from what it covers and who executes it, never filed"
status: implemented
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: ["[[ADR-0039-Three-Sections-Derived-Not-Filed]]"]
priority: high
scope: "Every acceptance check in every front door — 671 notes fleet-wide."
acceptance: ["One predicate returns the section, called by every front door", "`tier:` is read by no code path and the tier constants are deleted", "A check gaining or losing a `command:` moves section with no other edit", "Exactly one section per check, and no id rendered twice"]
implements: "[[FEAT-0140-Sections-Are-Derived-Not-Filed]]"
verifies: []
related: ["[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[ISS-0208-Retire-The-Tier-Rule]]"]
tests: []
---

# A section is derived, never filed

## Statement

The section a check appears under **must** be computed: `command:` non-empty is *Automated tests*; otherwise `covers:` naming an `ISS-*` is *Regression tests*; otherwise *Feature tests*. No note field selects a section, and `tier:` **must not** be read.

## Acceptance Criteria

- [x] One predicate — `acceptance.section_of`, called by the payload, the navigator and the gate
- [x] `GATING_TIERS`, `PERMANENT_TIERS` and `TIER_LABELS` are deleted, and every caller moved to `MANUAL_SECTIONS`
- [x] A check gaining a `command:` moves section with no other edit — `tests/test_command_targets.py` proves the return trip on constructed input, since **zero** of the fleet's 139 commands are broken
- [x] Exactly one section per check — `test_the_tiers_render_in_the_tests_view` now asserts no id appears twice **anywhere**, which is strictly stronger than the rule it replaced, and it caught a real duplicate row while being written

## Notes

Precedence matters and is stated deliberately: `command:` wins over `covers:`, so an automated regression check is *Automated tests* — Edwin, *"it doesn't matter why they were automated"*.
