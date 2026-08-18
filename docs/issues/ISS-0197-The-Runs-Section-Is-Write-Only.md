---
type: "[[issue]]"
id: ISS-0197
aliases: ["ISS-0197"]
title: "`## Runs` is write-only — a 107-step manual test records every step result and nothing can answer which steps currently stand"
status: open
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: cockpit-server
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
related: ["[[ISS-0195-Two-Types-Carry-One-Act]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]"]
---

# `## Runs` is write-only

Found by the independent review of [[ISS-0195-Two-Types-Carry-One-Act]], 2026-08-18. It is the true and much narrower content of that note's refuted claim that manual-test steps are "invisible".

**They are not invisible.** `manual_test_steps()` parses **362 steps** across the 22 manual tests; `steps=` rides every row of the live Tests nav (`TST-0013 steps=107`); `~tests/<TST>/run` opens a stepper; and `POST /api/notes/test-run` → `note_writes.stamp_test_run()` writes a per-step result line under `## Runs`.

**Nothing reads it back.** `_RUNS_HEADING_RE` occurs **only in the writer**. So the per-step results are prose that no surface parses, and the note's own status is the sole state a run leaves behind.

The consequence is specific: *"which of TST-0013's 107 steps is currently unproven"* is unanswerable, and a partly-walked test is indistinguishable from an unwalked one. A walk interrupted at step 60 of 107 records sixty results and reports nothing.

## Why this is a check-shaped problem in a test

This is precisely the granularity a `CHK-*` has and a manual `TST-*` does not — one addressable subject per thing to verify. [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] merges the types and does **not** fix this: a 107-step test is still one note after the merge.

It is worth its own decision later — whether a long manual test should be several acceptance tests — and worth reading first, which is cheap.

## Next actions

- [ ] Parse `## Runs` back, so the most recent result per step is available to the Tests view and the runner resumes where a walk stopped.
- [ ] Then reconsider whether a 107-step test should be 107 notes, with the parsed data to argue from rather than an intuition.
