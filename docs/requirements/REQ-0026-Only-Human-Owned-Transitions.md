---
type: "[[requirement]]"
id: REQ-0026
aliases: ["REQ-0026"]
title: "The cockpit performs only human-owned transitions"
status: draft
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[DES-0005-The-Actuator-Grammar]]"]
priority: high
scope: "Every write path added by PHASE-023 and consumed by later phases"
specifies: ["[[FEAT-0059-The-Write-Service-Widens]]", "[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]"]
acceptance:
  - "Every transition the cockpit offers appears in STATUSES.md's vocabulary and is a human judgment (approve, accept, decline, triage, answer) — never a close-out or gated status"
  - "Requesting an agent-owned transition is refused server-side with the ownership rule named, regardless of what any renderer displays"
  - "The transition vocabulary exists in exactly one module; no renderer restates it (guarded in the ISS-0023 style)"
  - "Removing a transition from the table removes it from every surface without a renderer change"
---

# Only human-owned transitions

The line PHASE-007 drew and ADR-0007 crossed narrowly — *the cockpit writes only to record a decision a human made in the UI* — restated as an enforceable contract for the widened door. The agent's column of the ownership table is unreachable from the UI by construction, and the refusal is the server's, so no display bug can widen it.
