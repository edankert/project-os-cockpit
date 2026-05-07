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

## Acceptance tests
- Acceptance tests are organized into three tiers. See `TESTING.md` for full rules.
  - **Tier 1 (Feature Tests):** Permanent. One or more per feature. Never removed.
  - **Tier 2 (Regression Tests):** Permanent. Created when a bug is fixed. Guards against recurrence.
  - **Tier 3 (Verification Tests):** Temporary. Removed after verified release if covered by unit tests.
- Acceptance test notes (`TST-*`) must include: Preconditions, Procedure (numbered steps with expected outcomes), and Result (pass/fail).
- The consolidated acceptance test checklist lives in `../../docs/tests/ACCEPTANCE_TESTS.md`.
- The `last_run` field records when the test was last executed. A test is **stale** when its linked feature has tasks updated after `last_run`.

## Acceptance test lifecycle
- **After implementing a feature:** create Tier 1 acceptance test(s) covering user-visible behavior.
- **After fixing a bug:** create a Tier 2 regression test that reproduces the original bug scenario.
- **After code changes:** uncheck all acceptance tests whose scope overlaps with the changed code.
- **After writing unit tests** that cover a Tier 2 acceptance test: move it to Tier 3 for removal on next release.

## Release gating
- Before any release, run the `release-verification` skill (`../skills/release-verification/SKILL.md`).
- A release is **blocked** if any Tier 1 or Tier 2 acceptance test is unchecked (not passing).
- Tier 3 tests do not gate releases.
- A test may be marked as a **release exception** if it cannot be completed (e.g., third-party API unavailable). Exceptions must be documented in the release note with justification.
- After re-running and passing all tests, `last_run` is updated, creating the baseline for the next release cycle.

## Post-release cleanup
- Remove Tier 3 tests that are verified and backed by unit tests.
- Clear all "RE-RUN" annotations from acceptance tests.
- Update SNAPSHOT focus to next milestone.

## Verification expectations (generic)
- Prefer a reproducible command, test, or check that demonstrates the change.
- If verification is manual, record exact steps and expected outputs in the task/workflow note.
