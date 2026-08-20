---
type: "[[risk]]"
id: RISK-0005
aliases: ["RISK-0005"]
title: "The write surface — a LAN-visible server gains mutation endpoints, and every future verb will want to join them"
status: closed
severity: high
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: "2026-08-20"
source: ["Preflight risk scan for PHASE-023, per LIFECYCLE's security trigger"]
component: server
mitigation: "[[REQ-0027-Every-Write-Guarded]]"
related: ["[[FEAT-0059-The-Write-Service-Widens]]", "[[REQ-0026-Only-Human-Owned-Transitions]]", "[[ISS-0246-The-Two-Front-Doors-Are-Not-Comparable]]", "[[FEAT-0083-The-Browser-Cockpit-Answers-Questions]]"]
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

## Closed — 2026-08-11

The condition this note set for itself is met: *"closes when the hardening suite exists and exercises every refusal by attempting the forbidden thing — including a non-loopback write against every mutation endpoint enumerated by walking the route table, so a new endpoint added without the guard fails the suite by existing."*

**It exists and it enumerates.** `test_every_note_mutating_endpoint_requires_loopback` parses the POST dispatch table out of `server.py` rather than listing routes by hand — **21 routes** today — and requires `_require_loopback` in each handler that touches `docs/`, with a named allow-list of the five that change runtime state only. A new endpoint that forgets the guard fails by existing, which is failure shape 1 addressed structurally rather than by vigilance.

**And it was exercised for real, not only in the abstract.** [[REL-0001]]'s verification pass drove every mutation endpoint over the LAN interface `192.168.68.123:8791`: **ten of ten returned 403 while reads returned 200**. That is the check `test_mutation_endpoints_reject_non_loopback_callers` explicitly disclosed it could not make — *"an honest static check, since http.server cannot spoof a peer address"* — so the manual walk closed the gap the automated one names.

Failure shape 2 (scope creep by precedent) is answered by [[REQ-0026]]'s ownership table plus the `CREATABLE_TYPES` allow-list, which is asserted as an **exact set** so each widening is a visible decision. It widened once today, from `{issue}` to `{issue, release}`, with the review recorded on the constant ([[TASK-0316]]).

**Trigger review stands.** Any new mutation endpoint, any change to the bind addresses, or any proposal to let mode 1 write reopens this. The desktop sidecar currently binds `127.0.0.1` only; the render server's `0.0.0.0` remains read-only by peer check, not by hope.

## Re-opens by decision — 2026-08-12

[[ADR-0010]] option 4 makes parity the goal and an authenticated write path its precondition ([[REQ-0034]]).

**This risk closed on the strength of the mitigation that decision plans to replace.** Its own trigger already anticipated the moment — *"any proposal to let mode 1 (the LAN-served cockpit) write"* — and that proposal has now been accepted, in principle, with the guard held until the replacement exists.

So the position is stated rather than left to be noticed:

- **It stays `closed` today**, honestly: loopback-only is enforced, enumerated by walking the route table, and driven over a real LAN interface at ten of ten.
- **It re-opens before [[REQ-0034]] is implemented**, not after. A risk whose mitigation is being swapped is live again from the moment the swap starts, and re-closing it must rest on the new evidence rather than inheriting the old closure.
- The re-close condition is [[REQ-0034]]'s acceptance, in full — including that the enumerating guard still fails a forgetful endpoint **by existing**, which is the property that made the first closure worth anything.

## The ten-of-ten is re-run, not inherited — 2026-08-20

Re-homed from [[ISS-0246]], which raised it and could not perform it: it is a precondition on future work rather than work of its own, so it belongs on the risk whose trigger already names the moment.

**Before any write endpoint is offered on a LAN-reachable surface, [[REL-0001]]'s measurement is driven again.** Every mutation endpoint, over the real LAN interface, against the *new* authorisation model — not the loopback check it replaces. Ten of ten returned 403 in August 2026 **because the peer was not on loopback**; an authenticated path answers a different question, so a pass inherited from that run would be evidence about a mechanism that is no longer there.

This bears directly on the eleven reading views [[FEAT-0083]] now scopes. Those are reads and nothing gates them. What is gated is `~release`, and the **write halves** of `~checks` and `~review` — marking a check, recording a verdict — which is why splitting those two at the view boundary rather than porting them whole is the difference between eleven reads and eleven reads plus three writes nobody authorised.
