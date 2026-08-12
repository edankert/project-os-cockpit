---
type: "[[requirement]]"
id: REQ-0034
aliases: ["REQ-0034"]
title: "A write from a non-loopback surface proves who is asking — authentication replaces the loopback check rather than removing it"
status: draft
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
phase: "[[PHASE-029-One-Tool-Two-Front-Doors]]"
source: ["[[ADR-0010]] option 4, decided 2026-08-12"]
features: []
related: ["[[ADR-0010]]", "[[REQ-0027]]", "[[RISK-0005-The-Write-Surface]]", "[[RISK-0001-Render-Server-Exposure]]", "[[ADR-0022]]"]
tags: [requirement, security]
---

# A non-loopback write proves who is asking

## Why this exists

[[ADR-0010]] option 4 makes parity the goal and this its precondition. Until it is implemented, **[[REQ-0027]] stands unchanged**: writes are loopback-only, and no part of that decision is licence to drop a guard early.

The thing being replaced is not a safety net over an authorisation model — **it is the authorisation model**. There is no authentication anywhere in this tool today. Remove `_require_loopback` without putting something in its place and the question *"who may write here"* has no answer: every device on the network can transition notes, tick criteria and create files across twelve repos, one of which publishes a live website.

## Requirement

**A mutation request arriving from a non-loopback peer is refused unless it carries proof of identity that the sidecar can verify.**

- The loopback path keeps working unchanged — a local write must not become harder because a remote one became possible.
- Refusal stays the default: **absence of proof is refusal**, never a fallback to "probably fine on a LAN".
- The proof is per-request. A surface that authenticates once and then writes freely is a session, and a session on a shared network is a shared session.
- Whatever proves identity must be **stateless to the record**: it never lands in a note, and a stolen artefact expires.

## Acceptance

- [ ] A non-loopback mutation without proof is refused with the same shape as today's refusal, verified by driving the real LAN interface rather than by a static check — the standard [[REL-0001]]'s pass set.
- [ ] A non-loopback mutation **with** valid proof succeeds, and writes exactly what the same call over loopback writes.
- [ ] The enumerating guard still enumerates: every route that touches `docs/` is covered, and a new endpoint that forgets the check fails the suite **by existing** — the property `test_every_note_mutating_endpoint_requires_loopback` already has and must not lose.
- [ ] Expiry and revocation are exercised, not merely designed.
- [ ] [[RISK-0005]] is re-opened before this lands and re-closed on its own evidence, rather than inheriting the closure of the mitigation this replaces.
- [ ] The terminal endpoint is **out of scope and stays loopback-only** ([[RISK-0001]]): shell access is a different hazard with a different answer, and widening it is not implied by widening writes.

## Out of scope

Deciding the mechanism. Token, mTLS, a pairing handshake, an OS keychain round-trip — this requirement says what must be true, and the design that follows says how. Choosing here would be an ADR pretending to be a requirement.
