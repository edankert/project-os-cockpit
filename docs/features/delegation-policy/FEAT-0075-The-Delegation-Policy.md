---
type: "[[feature]]"
id: FEAT-0075
aliases: ["FEAT-0075"]
title: "The delegation policy — a principal-approved note the actuators consult, delegate writes that carry their authority, and the push decision taken as an ADR"
status: doing
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[DES-0009-The-Standing-Worker]]", "[[ADR-0009-The-Principal-Is-A-Role]]"]
goal: "DELEGATION.md as the per-repo record of what is delegated and what escalates, approved through the actuator row it configures; the actions endpoint answering per caller identity; every delegate write stamped with its authority; and publishing under autonomy decided, not eroded."
requirements: ["[[REQ-0029-A-Delegate-Is-Always-Distinguishable]]", "[[REQ-0030-The-Worker-Never-Outruns-Its-Policy]]"]
tasks:
  - "[[TASK-0326-The-Policy-Note]]"
  - "[[TASK-0327-Role-Checks-Consult-Policy]]"
  - "[[TASK-0328-The-Push-Decision]]"
release: ""
related: []
tests: []
---

# The delegation policy

## Goal

ADR-0009 §4 made the delegation "a per-repo recorded fact"; this feature is that fact's format and its enforcement. The policy passes through the gate it configures — the principal approves DELEGATION.md via the actuator row — and its absence means what it should: **no delegation, no worker.**

## Out of Scope

- Fleet-default policies. Each repo's principal signs each repo's policy; inheritance is a later convenience with its own risks.
- Any delegation of publishing — that is TASK-0328's ADR to decide, explicitly.
