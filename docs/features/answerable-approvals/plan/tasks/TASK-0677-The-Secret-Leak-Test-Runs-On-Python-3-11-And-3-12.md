---
type: "[[task]]"
id: TASK-0677
aliases: ["TASK-0677"]
title: "The test that searches a started sidecar for its secret passes on Python 3.11 and 3.12, where CI runs it, not only on 3.13"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-16
updated: 2026-10-16
source: ["[[TASK-0667-Tests-Prove-A-Deny-Survives-And-An-Answer-Without-The-Secret-Is-Refused]]"]
parent: "[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]]"
effort: "XS"
due: ""
depends: []
blocks: []
related: []
tests: []
---

# The secret leak test runs on Python 3.11 and 3.12

The first CI runs after the 2026-10-16 push failed on one test, in both workflows: `tests/test_answerable_approval_promises.py::test_a_sidecar_started_as_the_shell_starts_it_leaks_its_secret_nowhere` raised `ValueError: I/O operation on closed file`. validate-docs runs Python 3.12 on Linux and observed-coverage runs 3.11 on macOS. Every other test passed (2197 and 2215).

The test writes the secret to the sidecar's stdin and closes stdin, as the shell does. Its cleanup then called `proc.communicate()`. Before Python 3.13, `communicate()` flushes stdin first and raises on a closed one. This repo's `.venv` is 3.13, so the full local run passed.

The sidecar is not at fault; only the test's cleanup changes. It now waits for the process and reads stderr itself.

## Definition of Done

- [x] The test's cleanup no longer calls `communicate()` after closing stdin, and still asserts that stderr does not carry the secret.
- [x] The test passes on Python 3.13 here and in both CI workflows.

## Result

The cleanup now calls `proc.wait()` and reads stderr. The test file passes here on 3.13 (17 passed). No 3.11 or 3.12 is installed here, so the cause was shown with Python 3.9.6 on a small script: `communicate()` after closing stdin raised `ValueError: I/O operation on closed file`, and the wait-and-read cleanup did not; on 3.13 both work. No other test closes stdin and then calls `communicate()`. Both CI workflows passed on f2c09c1: validate-docs (Python 3.12, Linux) and observed-coverage (Python 3.11, macOS).
