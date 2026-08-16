---
type: "[[task]]"
id: TASK-0430
aliases: ["TASK-0430"]
title: "The suite is addressable — a check is found and written by section and ordinal, never by a global checkbox index"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0103]] — the walker needs an address it can trust"]
parent: "[[FEAT-0103-The-Gate-Is-Walkable]]"
effort: M
depends: []
blocks: ["[[TASK-0432-The-Gate-Lists-Its-Checks]]", "[[TASK-0433-The-Acceptance-Walker]]"]
related: ["[[ISS-0141]]"]
tests: ["[[TST-0029-The-Walker-Ticks-What-It-Walked]]"]
---

# The suite is addressable

## What

`acceptance.Item` already computes `number` = `f"{section}.{ordinal}"` — `1.25.3`. That becomes the address a walker reads and writes by, plus the resolver that turns it into a line in `ACCEPTANCE_TESTS.md`.

## Why not the existing index

`POST /api/notes/check-toggle` addresses a checkbox by its **zero-based ordinal within the whole rendered file**. The suite has 542 of them. Any edit above a row shifts every index below it, and the walker writes whatever is now at that position — silently, and to a check nobody was looking at. A walker that writes the wrong row is worse than one that writes nothing.

Section-and-ordinal survives edits elsewhere in the file, and when its own section changes it fails to resolve rather than resolving to something else.

## Definition of done

- [ ] `acceptance` resolves a `number` to the exact source line, and returns nothing rather than a guess when it cannot
- [ ] A write refuses when the row at that address is not the row the caller thought it was — the name is carried and compared
- [ ] `mtime` guard, as every other `note_writes` path has
- [ ] A `- [~]` reconciled row is refused: settled by decision is not the same as walked ([[ISS-0141]])
- [ ] The write goes through `note_writes`, inheriting its discipline, rather than extending the older `check-toggle` endpoint
- [ ] Round-trip asserted: parse the suite, walk a check, re-parse, and the count moves by exactly one
