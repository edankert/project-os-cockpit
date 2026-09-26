---
type: "[[task]]"
id: TASK-0310
aliases: ["TASK-0310"]
title: "An accepted design drafts its requirements — through an agent, never by fiat"
status: done
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0070-Design-Gating-And-Scaffolding]]"]
parent: "[[FEAT-0070-Design-Gating-And-Scaffolding]]"
effort: M
depends: ["[[TASK-0309]]"]
blocks: []
related: []
tests: []
---

# An accepted design drafts its requirements

## Definition of Done

- `Derive requirements` on an accepted design dispatches impact-analysis/feature-scaffold with the design as source; REQs arrive `draft` citing the design's decisions; the actuator row approves them.
- No REQ text is ever generated without the dispatch — FEAT-0051's rule.

## Done — 2026-08-11

`Derive requirements` on an accepted design, in the agent-action registry.

**Only on `accepted`.** An unaccepted design has nothing to derive *from*, and offering the verb earlier invites deriving requirements from a shape nobody agreed to — which is the failure *design before code* exists to prevent, reached from the other direction.

**It dispatches; it never writes.** [[FEAT-0051]]'s rule, and the reason this is a prompt in a registry rather than a code path: the composed prompt runs `impact-analysis` against existing requirements and `feature-scaffold` where a new capability is implied, and every REQ arrives `status: draft` citing the design's decisions. If this verb ever grew a branch that wrote requirement prose directly, the tool would be authoring the specification it exists to render.

**And it forbids self-approval in as many words** — *"Do NOT approve them — approval is the actuator row's, and a requirement the tool approved for itself is not a requirement anybody agreed to."* Asserted in a test, because that sentence is the difference between a scaffold and a rubber stamp.
