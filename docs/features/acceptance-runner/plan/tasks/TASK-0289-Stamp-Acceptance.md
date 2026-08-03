---
type: "[[task]]"
id: TASK-0289
aliases: ["TASK-0289"]
title: "stamp_acceptance — the run log into the feature note, and the gate's satisfied state"
status: backlog
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0063-The-Acceptance-Runner]]"]
parent: "[[FEAT-0063-The-Acceptance-Runner]]"
effort: M
depends: ["[[TASK-0288]]"]
blocks: []
related: []
tests: []
---

# stamp_acceptance

## Definition of Done

- A completed run appends `### <date> — <witness> — N passed · M failed → ISS-… · K skipped` under `## Acceptance runs`, in stamp_test_run's grammar.
- `accepted_by`/`accepted_date` written only by a completed run on a feature that requested acceptance — no other path stamps them (REQ-0028).
- All writes through note_writes' guards; the hardening suite gains the acceptance verbs.
