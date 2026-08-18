---
type: "[[task]]"
id: TASK-0501
aliases: ["TASK-0501"]
title: "Prove the derived gate reproduces the tier gate, per repo, and only then retire the tier rule"
status: done
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0124-Gating-Is-Derived-From-Covers]]"]
parent: "[[FEAT-0124-Gating-Is-Derived-From-Covers]]"
effort: M
depends: ["[[TASK-0500-Derive-The-Gate-From-Covers]]"]
blocks: []
related: []
tests: []
---

# Prove, then retire

**Per repo, before and after, and equal:** blocking counts of **0 / 56 / 60** for `project-os-cockpit` / `your-sudoku` / `your-trainer` — and **the same set of blocking items, not the same number.** A count can match while the membership has rotated, which is the failure mode a count cannot see.

**This task exists because of specific failures, not as a formality.** Twice on 2026-08-18 a change reported success having quietly changed nothing — a regex that needed a trailing newline, and a script that died before writing — and once a gate went silent in a repo nobody was looking at, when `your-trainer`'s stale count sat at 0 because a field had been emptied. **A gate that gets quieter during a migration is the shape of failure this project has already paid for.**

So the assertion is not *"the derived gate works"*. It is *"the derived gate and the tier gate name the same items, in every repo, and here is the diff where they do not"*.

Only then does the tier rule go — and `tier:` survives afterwards only if it earns its place as a **lifetime** field ([[ADR-0034-Three-Axes-Not-One-Word]] decision 6), not as a gate.

Done when: equivalence is proven per repo by membership, the tier rule is removed, and the phase's own gate figures are unchanged.

## Done 2026-08-18

**Equivalence proven by membership, not by count** — `test_the_derived_gate_names_the_same_items_as_the_tier_rule`, parametrised over all three suites, diffs the two sets and reports which rule names what. 0 / 56 / 60 blocking, identical sets.

**The tier rule is not deleted; it is subsumed.** `blocking()` calls `blocking_for(None)`, so there is one predicate with the tiers filtered inside it rather than two rules to keep in step. That is the same reasoning [[ADR-0032]] gives about the verification link: two encodings of one fact drift, and the drift is silent.

**The uniform gate found six true things and ships as a warning.** `your-sudoku`'s FEAT-0025 is `done` with six checks covering it that nobody has walked. Erroring on day one would take a green repo red for a rule it had no chance to satisfy, so `VERIFY-ACCEPTANCE` carries a promotion date of 2026-11-20 — ADR-0011 clause 3, the same way `TEST-ENTRYPOINT` shipped.
