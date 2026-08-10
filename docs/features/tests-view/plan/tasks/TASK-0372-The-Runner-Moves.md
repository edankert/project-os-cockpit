---
type: "[[task]]"
id: TASK-0372
aliases: ["TASK-0372"]
title: "The manual test runner moves from the desk to the Tests view, unchanged in what it writes"
status: backlog
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[FEAT-0086-Tests-Becomes-A-View]]"]
parent: "[[FEAT-0086-Tests-Becomes-A-View]]"
effort: M
due: ""
depends: ["[[TASK-0371-The-Tests-View-And-Its-Register]]"]
blocks: []
related: ["[[TST-0011-Overview-And-Review-Desk]]"]
tests: []
---

# The runner moves

## Definition of Done
- [ ] The stepper runs from the Tests view: steps parsed from the note, Pass/Fail/Skip, evidence
- [ ] `stamp_test_run` writes exactly what it writes today — `status`, `last_run`, the `## Runs` entry — with the same allow-list, mtime precondition and loopback check
- [ ] A fail still drafts its `ISS-*`
- [ ] `~review/<TST>/run` deep links migrate to the new route
- [ ] No write path changed; the diff is routing and placement only

## Steps
- [ ] Move `buildTestRunner` and its route; leave `note_writes` untouched
- [ ] Add the redirect from the old route
- [ ] Re-run the round-trip assertion: a stamped note is byte-identical outside its allow-listed fields

## Notes
The runner is the desk's one piece of genuine machinery and the reason its removal is a move rather than a deletion. Everything guarding it lives server-side and must not be touched by a renderer change — if this task ends up editing `note_writes.py`, something has gone wrong.

[[TST-0011]] exercises the desk and will need its steps updated for the new location.
