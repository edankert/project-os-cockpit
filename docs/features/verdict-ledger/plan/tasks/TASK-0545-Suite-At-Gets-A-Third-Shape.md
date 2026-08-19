---
type: "[[task]]"
id: TASK-0545
aliases: ["TASK-0545"]
title: "`suite_at` gets a third shape — a historical read after the ledger cut needs notes plus a ledger"
status: done
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

- [x] `suite_at` reads the ledger at the ref and joins it to the notes at that ref.
- [x] The three-way branch is documented where the two-way one is, with the same reasoning: a tag is immutable, so the shape it holds is a permanent fact about the past.
- [x] The two callers that matter are proved on a real tag: `_chronic` (`acceptance.py:1134` — the oldest tag at which a row was already unsettled) and the release delta (`:1479`, `:1502`).
- [x] Still two subprocesses per ref, not N.

## Notes

**No other task in this phase names `suite_at`**, and it is the one read path where "the verdict lives elsewhere now" silently produces a wrong answer rather than an error — every historical tag would report zero walked, and the chronic-rows surface would report every row as chronic.

Found by auditing the decisions against the tasks rather than by anything failing, which is the argument for doing that audit before the phase starts rather than after.

## Done 2026-08-19 — and it found a live bug on the way in

`suite_at` reads three shapes now: the document, notes-with-marks, and notes-plus-ledger. The third is the one that produces a **wrong answer** rather than an error — a historical suite with no verdicts on its notes looks exactly like a historical suite nobody walked.

**Opening the function exposed [[ISS-0221]]**, which had nothing to do with this phase. `_notes_at` matched `CHK-` only and never followed [[ADR-0031]]'s renumber, so from 2026-08-18 it matched nothing and `suite_at` returned **`None` at HEAD**. Every consumer read that as *"no baseline"*, and the release delta has been reporting `comparable: false` at every post-migration ref for a day.

It survived because it fails in the direction that makes a surface say **less** rather than something wrong, and because `test_gate_delta`'s twelve historical tags all predate the migration — the branch that was broken was never the branch under test. Both prefixes are matched now, permanently: a tag is immutable, so the refs holding `CHK-*` will hold them forever.

**The cost guard moved from 3 subprocesses to 4** (5 when a ledger exists), and its comment now says what it defends: the **scaling**, not the constant. None of the calls grows with the number of checks.

**A historical ledger that will not parse is skipped, not raised.** The past is immutable, so refusing it would make a surface unable to render a tag nobody can fix.
