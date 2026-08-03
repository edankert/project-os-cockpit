---
type: "[[risk]]"
id: RISK-0005
aliases: ["RISK-0005"]
title: "The write surface — a LAN-visible server gains mutation endpoints, and every future verb will want to join them"
status: open
severity: high
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["Preflight risk scan for PHASE-023, per LIFECYCLE's security trigger"]
component: server
mitigation: "[[REQ-0027-Every-Write-Guarded]]"
related: ["[[FEAT-0059-The-Write-Service-Widens]]", "[[REQ-0026-Only-Human-Owned-Transitions]]"]
tests: []
---

# The write surface

## The hazard

The render server binds 0.0.0.0 so a tablet can read the notes (RISK-0001 accepted that for a read-only surface). PHASE-023 adds endpoints that **modify the record** — transition, tick, create — and PHASE-024/025 add more. Two failure shapes:

1. **The guard regresses** — a refactor drops `_require_loopback` from one handler and every device on the Wi-Fi can approve requirements. Nothing visible changes; the app works identically.
2. **Scope creep by precedent** — each new verb cites the last as licence, and the narrow door becomes a REST API for the corpus without any single change looking like the step too far.

## Why open, not mitigated

The mitigation ([[REQ-0027]]) is written but not yet implemented or tested. This risk closes when the hardening suite exists and exercises every refusal **by attempting the forbidden thing** — including a non-loopback write against every mutation endpoint enumerated by walking the route table, so a new endpoint added without the guard fails the suite by existing.

## Trigger review

Any new mutation endpoint, any change to the server's bind addresses, or any proposal to let mode 1 (the LAN-served cockpit) write.
