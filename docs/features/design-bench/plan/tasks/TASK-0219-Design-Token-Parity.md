---
type: "[[task]]"
id: TASK-0219
aliases: ["TASK-0219"]
title: "Scoped palette parity — a design's status colours must match statuses.py"
status: done
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

- [x] Scope is the **status/severity palette only** — not spacing, not type scale, not chrome — evidence: `SCOPED_PREFIXES = ("--status-", "--severity-")`; `test_only_scoped_families_are_read` asserts an accent is out of scope
- [x] The design declares its palette using the implementation's token names, or a mapping declared once in its `## Tokens` section — evidence: the authoring contract ([[TASK-0221]]) requires verbatim names or a declared mapping
- [x] A test asserts the design's palette matches the `statuses.py`-derived palette, in the shape of [[TST-0019]] — evidence: `tests/test_design_tokens.py`, 10 tests
- [x] The **direction of authority is written down**: for the status palette, `statuses.py` is upstream and a design that disagrees is wrong — evidence: module docstring and `## Conformance` in [[DES-0002]] — the implementation is upstream; a disagreeing design is wrong
- [x] The test **fails when a token is changed in the implementation and not the design**, verified by inversion — a test that cannot fail does not guard — evidence: `test_a_drifted_value_is_caught` on a one-digit change; `test_a_different_colour_space_IS_reported`
- [x] A token declared in the design and used nowhere is reported, so the design does not accumulate fiction — evidence: reported as `unknown`, not `diverged` — a design proposing a new status is legitimate
- [x] Extraction reads CSS custom properties; the only hand-maintained artifact is the per-design name mapping, and a design using implementation names verbatim needs none — evidence: `read_tokens`, first-declaration-wins so light and dark schemes are not crossed

## Steps

- [x] Choose the declaration format (CSS custom properties in the artifact are the obvious candidate — the design already has to define them to render)
- [x] Extract from both sides and compare
- [x] Write the parity test with inversion coverage in both directions
- [x] Run it against DES-0001's dossier and the current implementation, and record what it finds

## Result

**Silent on the only artifact in the repo, and that is the honest outcome.** DES-0001 declares `--m-*` / `--t-*`, not `--status-*`, so the check finds nothing to compare — exactly what the review predicted. A test records that as a *fact* rather than dressing it up as a pass, and says what to change when a design does declare scoped tokens.

So the check is proven by inversion rather than by a live finding: a one-digit drift is caught, a different colour space is caught (deliberately — hex against hsl means one was retyped from the other), whitespace is not, and a token the implementation lacks is reported as `unknown` rather than `diverged`, because a design proposing a *new* status is a legitimate thing for a design to do.

**First-declaration-wins is load-bearing.** A stylesheet declares each token once per scheme, and taking the last would compare a design's light palette against the implementation's dark one. That exact bug shipped in the family-palette check earlier the same day and reported a divergence that did not exist; anyone following it would have "fixed" three apps to the wrong value.

## Notes

An earlier version of this note claimed this task justified building a design surface here at all. Independent review refuted that (see [[FEAT-0042]]), and the claim is withdrawn: the vocabularies in the founding artifact do not correspond, and the direction of authority was contradicted between this note and [[DES-0001]]'s Maintenance section on the same day.

What remains is a real, narrow check, and the precedent for *it* is exact. `base.css` and `cockpit.css` both restated the status palette, they drifted, and the corpus rendered a wrong colour for weeks — [[ISS-0023]], which produced [[TST-0019]]'s parity suite and the `statuses.py` single source.

A design token declared in a dossier and re-typed into a stylesheet is the same failure with the same remedy. The interesting part is that the design becomes the upstream side of the parity check rather than another surface that drifts.

Expect the first run against DES-0001 to find divergence — the dossier predates the implementation and the implementation moved. With the arrow now written down (`statuses.py` upstream), that divergence means **the dossier is stale**, which is an actionable finding rather than an ambiguous one. A check whose failures are routinely legitimate accumulates waivers; this one has a right answer.
