---
type: "[[task]]"
id: TASK-0289
aliases: ["TASK-0289"]
title: "stamp_acceptance — the run log into the feature note, and the gate's satisfied state"
status: done
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
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

## Done — 2026-08-11

`note_writes.stamp_acceptance_run` + `POST /api/notes/acceptance-run`.

A completed run appends `### <date> — <witness> — N passed · M failed → ISS-… · K skipped` under `## Acceptance runs`, in `_append_run_log`'s grammar, and stamps `accepted_by` / `accepted_date` / `acceptance: accepted`.

**[[REQ-0028]]'s four criteria, each with a test:**

1. *Every tick carries who and when, machine-composed* — the witness comes from the request's `actor` and the date from `_today()`. Neither is free text on this path.
2. *The log line names the same witness and totals* — one composed string, so the log and the frontmatter cannot disagree.
3. *`accepted_by` is only ever written by a completed run* — an incomplete run appends its log with `· INCOMPLETE` and stamps **nothing**. This is the one most easily got almost-right, so it has its own test.
4. *An agent cannot be a witness* — carried by `_require_loopback` plus REQ-0026's terms; asserted by the enumerating guard, which already sees the new route.

**Two guards beyond the criteria.** A run may not be recorded on a non-feature (acceptance is a feature-level judgment). And a **completed** run is refused on a feature that never requested acceptance — stamping one nobody asked about manufactures a judgment. The refusal is on the *stamp*, not the log: recording that somebody walked criteria is harmless and useful, so a partial walk stays possible anywhere.

`acceptance:` moves `requested → accepted`, or the feature would keep appearing on the queue it has just left.
