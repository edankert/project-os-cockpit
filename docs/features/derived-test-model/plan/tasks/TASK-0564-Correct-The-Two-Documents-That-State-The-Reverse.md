---
type: "[[task]]"
id: TASK-0564
aliases: ["TASK-0564"]
title: "Correct the two documents that state the position being reversed"
status: done
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: []
parent: "[[FEAT-0139-The-Suite-Is-The-Verdict]]"
effort: "S"
due: ""
depends: []
blocks: []
related: []
tests: []
---

# Correct the two documents that state the position being reversed

## Definition of Done
- [ ] `TESTING-MODEL.md` line 49 no longer says the runner writes the status
- [ ] `run-tests.py`'s docstring states the new position and keeps its evidence

## Steps
- [ ] Edit `docs/references/TESTING-MODEL.md`
- [ ] Edit the module docstring in the same commit as [[TASK-0559]]

## Notes

Both are local, not template-owned, so they change here.
