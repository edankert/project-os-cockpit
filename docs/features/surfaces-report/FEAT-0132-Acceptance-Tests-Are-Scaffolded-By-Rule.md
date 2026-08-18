---
type: "[[feature]]"
id: FEAT-0132
aliases: ["FEAT-0132"]
title: "A feature gets its acceptance tests by rule, not by being asked — scaffolded at creation and gated at close-out"
status: backlog
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
requirements: ["[[REQ-0051-Coverage-Is-A-Rule-Not-A-Request]]"]
tasks: ["[[TASK-0522-Scaffold-Acceptance-Tests-With-The-Feature]]", "[[TASK-0523-The-Validator-Names-An-Uncovered-Feature]]", "[[TASK-0524-Backfill-Your-Trainers-Seventy-Five]]"]
related: ["[[ADR-0036-The-Sweep-Is-Withdrawn]]", "[[DES-0012-Tests-In-Two-Flows]]", "[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]"]
tags: [feature]
---

# The rule, not the request

Edwin, correcting the withdrawal: *"On the sweep … I expected you to automate creating acceptance tests for each feature, a project-os rule, not a manual step."*

**I read the instruction too narrowly.** [[ADR-0036]] withdrew the *asking* — an obligation that nagged a feature to describe its own impact — and that withdrawal stands. What it did not do is supply the thing that should have been there instead. Removing the ask without adding the rule leaves coverage to whoever remembers.

## The measurement that settles it

`your-trainer`: **75 of 102 features carry no acceptance check at all.** The sweep existed for eighteen months of project time and coverage reached 27%. A mechanism that asks a person at close-out is a mechanism that produces the coverage of whoever was paying attention that day.

## The shape

**At creation** — `feature-scaffold` emits a Tier 1 acceptance test alongside `FEAT-*` and `PLAN.md`, the way it already emits the plan. A feature arrives with the question *"how would somebody tell this works?"* already having a home, rather than a hole nobody sees.

**At close-out** — the validator names a feature reaching a terminal status with no test covering it. Not a nag while it is being built; a gate at the moment the claim *"this is done"* is made.

**Not a badge.** [[ADR-0027]] and [[ADR-0030]] both bear here: this must not become a per-check obligation, and it must not count checks. One error at one moment, on the feature.

## Where the tier fits

The scaffolded test is **Tier 1** by construction — TESTING.md: *"created when a feature is first implemented … one or more tests per feature."* That is the tier's own definition being performed rather than described.

## Acceptance

- [ ] Creating a feature creates at least one acceptance test note for it.
- [ ] A feature cannot reach a terminal status with nothing covering it, or the departure is recorded.
- [ ] No per-check obligation and no badge counts checks.
- [ ] `your-trainer`'s 75 uncovered features are backfilled or explicitly excepted.
