---
type: "[[task]]"
id: TASK-0563
aliases: ["TASK-0563"]
title: "The `test-run` actuator reports a result instead of transitioning the note"
status: backlog
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
source: []
parent: "[[FEAT-0139-The-Suite-Is-The-Verdict]]"
effort: "M"
due: ""
depends: []
blocks: []
related: []
tests: []
---

# The `test-run` actuator reports a result instead of transitioning the note

## Definition of Done
- [ ] Executing a test from the cockpit writes no status
- [ ] The result is shown
- [ ] The loopback guard is unweakened

## Steps
- [ ] Change `note_writes.py`'s `test-run` transition set
- [ ] Return the outcome to the caller rather than persisting it

## Notes

`note_writes.py:120` currently allows `{passing, failing}` for `test-run`. Under [[REQ-0058]] both are forbidden on the population the actuator can reach.
