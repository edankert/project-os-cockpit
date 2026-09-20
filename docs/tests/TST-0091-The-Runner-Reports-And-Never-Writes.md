---
type: "[[test]]"
id: TST-0091
aliases: ["TST-0091"]
title: "The runner reports and never writes: all three outcomes leave a note byte-identical, and it carries no way to write frontmatter at all"
status: active
covers: ["[[REQ-0058-An-Automated-Test-Carries-No-Verdict]]"]
owner: user:edwin
created: 2026-09-20
updated: 2026-09-20
phase: []
source: ["[[ADR-0038-The-Suite-Is-The-Verdict]]", "project-os-dev ISS-0075"]
scope: system
level: unit
entrypoint: ""
command: ".venv/bin/pytest tests/test_runner_writes_nothing.py -q"
last_verified: ""
issues: []
tasks: []
artifacts: []
related: []
---

# The runner reports and never writes

Automated, in `tests/test_runner_writes_nothing.py`.

## What it pins

All three outcomes — passing, failing, unrunnable — leave the test note byte-identical, asserted on bytes rather than on `status:`, because stamping also wrote `last_run:`, `exit_code:` and `updated:`. A failing command still exits 1. `--write` is refused with a usage error. And, structurally, the script carries no `fm_set` and no `write_text`: a dead writer left in a script that must not write is one edit away from writing again, and no behavioural test would notice it come back.

## Why it has a note now

It had none until 2026-09-20. Its only executor was the whole-suite `pytest -q` in `observed-coverage.yml`, so it never appeared in `run-tests.py`'s list beside the other forty-three and nothing showed whether it had run. Filed with the reconciliation in project-os-dev ISS-0075, which replaced this repo's forked runner with the template's; every assertion here held for both, except `--write`, which the template's runner refuses.

The structural assertion was ported upstream at the same time, into the template's `test-verdict-model.sh`, so the other twelve repos get it too.
