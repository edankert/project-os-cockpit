---
type: "[[task]]"
id: TASK-0537
aliases: ["TASK-0537"]
title: "The write path appends an event — `mark_check` stops being a note write, and the endpoint says which platform it recorded"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0136-The-Cockpit-Reads-And-Writes-The-Ledger]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The write path

## Definition of Done

- [ ] `note_writes.mark_check` becomes a ledger append; it modifies no note and is renamed to say so.
- [ ] `POST /api/notes/mark-check` takes a platform and refuses without one.
- [ ] The author is recorded from the same principal the desk already uses ([[ADR-0009]] — the principal is a role).
- [ ] A reason-bearing mark is refused without a reason, at the endpoint as well as in the validator.
- [ ] `invalidate_check` appends an invalidation event to the working ledger, requiring a change id.
- [ ] Concurrent appends do not lose an entry.

## Notes

`mark_check` living in `note_writes.py` becomes wrong by name once it writes no note. Renaming it is not tidying — the module is the boundary that says what may touch a note, and leaving a ledger writer inside it re-opens the question every reader would otherwise stop asking.

[[ADR-0035]] gets stronger here, not weaker: a release page has nothing to write into. [[ISS-0210]]'s sixty live marks cannot come back by accident.
