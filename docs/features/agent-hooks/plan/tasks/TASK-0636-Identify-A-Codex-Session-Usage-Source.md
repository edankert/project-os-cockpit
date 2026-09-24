---
type: "[[task]]"
id: "TASK-0636"
title: "Identify a supported Codex session usage source"
status: "done"
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: "user:edwin"
created: "2026-09-23"
updated: "2026-09-23"
source: ["User request, 2026-09-23", "docs/reference/codex-parity-review-2026-09-23.md"]
parent: "[[FEAT-0019]]"
effort: "S"
depends: []
blocks: []
related: ["[[ISS-0312]]", "[[RISK-0004]]"]
tests: []
---

# Identify a supported Codex session usage source

## Definition of Done

- [x] Produce a bounded evidence note identifying whether supported read-only APIs can identify and observe the exact independently running Codex terminal thread.
- [x] Distinguish model identity, measured token use, context occupancy, account allowance and cache lifetime. State which are supported, unavailable or only historical.
- [x] Probe without creating, resuming or taking ownership of a thread, generating background model traffic, changing login state or copying credentials into evidence.
- [x] Conclude either with a concrete read-only integration proposal or an explicit unsupported result. If observation requires a new session owner, stop that branch and link the deferred PHASE-040 decision.

## Steps

- Confirm the installed behavior and capture a minimal reproduction.
- Deliver only this task's bounded result and record verification evidence.
- Update ISS-0312 and the parent plan before moving focus.

## Notes

This is an investigation, not authorization to add meters or a second session host. Keep cache unknown unless reliable data proves more. FEAT-0081 remains the unchanged Claude transcript reader; its no-API and no-warming contracts continue to hold. Technical uncertainty is already tracked by ISS-0312; do not mint a duplicate issue.

The source request and scope decision are recorded verbatim in [[ISS-0312]]. [[RISK-0004]] covers schema drift, configuration preservation and event identity. No new dependency or endpoint is authorized by this task.

## Evidence, 2026-09-23

See [the verification report](../../../../reference/codex-parity-verification-2026-09-23.md). This bounded investigation is complete; it does not certify full lifecycle parity.
