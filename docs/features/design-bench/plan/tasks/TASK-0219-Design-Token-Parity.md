---
type: "[[task]]"
id: TASK-0219
aliases: ["TASK-0219"]
title: "Scoped palette parity — a design's status colours must match statuses.py"
status: backlog
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
source: ["[[ISS-0023-Status-Vocabulary-Drift]]"]
parent: "[[FEAT-0042-Design-Bench]]"
effort: "M"
depends: ["[[TASK-0214]]", "[[TASK-0221]]"]
blocks: []
related: ["[[TST-0019-Status-Vocabulary-Parity]]", "[[ISS-0023-Status-Vocabulary-Drift]]"]
tests: []
---

# Scoped palette parity

## Definition of Done

- [ ] Scope is the **status/severity palette only** — not spacing, not type scale, not chrome
- [ ] The design declares its palette using the implementation's token names, or a mapping declared once in its `## Tokens` section
- [ ] A test asserts the design's palette matches the `statuses.py`-derived palette, in the shape of [[TST-0019]]
- [ ] The **direction of authority is written down**: for the status palette, `statuses.py` is upstream and a design that disagrees is wrong
- [ ] The test **fails when a token is changed in the implementation and not the design**, verified by inversion — a test that cannot fail does not guard
- [ ] A token declared in the design and used nowhere is reported, so the design does not accumulate fiction
- [ ] Extraction reads CSS custom properties; the only hand-maintained artifact is the per-design name mapping, and a design using implementation names verbatim needs none

## Steps

- [ ] Choose the declaration format (CSS custom properties in the artifact are the obvious candidate — the design already has to define them to render)
- [ ] Extract from both sides and compare
- [ ] Write the parity test with inversion coverage in both directions
- [ ] Run it against DES-0001's dossier and the current implementation, and record what it finds

## Notes

An earlier version of this note claimed this task justified building a design surface here at all. Independent review refuted that (see [[FEAT-0042]]), and the claim is withdrawn: the vocabularies in the founding artifact do not correspond, and the direction of authority was contradicted between this note and [[DES-0001]]'s Maintenance section on the same day.

What remains is a real, narrow check, and the precedent for *it* is exact. `base.css` and `cockpit.css` both restated the status palette, they drifted, and the corpus rendered a wrong colour for weeks — [[ISS-0023]], which produced [[TST-0019]]'s parity suite and the `statuses.py` single source.

A design token declared in a dossier and re-typed into a stylesheet is the same failure with the same remedy. The interesting part is that the design becomes the upstream side of the parity check rather than another surface that drifts.

Expect the first run against DES-0001 to find divergence — the dossier predates the implementation and the implementation moved. With the arrow now written down (`statuses.py` upstream), that divergence means **the dossier is stale**, which is an actionable finding rather than an ambiguous one. A check whose failures are routinely legitimate accumulates waivers; this one has a right answer.
