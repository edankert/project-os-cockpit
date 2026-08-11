---
type: "[[task]]"
id: TASK-0333
aliases: ["TASK-0333"]
title: "The charter note — goals, non-goals and taste constraints, drafted from the record, approved by the principal"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0077-The-Intent-Charter]]"]
parent: "[[FEAT-0077-The-Intent-Charter]]"
effort: M
depends: ["[[TASK-0332-DES-0003-Revised]]"]
blocks: []
related: []
tests: []
---

# The charter note

## Definition of Done

- An INTENT note per repo: what this project is for, what it must never become, and the taste rules its record has already paid for — first draft dispatched from the corpus's ADRs, phase close-outs and design-system notes, never invented.
- Approved through the actuator row; only an approved charter can be named by a delegation's `acceptance:` line.
- Amendment re-enters approval, and the charter's sha is stamped on every judgment made under it — the delegation-authority pattern, applied to intent.

## Done — 2026-08-11

`INTENT.md` at the repo root, `status: draft`, plus the gate in `charter.py`.

**I first recorded this as "not mine to write" and that was a misreading.** The DoD says the first draft is *"**dispatched** from the corpus's ADRs, phase close-outs and design-system notes, **never invented**"* — the prohibition is on inventing, not on drafting from the record. Assembling what the corpus already says, with citations, is exactly the task; approving it remains the principal's ([[REQ-0026]]).

So every clause carries where it came from:

- **What it is for** — [[REL-0001]]'s goal sentence verbatim, itself assembled from [[ADR-0009]], [[ADR-0020]], [[DES-0003]] and [[PHASE-028]].
- **What it must never become** — five rules, each from a decision already taken: no self-granted authority ([[ADR-0009]], [[REQ-0029]]), defaults that never grant ([[FEAT-0075]]/[[FEAT-0076]]), not an editor ([[ISS-0096]]), not a second list ([[ISS-0068]]), and no blocking gate on an unautomatable judgment.
- **The taste** — eight rules, each costing a correction and citing it: one border per object, fold on volume never meaning, a name is not a label, absent beats zero, one empty-state voice, a number says what it counts, evidence names its witness, an anchor never floats.

**The citations are the point.** A charter that summarised the record would be a second source that drifts; one that quotes it lets a reader check rather than trust, and makes anything that has drifted findable.

`charter.load()` reports it **unusable** today, correctly: *"charter is draft, not approved — a draft charter is no charter."* That is the honest state, and it is the same gate the delegation policy passes through, for the same reason: an agent that could write and approve the intent it is judged against is judging itself.
