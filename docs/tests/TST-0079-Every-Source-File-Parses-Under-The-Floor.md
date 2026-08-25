---
type: "[[test]]"
id: TST-0079
aliases: ["TST-0079"]
title: "Every source file parses under the oldest Python the project claims — the one defect class a newer interpreter cannot see"
status: active
covers: ["[[ISS-0256]]"]
owner: user:edwin
created: 2026-08-25
updated: 2026-08-25
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
source: ["[[ISS-0256]]"]
scope: system
level: unit
entrypoint: ""
command: ".venv/bin/pytest tests/test_python_floor.py -q"
last_verified: ""
issues: ["[[ISS-0256]]"]
tasks: ["[[TASK-0578]]"]
artifacts: []
related: ["[[FEAT-0138]]"]
---

# Every source file parses under the floor

Automated, in `tests/test_python_floor.py`.

## What it pins

**That no source file uses a construct PEP 701 introduced.** `pyproject.toml` promises `>=3.11`; CI pins `3.11`; this machine runs 3.13. A backslash inside an f-string *expression* compiles here and is a `SyntaxError` there — so the file does not fail, it fails to **parse**, and every test that imports or executes it fails at once with a message about syntax rather than about behaviour.

**That the detector fires.** A guard nothing has been seen to catch is an assumption. `tests/fixtures/pep701_offender.py.txt` holds the construct from `migrate-acceptance-checks.py:169` verbatim, and a test asserts the scan finds it. This is not ceremony: the first version of the detector, written the obvious way, returned **zero findings against that very line** — it skipped `FSTRING_MIDDLE` tokens, which is precisely where the backslash lives when the offending string is nested inside another f-string.

**That the module retires itself.** `test_the_floor_is_below_the_pep_701_relaxation` fails once `requires-python` reaches 3.12, at which point both constructs are legal everywhere the project runs and the module should be deleted rather than left as a check that cannot fail.

## Two halves, because the interpreter decides what can be asked

**On the floor (< 3.12), it compiles every file.** Authoritative and exhaustive — the real grammar, every construct, not just the two this module can name. That is the half CI runs.

**Above it (>= 3.12), it scans for the constructs PEP 701 relaxed.** Narrower by necessity: with no floor interpreter there is nothing to ask. It buys earlier discovery, not equivalence.

The first version had only the second half — and reached for `tokenize.FSTRING_START`, **which 3.12 added**. So a guard written to protect 3.11 raised `AttributeError` on 3.11: the very mistake it exists to catch, one layer up, shipped inside the fix for it. CI caught it on the next run, which is the argument for the whole exercise.

## Why the existing checks could not see it

`validate-docs` passed. `validate-docs.sh --as-committed` passed. That second one is the repo's own remedy for "a local pass is not a CI pass" and it is genuinely strong — it materialises `HEAD` into a temp tree, so ignored and untracked files cannot hide there. But it runs **the local interpreter**, and a version-conditional syntax error is invisible to any interpreter new enough to accept it.

## Mutations checked

Each applied, each caught, before this was recorded:

- the original f-string reinstated in `migrate-acceptance-checks.py` → the scan half fails.
- the `len(quotes) < 2` depth test removed from the detector → the known-offender test fails, which is the first version's bug reproduced deliberately.
- `tokenize.FSTRING_START`/`MIDDLE`/`END` deleted from the module and `CAN_SCAN` forced false, simulating 3.11 → imports cleanly and the compile half passes over every source file. The one thing this cannot show locally is the fixture raising `SyntaxError`, because it compiles fine on 3.13 — that assertion is CI's to make.
