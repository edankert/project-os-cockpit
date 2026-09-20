---
type: "[[change]]"
id: CHG-20260920-CI-Runs-The-Suite-Instead-Of-Reporting-Green-Over-Nothing
title: "CI runs the test suite, where it had been passing without running a single test"
status: merged
created: 2026-09-20
updated: 2026-09-20
owner: user:edwin
related: ["[[REQ-0058-An-Automated-Test-Carries-No-Verdict]]", "[[ADR-0038-The-Suite-Is-The-Verdict]]"]
tags: [ci, tests]
---

# CI runs the test suite, where it had been passing without running a single test

## What changed

This repo's CI job reported success without executing any of its tests, and now runs the suite once and reports what it finds.

Forty-three of this repo's forty-four test commands begin with `.venv/bin/`. The `validate-docs` workflow installs into the runner's system Python and never creates a `.venv`, so on GitHub Actions every one of those commands exits 127. The runner this repo carried classified that as *unrunnable*, printed "an environment gap, not a failure", and exited 0. The job went green in 21–33 seconds, which is not long enough to run forty-four cold pytest suites — the clearest sign, in hindsight, that it was running none of them.

`SNAPSHOT.yaml` now declares the one command that covers them:

```yaml
ci:
  suite_command: "python -m pytest -q"
```

and this repo takes the template's runner, whose `--ci` path runs that single command and treats a test CI cannot execute as a failure rather than a shrug.

## Who notices

Anyone pushing to this repo. CI now takes as long as the suite takes, and a broken test fails the build instead of disappearing into a count of unrunnable ones.

## Impact

- `tools/scripts/run-tests.py` — replaced by the template's, ending a month-old fork (project-os-dev ISS-0075). The two were never in conflict at the decision level: ADR-0025 adopted this repo's own ADR-0038 fleet-wide and cites it. The fork simply fell behind five template fixes and, in copying one of them, broke the `--ci` path: its `main` unpacked four values from a `run_one` that returns three, so declaring `ci.suite_command` before this change would have crashed the runner.
- `SNAPSHOT.yaml` — a `ci:` block.
- `tests/test_runner_writes_nothing.py` — calls the runner without `--write`, and asserts the flag is now refused. Every other assertion it made already held for the template's runner.
- `.project-os-sync` — the `keep_local:` list is empty; this repo no longer keeps any file back from the template.
- `docs/requirements/REQ-0058-*.md` — two acceptance lines no longer describe `--write` as accepted-and-inert.

## What was gained and lost

Gained: a test CI cannot run fails the build (`PROJECT_OS_ALLOW_UNRUNNABLE=1` accepts the gap deliberately when that is wanted); a repeated command runs once; a failing command prints its last forty lines rather than one; `--ci` works at all.

Lost: `--write` as an accepted no-op. ADR-0038 kept it because every invocation of the day passed it. On 2026-09-20 no executable caller in the fleet passed it — only past-tense prose in change notes — and the template's runner had refused it since 2026-09-03.
