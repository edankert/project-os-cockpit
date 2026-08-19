---
type: "[[task]]"
id: TASK-0545
aliases: ["TASK-0545"]
title: "`suite_at` gets a third shape — a historical read after the ledger cut needs notes plus a ledger"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0136-The-Cockpit-Reads-And-Writes-The-Ledger]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# Reading the past, for the third time

`acceptance.suite_at(project_root, ref)` reads the suite as it stood at a git ref. It already carries **two** shapes split by time ([[ADR-0030]], TASK-0462): refs before a repo's migration hold `ACCEPTANCE_TESTS.md`; refs after hold notes, read with two subprocesses.

**The ledger makes it three.** A ref after this migration holds notes with no verdict in them — the verdict is in a ledger file at that same ref. A `suite_at` that reads only the notes will report every historical tag as *nothing walked*.

## Definition of Done

- [ ] `suite_at` reads the ledger at the ref and joins it to the notes at that ref.
- [ ] The three-way branch is documented where the two-way one is, with the same reasoning: a tag is immutable, so the shape it holds is a permanent fact about the past.
- [ ] The two callers that matter are proved on a real tag: `_chronic` (`acceptance.py:1134` — the oldest tag at which a row was already unsettled) and the release delta (`:1479`, `:1502`).
- [ ] Still two subprocesses per ref, not N.

## Notes

**No other task in this phase names `suite_at`**, and it is the one read path where "the verdict lives elsewhere now" silently produces a wrong answer rather than an error — every historical tag would report zero walked, and the chronic-rows surface would report every row as chronic.

Found by auditing the decisions against the tasks rather than by anything failing, which is the argument for doing that audit before the phase starts rather than after.
