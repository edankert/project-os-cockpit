---
type: "[[task]]"
id: TASK-0209
aliases: ["TASK-0209"]
title: "Manual test runner — TST Steps parsed into a stepper; Pass/Fail/Skip + evidence; status/last_run stamping + ## Runs log; fail drafts an ISS"
status: done
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
parent: "[[FEAT-0041-Review-Desk]]"
effort: ""
due: ""
depends: ["[[TASK-0206]]"]
blocks: []
related: ["[[TST-0011-Live-Session-Instrumentation]]", "[[FEAT-0019-Agent-Hook-Ingestion]]"]
tests: []
---

# Manual test runner

## Definition of Done

- [x] The sidecar parses a manual TST note's Steps section (exit-criteria parser pattern) into ordered steps with expected results; `~review/<TST-ID>/run` renders them as a stepper — one emphasized current step with Pass / Fail / Skip and a free-text evidence field, completed steps collapsed above, remaining below, progress bar in the header.
- [x] Completing a run stamps the note: frontmatter `status` (`passing`/`failing` per outcome) + `last_run` (and `last_verified` per the manual-test convention in STATUSES.md), and appends a structured run log (date, per-step result + evidence) under `## Runs`.
- [x] A failing step drafts an ISS through the issue-intake shape — pre-filled with the test ID, step, expected vs observed, and evidence — for the user to confirm; the run log records the draft's ID once filed.
- [x] Aborting a run writes nothing to `status` (the partial log may be kept under `## Runs` marked aborted).
- [x] TST-0011 (at `ready` since June — defined, never executed) is runnable end-to-end and is the acceptance demo.

## Steps

- [x] Steps-section parser in the sidecar (+ tests over TST-0011's actual note).
- [x] Stepper UI + per-step state; evidence capture.
- [x] Write-back: frontmatter stamping + `## Runs` append (+ tests: idempotent append, no body mangling).
- [x] Fail→ISS draft flow via issue intake.

## Notes

This is the manual counterpart of execution-stamped statuses (STATUSES.md: `passing`/`failing` written by the runner, not the author) — the runner is what makes a manual test's status honest, and it gives close-out's "tests must be passing" gate a first-class way to become true. The write scope is strictly the TST note being run.
