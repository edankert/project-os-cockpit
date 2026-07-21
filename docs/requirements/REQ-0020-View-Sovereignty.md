---
type: "[[requirement]]"
id: REQ-0020
aliases: ["REQ-0020"]
title: "View sovereignty — the user's chosen view is never evicted without consent"
status: implemented
implements: []
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-20
source: ["[[ISS-0011-Follow-Mode-Evicts-Chosen-View]]"]
priority: high
scope: "FEAT-0034"
specifies: ["[[FEAT-0034-Agents-Tab-And-Follow-Control]]"]
verifies: []
related: ["[[REQ-0018-Agent-Attention-Completeness]]"]
tests: []
---

# REQ-0020 — view sovereignty

## Requirement

Automatic navigation (agent follow, or any future auto-focus mechanism) must be consentful: (1) following is a visible, persisted per-workspace toggle in every UI — desktop gains the Following/Manual control mode-1 already has; (2) even while following, a **virtual page the user deliberately opened** (~agents, ~overview, ~session/…) is never replaced by an automatic navigation — follow updates apply to the doc surface only; (3) an automatic navigation that was suppressed must remain discoverable (e.g. the existing "Agent focus → …" toast offering the jump).

## Rationale

The desktop shell hard-follows every `cockpit:focus` event, so agent activity evicts whatever the user is reading — including the fleet screen built precisely for watching agents (ISS-0011, user report 2026-07-19; options artifact §1: claude.ai/code/artifact/f3999688-73de-4c36-bcc7-b2511f554ed0).

## Impact analysis (2026-07-19)

Touches the FEAT-0021/COCKPIT.md "cockpit focus" contract: agents keep calling `cockpit focus` unchanged — the *receiver* becomes polite. Mode-1 already satisfies (1); no existing requirement demands hard-follow, so no conflicts. Confirmed no tensions with REQ-0001..0019.
