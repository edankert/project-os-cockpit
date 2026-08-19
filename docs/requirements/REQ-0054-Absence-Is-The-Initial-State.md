---
type: "[[requirement]]"
id: REQ-0054
aliases: ["REQ-0054"]
title: "Absence is the initial state — a check with no entry for a platform is owed on that platform, and nothing declares applicability"
status: draft
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
priority: high
scope: "acceptance queries and gate"
implements: "[[FEAT-0135-Everything-Downstream-Is-A-Query]]"
acceptance:
  - "[ ] A check with no terminal entry for platform P reports as owed on P, with no field anywhere declaring applicability."
  - "[ ] Adding a platform to a repo requires no note edit, no schema change and no backfill."
  - "[ ] There are exactly two ways a check leaves a platform's owed set without being run — `na` and `excused` — and both carry a date, an author and a required reason."
  - "[ ] An `excused` expires when its ledger seals; the check is owed again on the next release with no action by anybody."
  - "[ ] An `na` persists until invalidated, through the same machinery that re-arms a stale pass."
  - "[ ] `blocked` does not clear the gate, and a test proves it."
  - "[ ] The gate delta against today's gate is measured and recorded per repo before that repo migrates."
covers: []
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ISS-0208-Retire-The-Tier-Rule]]", "[[ISS-0206-A-Check-Cannot-Belong-To-A-Release]]"]
tags: [requirement]
---

# The absence is the honest initial state

## Statement

Applicability **shall not** be declared. A check with no terminal entry for a platform **shall** be reported as owed on that platform.

There are exactly **two** exits without a run, and they differ in whether the exception comes back: an **`na`** event (cannot apply here — persists until invalidated) and an **`excused`** event (not done this cycle, by decision — **expires when its ledger seals**). Both carry a date, an author and a required reason. A check that could not be run for an environmental reason is **`blocked`** and still gates.

## Why `excused` is a separate value, and why it must expire

`na` and `excused` differ in exactly one property: **whether the exception comes back.** Re-declaring `na` every release is the maintained-matrix failure this phase exists to remove, so it persists. `excused` is a statement about one release, and if it persists then a check excused once is excused forever.

**That is what the code does today.** `Item.excepted` is `mark in {canceled, -}` read from frontmatter and scoped to nothing — while the comment directly above that set still describes the per-release property [[ADR-0029]] removed when the exception moved from `[!]` to `[-]`. Latent, not live: `mark: canceled` is written 0 times in all three repos.

## Why not an `applies:` field

A per-note × per-platform applicability field is `PARITY_MATRIX` hiding in frontmatter — hand-maintained, per-note, and rotting by the mechanism that matrix already demonstrated eight times in a single device session (`ISS-0359`..`ISS-0366` in `your-trainer`, all on rows the matrix called DONE).

The absence costs nothing to maintain and cannot be wrong. Add a platform and every check is immediately owed there, which is the correct starting position and the one a maintained field would have to be edited 671 times to reach.

## The criterion that is not optional

**Criterion 5 gates the other four.** This requirement makes one repo's gate substantially tighter — 513 Android passes stop counting toward an iOS release — and a gate that moves without somebody having seen the number is the failure [[ISS-0208]] is still open about. Measure, state, then migrate.

## Acceptance criteria

- [ ] No entry for a platform means owed on that platform.
- [ ] A new platform needs no edits anywhere.
- [ ] Two exits, both requiring date, author and reason.
- [ ] `excused` expires at the seal.
- [ ] `na` persists until invalidated.
- [ ] `blocked` still gates, proved.
- [ ] Per-repo gate delta measured and recorded before migration.
