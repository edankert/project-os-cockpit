---
type: instruction
id: INSTR-QUALITY
status: active
owner: group:maintainers
created: 2026-01-27
updated: 2026-01-27
tags: [instructions, quality]
---

# Quality and close-out rules

These rules define what “done” means for work tracked in this documentation system.

## Minimum close-out for any implemented task
- Update the task note status to `done`.
- Update `../../SNAPSHOT.yaml`:
  - set task status to `done`
  - update `focus` (clear or move to next task)
  - update related item statuses if appropriate (issue fixed/closed, feature progressed)
- If behavior/paths/contracts changed, create a `CHG-*` note and link it.

## Documentation Fidelity
- Ensure `metrics` in `../../SNAPSHOT.yaml` accurately reflect the count of `done` features and tasks.
- Verify that every item in the snapshot has a valid `file` path that exists on disk.
- Discrepancies between the filesystem and the snapshot are considered a build failure.
- **Enforcement:** Use the `snapshot-sync` skill (`../skills/snapshot-sync/SKILL.md`) to validate invariants and reconcile drift between the snapshot and notes.

## Verification gating (tests)
- Do not mark an implementation task `done` unless verification is complete:
  - If verification is automated: link to the relevant `[[test]]` and ensure it is `status: passing` (and record evidence in the test note).
  - If verification is manual: the LLM must create a `[[test]]` note with a clear procedure; a human runs it and reports results; the LLM then updates the test to `passing`/`failing` with evidence.
- Do not mark an issue `closed` unless the verifying test(s) are `passing` (use `fixed` for “implemented but not yet verified”).
- Do not mark a requirement `verified` unless the verifying test(s) are `passing`.
- Do not mark a feature `done` unless its required tasks are `done` and required tests are `passing`.

## Verification expectations (generic)
- Prefer a reproducible command, test, or check that demonstrates the change.
- If verification is manual, record exact steps and expected outputs in the task/workflow note.
