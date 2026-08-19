---
type: "[[requirement]]"
id: REQ-0059
aliases: ["REQ-0059"]
title: "A check's section is derived from what it covers and who executes it, never filed"
status: draft
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
source: ["[[ADR-0039-Three-Sections-Derived-Not-Filed]]"]
priority: high
scope: "Every acceptance check in every front door — 671 notes fleet-wide."
acceptance: ["`tier:` is read by no code path", "Both front doors compute the same section for the same note"]
implements: "[[FEAT-0140-Sections-Are-Derived-Not-Filed]]"
verifies: []
related: ["[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[ISS-0208-Retire-The-Tier-Rule]]"]
tests: []
---

# A section is derived, never filed

## Statement

The section a check appears under **must** be computed: `command:` non-empty is *Automated tests*; otherwise `covers:` naming an `ISS-*` is *Regression tests*; otherwise *Feature tests*. No note field selects a section, and `tier:` **must not** be read.

## Acceptance Criteria

- [ ] One predicate, called by both front doors — a second implementation is how they come to disagree
- [ ] `GATING_TIERS`, `PERMANENT_TIERS` and `TIER_LABELS` are deleted
- [ ] A check gaining a `command:` moves section with no other edit; losing it moves back
- [ ] Order is total and stable: a check falls in exactly one section, asserted

## Notes

Precedence matters and is stated deliberately: `command:` wins over `covers:`, so an automated regression check is *Automated tests* — Edwin, *"it doesn't matter why they were automated"*.
