---
type: "[[issue]]"
id: ISS-0197
aliases: ["ISS-0197"]
title: "`## Runs` is write-only — a 107-step manual test records every step result and nothing can answer which steps currently stand"
status: fixed
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

## Fixed 2026-08-18

`cockpit.manual_test_runs` parses the section back, and `manual_test_step_state` answers the question it could not: **which steps currently stand**. The Tests row carries `steps_proven` beside `steps`, absent when the note has never been walked — *"0 of 107 proven"* and *"never walked"* are different sentences and a row that conflated them would be the original defect wearing a number.

**A step's state is its result in the most recent run that mentions it**, not in the most recent run. A partial walk does not un-prove the steps it never reached, and reading "the latest run" would have reported step 1 as unproven because a later, shorter walk did not repeat it. That distinction is the whole content of the fix and it has its own guard.

**Parsed with the writer's own shape**, so the two cannot drift quietly: `test_the_runs_section_round_trips_through_its_own_writer` drives `stamp_test_run` and reads its output back, and fails on the same commit that changes the format — rather than the reader returning nothing, which is indistinguishable from a test nobody has walked.

## What this does not do

A 107-step test is still one note. Whether a long manual procedure should be several acceptance tests is a separate decision, and it is now one that can be argued from parsed data rather than from an intuition.
