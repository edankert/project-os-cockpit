---
type: "[[task]]"
id: TASK-0219
aliases: ["TASK-0219"]
title: "Design tokens checked against the implementation's CSS"
status: backlog
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
source: ["[[ISS-0023-Status-Vocabulary-Drift]]"]
parent: "[[FEAT-0042-Design-Bench]]"
effort: "M"
depends: ["[[TASK-0214]]"]
blocks: []
related: ["[[TST-0019-Status-Vocabulary-Parity]]", "[[ISS-0023-Status-Vocabulary-Drift]]"]
tests: []
---

# Design token parity

## Definition of Done

- [ ] A design note declares its tokens (colour, spacing, type scale) in one place, as data rather than prose
- [ ] A test asserts the implementation's CSS matches the declared tokens, in the shape of [[TST-0019]]
- [ ] The test **fails when a token is changed in the implementation and not the design**, verified by inversion — a test that cannot fail does not guard
- [ ] A token declared in the design and used nowhere is reported, so the design does not accumulate fiction
- [ ] Token extraction reads CSS custom properties, not hand-maintained lists

## Steps

- [ ] Choose the declaration format (CSS custom properties in the artifact are the obvious candidate — the design already has to define them to render)
- [ ] Extract from both sides and compare
- [ ] Write the parity test with inversion coverage in both directions
- [ ] Run it against DES-0001's dossier and the current implementation, and record what it finds

## Notes

This is the task that justifies building a design surface *here* rather than using an external tool, and the precedent is exact. `base.css` and `cockpit.css` both restated the status palette, they drifted, and the corpus rendered a wrong colour for weeks — [[ISS-0023]], which produced [[TST-0019]]'s parity suite and the `statuses.py` single source.

A design token declared in a dossier and re-typed into a stylesheet is the same failure with the same remedy. The interesting part is that the design becomes the upstream side of the parity check rather than another surface that drifts.

Expect the first run against DES-0001 to find real divergence. The dossier was authored before the implementation and the implementation moved; that is data, not a bug in the check.
