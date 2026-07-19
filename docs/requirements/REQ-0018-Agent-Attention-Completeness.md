---
type: "[[requirement]]"
id: REQ-0018
aliases: ["REQ-0018"]
title: "Every agent state that needs the user is discoverable in-app, across all workspaces, until acted on or dismissed"
status: approved
implements: []
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
priority: high
scope: "FEAT-0030"
specifies: ["[[FEAT-0030-Agent-Inbox]]"]
verifies: []
related: ["[[FEAT-0020-Agent-Activity-Surfaces]]"]
tests: []
---

# REQ-0018 — agent attention completeness

## Requirement

The cockpit must answer "what needs me?" completely from one in-app surface: (1) `needs-input` states (act now), (2) `waiting` states (turn finished, review), and (3) recently finished sessions (what happened while away) must all appear, across **all** workspaces, and must persist until the user acts or dismisses — not evaporate on state decay. An OS notification may announce a transition, but missing it must never mean losing the information.

Severity must be honest, and attention must have a read-state: a normally-finished turn is `waiting`, never the blocked-red tier (that tier is reserved for mid-work blocks such as permission prompts); and urgency animation distinguishes *unseen* (pulses) from *seen-but-pending* (static colour) — looking at a workspace acknowledges its current alert without changing any state data. (Added 2026-07-19 after the persistent-red-blink report.)

## Rationale

Today the inbox lists only `needs-input`; `waiting` exists solely as a missable OS notification and a transient rail pulse, and completed background sessions decay to idle with no landing place (review finding, 2026-07-19 — mockups: claude.ai/code/artifact/7011ef1d-f77f-4585-a899-d4ac84a78976).

## Impact analysis (2026-07-19, re-checked after the read-state addition)

Touches FEAT-0020's inbox surface (extension, no contradiction) and the severity mapping in FEAT-0019's ingest table (idle_prompt remap — deliberate semantic correction, tracked as TASK-0156 with external-hook parity via TASK-0153). No conflict with existing REQ-0001..0017 (rendering/adapter/landing concerns). Confirmed no tensions.
