---
type: "[[issue]]"
id: ISS-0317
aliases: ["ISS-0317"]
title: "Both CI workflows fail on every push: nine tests need things the template's runner does not have, two read a folder a fresh clone does not contain"
status: fixed
phase: []
owner: user:edwin
created: 2026-10-06
updated: 2026-10-06
source: ["ci-failure"]
reported_by: user:edwin
question: ""
severity: high
component: tooling
parent: ""
related: ["[[ISS-0256]]", "[[TST-0079]]"]
tests: []
---

# Both CI workflows fail on every push: nine tests need things the template's runner does not have, two read a folder a fresh clone does not contain

## Problem

Every push since 2026-09-20 has turned both GitHub workflows red, so CI has stopped telling anyone whether a push broke something. On the push of 2026-10-06 (`d1df13c`), `validate-docs` reported 9 failed and 2 errors, and `observed-coverage` reported 2 errors. None of them reproduce on Edwin's Mac, and none is a defect in the cockpit itself.

> [!quote] As reported — 2026-10-06 (user:edwin)
> fix all the errors

## The causes

**1. Two tests call `pytest.skip` without importing `pytest`.** `tests/test_validation.py` skips the miscased-root tests on a case-sensitive filesystem. macOS is case-insensitive, so the skip line never runs here. Linux is case-sensitive, so it runs on CI and raises `NameError: name 'pytest' is not defined`.

**2. A test fixture writes into a folder that a fresh clone does not have.** `attention_index` in `tests/test_surface_ownership.py` writes five task notes into `docs/features/fleet-health/plan/tasks/`. Commit `7b9d512` moved that folder's last notes to `docs/archive/`. Git stores files and not folders, so a clone has no such folder. On this Mac the empty folder is still on disk. This is the only failure in `observed-coverage`, and it fails the two tests that use the fixture.

**3. The template's `validate-docs` workflow now runs the whole suite on a bare runner.** On 2026-09-18 the template's `validate-docs.yml` gained a step that runs the repo's `ci.suite_command` (project-os-dev TASK-0137). That runner checks out one commit, has no `~/Dev/repos/project-os` beside it, and does not build the desktop app. [[ISS-0256]] gave the `observed-coverage` runner all three on 2026-08-25. `validate-docs.yml` is template-owned (`tools/sync/MANIFEST.yaml`) and is shared by every fleet repo, so it cannot be given this repo's sibling. Seven tests fail there for that reason:

- two need the full git history: `test_change_shape.py::test_it_answers_for_this_repos_own_work` and `test_history_payload.py::test_an_anchored_window_ends_at_the_requested_date`;
- four need the template repo: `test_feature_uncovered.py` (two tests), `test_surface_type.py::test_the_template_is_template_owned_and_identical_upstream` and `test_fleet_migration.py::test_main_runs_end_to_end_and_its_dry_run_previews_the_snapshot`;
- one needs the built renderer: `test_digest_watermark.py::test_the_header_measures_from_the_instant_not_the_day`.

## Repro

Clone the repo into a fresh folder and run the suite with `HOME` pointing at an empty folder. That reproduces causes 2 and 3 on macOS. Cause 1 needs a case-sensitive filesystem.

## Expected

Both workflows pass on a clean push. A test whose environment is missing in the `observe` job still fails, as [[ISS-0256]] decided.

## Actual

`validate-docs`: 9 failed, 2100 passed, 40 skipped, 2 errors. `observed-coverage`: 2116 passed, 33 skipped, 2 errors.

## Fix

- Cause 1: import `pytest`.
- Cause 2: the fixture creates the folder before writing into it.
- Cause 3: `test_fleet_migration` passes `--upstream` with the same fallback its `validator` fixture already uses, so it runs on any runner. The other six check for what they need through one helper in `tests/conftest.py`. When it is missing, the test skips and names what is missing. The `observe` job sets `COCKPIT_CI_FULL_ENV=1`, and with that set a missing piece is a failure, not a skip. So the `observe` job keeps the guarantee [[ISS-0256]] gave it, and the template's bare runner stops failing on things it was never given.

Giving the template's runner the full history (`fetch-depth: 0`) would be an upstream change that every fleet repo receives. It is not needed for this fix, because the `observe` job already runs these tests with full history.

## Evidence

- CI runs 37531820960 (`validate-docs`) and 37531820959 (`observed-coverage`), 2026-10-06T21:09:20Z, on `d1df13c`.
- The previous push, `4e5b150` on 2026-09-20, failed `validate-docs` with 11 failures. Two of those (`test_guided_walk_ledger_copy`) no longer occur.
- Reproduced locally in a fresh clone with an empty `HOME`: causes 2 and 3, 7 failures.

## Verification

Run on 2026-10-06, before pushing:

- **Bare runner.** A depth-1 clone of the working tree, with `HOME` pointing at an empty folder, ran the eight affected test files: 144 passed, 11 skipped, 0 failed. Every skip names what is missing.
- **The promise holds.** The same run with `COCKPIT_CI_FULL_ENV=1` gave 9 failed: the seven tests above plus `test_upstream_recognises_coverage_too` and `test_the_escape_is_the_same_field_upstream`. Those two had been passing on nothing on the bare runner. They run the template's validator from a path that does not exist, count zero findings in its empty output, and assert zero. The check now sits in their shared helper `_upstream_findings`.
- **Cause 1.** On a case-sensitive disk image, the two miscased-root tests failed with the old file and skipped with the import added.
- **Full suite, full environment.** On this Mac with `COCKPIT_CI_FULL_ENV=1`: 2140 passed, 11 skipped.

Risk scan: `COCKPIT_CI_FULL_ENV` is read only by the test suite and set only by `observed-coverage.yml`. The cockpit itself never reads it, so it adds no configuration surface and no `RISK-*`.

## Next Actions

- [x] Fix, run the suite in a fresh clone with an empty `HOME`, then with the full environment.
- [ ] Push and confirm both workflows are green.
