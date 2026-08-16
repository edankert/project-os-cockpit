---
type: "[[task]]"
id: TASK-0449
aliases: ["TASK-0449"]
title: "Order the walk by its setup cost, using the burden tags the suite already carries on 107 rows"
status: cancelled
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0108-The-Gate-Is-A-Delta-Not-A-Census]]", "Independent functionality review of PHASE-034, 2026-08-16"]
parent: "[[FEAT-0108-The-Gate-Is-A-Delta-Not-A-Census]]"
effort: M
depends: ["[[TASK-0446-The-Suite-At-The-Last-Tag]]"]
blocks: []
related: []
tests: []
---

# Order the walk by its setup cost

## Why

The gate hands over its rows in document order. A person with a trainer in the garage needs them in **setup order**, because the expensive precondition is standing up hardware, not reading a check. Ordering is nearly free and it is the difference between a walkable list and a wall.

And the schema exists rather than needing invention. `TST-0013` tags all 107 of its rows:

```
[App] 98 · [Trainer] 21 · [Strava] 8 · [icu] 6 · [AI] 6 · [HRM] 4 · [Family] 4 · [Net] 2 · [2-platform] 2
```

`ACCEPTANCE_RUN_PLAN_v2.1.1.md` goes further and is entirely hand-built: an `A`/`B`/`C` burden column and phases ordered by it — automated first, no-hardware next, real trainer after, store verification last.

## What

Read the bracket tags where the corpus carries them, group the blocking rows by burden, and order least-costly first. Document order stays available and stays the default until this is proven.

## What this must not become

**No time estimates.** The run plan's `~30 min` / `~45 min` numbers are a person's guesses, and rendering them would harden a guess into false precision the tool appears to vouch for. Order, not schedule.

**No new tag vocabulary.** If a suite carries no burden tags — which is every suite in the fleet except TST-0013 — the order is unchanged and nothing is displayed. A heuristic that infers burden from prose is explicitly out of scope; it would be wrong quietly.

## A finding to record while doing this

The suite's `## Manual Test Environment Breakdown` is a hand-maintained aggregate claiming **≈120 manual rows** against a file with 579 checkboxes, and `TST-0013` itself says "~120 rows" while holding 107. Two hand-counted aggregates, both drifted. This is the canonical case for computing an aggregate rather than maintaining one — and computing it is a side effect of this task, not extra work.

## Done when

- [~] burden tags parsed where present, and the count per tag computed rather than read from any prose
- [~] blocking rows can be ordered least-costly-first, and document order remains available
- [~] a suite with no burden tags renders in document order with no burden column and no placeholder
- [~] a row with several tags takes the **most** expensive, not the first
- [~] no time estimate appears anywhere in the output
- [~] the computed row count for `../your-trainer` is asserted, and the drift from the two hand-written aggregates recorded

## Cancelled 2026-08-16 — the mechanism is not in the corpus and the purpose is already served

Two measurements, both taken **before** anything shipped, and either alone is fatal:

1. **`ACCEPTANCE_TESTS.md` carries no burden tags.** The document the gate reads has zero, in every repo in the fleet. A scanner written for it found six and **all six were false positives** — `[Debug]` lifted out of a quoted workout name, *"verify no workouts with `[Debug]` prefix appear"*. A 6-of-6 false-positive rate on the only corpus it would ever run against is not a heuristic that needs tuning.
2. **`TST-0013` is not a suite.** It has no `# Tier N` heading, so `acceptance.parse` yields **0 items** for it. The one document carrying real tags is a `TST-*` read by `manual_test_steps`, which the gate never sees. The two halves of this task's premise live in different documents read by different parsers.

This task's own scope note said a heuristic inferring burden from prose was out of scope because *"it would be wrong quietly"*. It would have been, and the scanner was written and deleted rather than argued about.

**The purpose is not lost.** *Do not make someone stand a trainer up twice* is already served: [[FEAT-0102]] groups the gate by section, and the section **is** the sitting. What this task would have added on top is a second ordering over a field that does not exist.

`cancelled`, not `deferred`: deferring says *later*, and nothing here gets truer with time. If a suite ever adopts the tag convention, that is a new task against a corpus that has one.
