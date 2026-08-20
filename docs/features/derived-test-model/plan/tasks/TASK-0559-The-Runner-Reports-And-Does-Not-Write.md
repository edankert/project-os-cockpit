---
type: "[[task]]"
id: TASK-0559
aliases: ["TASK-0559"]
title: "`run-tests.py` reports and does not write"
status: done
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: []
parent: "[[FEAT-0139-The-Suite-Is-The-Verdict]]"
effort: "M"
due: ""
depends: []
blocks: []
related: []
tests: []
---

# `run-tests.py` reports and does not write

## Definition of Done
- [ ] `--write` mutates no note; the flag is removed or becomes a no-op with a stated reason
- [ ] Exit code behaviour is unchanged — non-zero when something failed
- [ ] A test asserts the notes are byte-identical after an execution that would previously have stamped

## Steps
- [ ] Delete the `fm_set` block that writes `status`, `last_run`, `exit_code`, `updated`
- [ ] Keep the three outcomes and the report; they are what CI reads
- [ ] Rewrite the module docstring, which is the clearest statement of the reversed position

## Notes

**First, and before [[TASK-0562]].** Cleaning the corpus while the runner still stamps means the next execution re-stamps what was just stripped.

The docstring's own evidence survives the reversal and should be kept: `failing` written zero times in 5,890 writes. [[ADR-0038]] re-reads it rather than disputing it.
