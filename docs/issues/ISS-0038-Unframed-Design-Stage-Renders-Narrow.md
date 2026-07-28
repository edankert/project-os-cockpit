---
type: "[[issue]]"
id: ISS-0038
aliases: ["ISS-0038"]
title: "An unframed design renders as a narrow column instead of filling the pane"
status: fixed
severity: medium
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["user report 2026-07-28 while reviewing the design surface"]
related: ["[[FEAT-0042-Design-Bench]]", "[[FEAT-0043-Design-Top-Level-Surface]]"]
fixed_by: []
---

# An unframed design renders narrow

## What Edwin saw

Selecting **Working copy** alone showed the artifact "as a very small column in the middle of the screen" instead of at full width.

## Mechanism

`.design-body` is a flex container. Outside compare mode `.design-stage` is a plain flex item — `flex: 0 1 auto` — so its width comes from its content, the iframe. The iframe carries `width: 100%`, which resolves against the stage. Circular: with no definite basis anywhere, the iframe falls back to its **intrinsic 300px default**.

Measured in a minimal repro at a 1000px body: **302px before, 1000px after.**

Compare mode was never affected because `.is-compare .design-stage` sets `flex: 1 1 0`, giving the stage a definite basis. That rule is the tell — the same bug was hit and fixed in compare mode only, and the single-frame path was left as it was.

## Fix

`.design-body > .design-stage:not(.is-framed) { flex: 1 1 auto; min-width: 0; }`

`:not(.is-framed)` is deliberate. A framed stage's width *is* the declared viewport (900px, a phone width); stretching it would defeat the framing the viewport presets exist to provide. Only the document case — `viewport:` absent, meaning "let it scroll" — fills the pane.

## Why it survived the tests

Every design-bench test asserts payloads and source text. Nothing measures a rendered box, so a layout defect was invisible to all 81 of them. `desktop/harness/` can load the real bundle in a browser and is the place a regression test for this would go — noted rather than done, since the harness has no design page yet.
