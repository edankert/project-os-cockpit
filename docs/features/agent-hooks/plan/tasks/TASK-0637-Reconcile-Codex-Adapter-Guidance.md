---
type: "[[task]]"
id: "TASK-0637"
title: "Reconcile Codex adapter guidance and enforcement limits"
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

# Reconcile Codex adapter guidance and enforcement limits

## Definition of Done

- [x] Update stale Codex guide and ISS-0312 claims to identify the native hooks, skills, agent profiles and embedded telemetry already delivered, retaining dated historical evidence.
- [x] Check documentation-first refusal, invalid completion and Stop validation with telemetry enabled, and identify which checks were fixtures versus real CLI observations.
- [x] Assess whether installed Codex tool events reliably identify reviewer subagents for HC-010 budgeting. Record the enforcement limit when correlation is absent; do not claim parity from instructions alone.
- [x] Keep canonical shared-adapter changes upstream, regenerate any affected downstream adapters, and run the generator consistency and documentation checks.
- [x] Confirm focused task membership resolves the startup hint; preserve TASK-0631 and its existing handoff while Codex work is in focus.

## Steps

- Confirm the installed behavior and capture a minimal reproduction.
- Deliver only this task's bounded result and record verification evidence.
- Update ISS-0312 and the parent plan before moving focus.

## Notes

Documentation reconciliation can proceed while acceptance remains pending. Hook enforcement changes require evidence of supported identity, not an assumption from subagent start/stop names. The bounded assessment may conclude instruction-only enforcement remains necessary.

The source request and scope decision are recorded verbatim in [[ISS-0312]]. [[RISK-0004]] covers schema drift, configuration preservation and event identity. No new dependency or endpoint is authorized by this task.

## Evidence, 2026-09-23

See [the verification report](../../../../reference/codex-parity-verification-2026-09-23.md). Guide reconciliation and enforcement assessment are complete; the focus-hint correction remains open.

## Handoff

Membership is restored, but a direct UserPromptSubmit probe still prints `TASK-0634 is , phase PHASE-007`. The shared dispatcher `item_status()` only matches unquoted statuses; newly scaffolded and sync-derived snapshot entries use quoted strings. Do not rewrite canonical state formatting to conceal the parser defect. ISS-0312 retains this bounded upstream correction: fix and test quoted status parsing in project-os, then sync the dispatcher. The cockpit guide itself is reconciled and 67 generated artifacts plus 12 adapter tests pass.

The correction now proceeds in the template at `/Users/Edwin/Dev/repos/project-os` and is copied into this downstream checkout. The template remains uninitialized and receives no project lifecycle data; this task and change note own the cross-repository patch. Existing untracked upstream rank scripts are unrelated and preserved.

## Resolution

Fixed quoted status parsing upstream and copied the same dispatcher and regression test here. All 13 adapter tests pass, including unquoted, double-quoted and single-quoted states. Upstream docs-first and validation pass; existing unrelated rank scripts were preserved. The direct prompt hint is repeated after snapshot sync below. No shared generated files changed.

Final direct prompt hint: `TASK-0633 is doing, phase PHASE-007`, after sync. TASK-0631 remains doing with its earlier handoff.
