---
type: "[[task]]"
id: TASK-0311
aliases: ["TASK-0311"]
title: "The design-gate convention proposed to project-os"
status: done
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0070-Design-Gating-And-Scaffolding]]"]
parent: "[[FEAT-0070-Design-Gating-And-Scaffolding]]"
effort: S
depends: ["[[TASK-0309]]"]
blocks: []
related: []
tests: []
---

# The design-gate convention proposed to project-os

## Definition of Done

- The proposal note files `design:`, the gate, and the derive-by-dispatch discipline upstream — the close-out-rule route, with this repo's experience as evidence.

## Done — 2026-08-11

The convention is documented in `TAXONOMY.md` alongside `acceptance:`, both marked as **local divergence ahead of upstream**, with the reasoning that carries them home:

- `design:` on a feature, and `DESIGN-GATE` as a **warning** — the judgment being gated cannot be automated, so a blocking gate gets cleared to unblock the build.
- The satisfied set is `accepted`/`implemented`/`superseded`, **not** `accepted` alone. This is the part worth taking upstream: the obvious rule fires false positives on any repo whose designs have progressed, and it did so five times here within a minute of being written.
- Derive-by-dispatch: the tool composes the prompt and an agent does the work, so no requirement text exists that nobody asked for.

Filed here rather than as a separate note because `tools/instructions/` is template-owned: the divergence note *is* the proposal, and a sync will surface it as a deliberate edit rather than as drift. That is the close-out-rule route this project already used for the "file what the validator reports and you cannot fix" rule.
