---
type: "[[task]]"
id: TASK-0537
aliases: ["TASK-0537"]
title: "The write path appends an event — `mark_check` stops being a note write, and the endpoint says which platform it recorded"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0136-The-Cockpit-Reads-And-Writes-The-Ledger]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The write path

## Definition of Done

- [x] `note_writes.record_verdict` appends to the ledger and **modifies no note** — named for what it does rather than for where it lives.
- [x] `POST /api/notes/mark-check` routes to it when the payload names a platform, and `record_verdict` refuses without one.
- [x] The author is recorded, defaulting to the desk's principal.
- [x] A reason-bearing mark is refused without a reason, by `ledger.check_entry`, so the endpoint and the file cannot disagree.
- [x] `verdict: needs-re-run` appends an invalidation event and still requires a change id that resolves.
- [ ] Concurrent appends do not lose an entry — **not addressed**, see below.

## Done 2026-08-19

**`mark_check` is kept, not deleted.** Nine of twelve fleet repos have no ledger and their suites must keep working exactly as they did; a write path that stopped working the day the schema changed upstream would take the tool away from every repo that had not migrated. The discriminator is **the payload**, not a config flag: a repo mid-migration has both shapes reachable for exactly as long as it takes, and a flag would have to be flipped by somebody who remembered.

**The platform is required rather than defaulted**, and that is the whole point. A default would put the old bug back with a friendlier interface — 579 notes recording an Android result as a platform-free fact.

**Concurrency is not addressed and is recorded as such.** `append` is read-modify-write on one file, so two simultaneous appends can lose one. Today every writer is a single local sidecar and a CI emitter that does not exist yet ([[FEAT-0138]]), so the window is theoretical — but it stops being theoretical the moment Stage 2 lands, and the honest place to say so is here rather than in a review.

## Notes

`mark_check` living in `note_writes.py` becomes wrong by name once it writes no note. Renaming it is not tidying — the module is the boundary that says what may touch a note, and leaving a ledger writer inside it re-opens the question every reader would otherwise stop asking.

[[ADR-0035]] gets stronger here, not weaker: a release page has nothing to write into. [[ISS-0210]]'s sixty live marks cannot come back by accident.
