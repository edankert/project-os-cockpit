---
type: "[[feature]]"
id: FEAT-0070
aliases: ["FEAT-0070"]
title: "An accepted design gates the feature that names it, and can scaffold that feature's requirements — by dispatch, never by fiat"
status: planned
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[DES-0007-The-Bench-Closes-The-Loop]]"]
goal: "Features gain optional `design:`; the local DESIGN-GATE validator rule holds a feature in the pending band while its design is unaccepted (warning first, ADR-0011's path); Derive-requirements on an accepted design dispatches the scaffold skills; the convention is proposed upstream."
requirements: []
tasks:
  - "[[TASK-0309-The-Design-Gate]]"
  - "[[TASK-0310-Derive-Requirements-By-Dispatch]]"
  - "[[TASK-0311-The-Upstream-Proposal]]"
release: ""
related: ["[[FEAT-0059-The-Write-Service-Widens]]"]
tests: []
---

# Design gating and scaffolding

## Goal

Design-up-front becomes enforceable instead of aspirational, by the same route every local rule has taken: this repo's validator first, the upstream proposal alongside. Scaffolding preserves the split PHASE-023 encodes everywhere — an agent drafts REQs citing the design's decisions, they arrive `draft`, the human approves through the actuator row.

## Out of Scope

- Retrofitting existing features. The gate applies where `design:` is present; history is not re-litigated.
- Upstream adoption itself — that is upstream's decision; the proposal is this feature's deliverable.
