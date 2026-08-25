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

**That the check retires itself.** `test_the_floor_is_below_the_pep_701_relaxation` fails once `requires-python` reaches 3.12, at which point both constructs are legal everywhere the project runs and the module should be deleted rather than left as a check that cannot fail.

## What it does not pin

It is **not** a Python 3.11 grammar check, and cannot be one — no 3.11 interpreter is installed on this machine. It covers the two constructs PEP 701 relaxed, which is the gap that actually bit. The general check is CI pinning `3.11`, and that is the authority; this only moves the discovery earlier than a push.

## Why the existing checks could not see it

`validate-docs` passed. `validate-docs.sh --as-committed` passed. That second one is the repo's own remedy for "a local pass is not a CI pass" and it is genuinely strong — it materialises `HEAD` into a temp tree, so ignored and untracked files cannot hide there. But it runs **the local interpreter**, and a version-conditional syntax error is invisible to any interpreter new enough to accept it.

## Mutations checked

Both applied, both failed, before this was recorded:

- the original f-string reinstated in `migrate-acceptance-checks.py` → `test_no_source_file_needs_a_python_newer_than_the_floor` fails.
- the `len(quotes) < 2` depth test removed from the detector → `test_the_scan_sees_a_known_offender` fails, which is the first version's bug reproduced deliberately.
