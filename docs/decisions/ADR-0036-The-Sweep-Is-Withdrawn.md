---
type: "[[decision]]"
id: ADR-0036
aliases: ["ADR-0036"]
title: "The acceptance sweep is withdrawn — the obligation, the page and the write path — until a need for it returns"
status: accepted
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
decided: 2026-08-18
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ADR-0030-One-Note-Per-Acceptance-Check]]", "[[FEAT-0115]]", "[[DES-0012-Tests-In-Two-Flows]]"]
tags: [decision]
---

# The sweep is withdrawn

Edwin, 2026-08-18: *"I would like to remove the sweep functionality, until we find a need for it later."*

## What it was

[[FEAT-0115]] / TASK-0467, built during [[PHASE-035]]. An obligation on an in-flight feature asking *what did this change do to the acceptance suite?*, a `~sweep/<FEAT-id>` page, and a write path that added checks, wrote `invalidated_by:` on the ones a change overtook, and stamped `acceptance_impact:` on the feature — in one commit.

It was built from a real, measured problem: **54 rows across the fleet carried a hand-written `RE-RUN (…)` and all 54 were still ticked**, because unticking destroyed the only record the check had passed.

## Why it goes anyway

**The problem it was built for is no longer in the corpus.** Those 54 annotations were cleared on Edwin's instruction. Measured 2026-08-18: `mark: rerun` is **0** in every repo and `invalidated_by:` is **0** in every repo. The sweep's entire output population is empty.

**What is left is the asking.** Six features owed a sweep on the day this was written, and **five were created that afternoon** for [[PHASE-037]]'s own surfaces work — none of which touches an acceptance check. The honest answer for each is `none — reason`, five times. An obligation whose common case is "nothing to do, say so" is the [[ADR-0027]] failure the three-state field was designed to avoid, arriving by a different route: the field avoids nagging *after* you answer, and does nothing about being asked in the first place.

**And the design moved.** [[DES-0012]] establishes that the suite is organised by **surface**, and that Tier 3's real obligation is release-time housekeeping — promote or remove — not per-feature sweeping. A mechanism keyed on features is aimed at the wrong subject under that design.

## Decision

Withdraw it entirely: the obligation, the registry rows, the `~sweep/` route and page, the write path, and `acceptance_impact:` as a *read* field.

**`acceptance_impact:` values already written are left in place.** They are a record that somebody considered the question on a date, which stays true whether or not anything asks for it. Deleting them would destroy history to tidy a schema.

## Consequences

- The `Sweep` verb and its `action` leave the obligation registry; no badge counts it.
- **Something does replace it, and it is not another ask.** Edwin, on reading this: *"I expected you to automate creating acceptance tests for each feature, a project-os rule, not a manual step."* Withdrawing the obligation was right; leaving the gap was not. [[FEAT-0132]] scaffolds a Tier 1 acceptance test **with the feature** and gates the terminal status at close-out — a rule, running whether or not anyone remembers.

  The measurement that settles which of the two works: `your-trainer` has **75 of 102 features with no acceptance check at all**, produced while the sweep existed. A mechanism that asks a person at close-out produces the coverage of whoever was paying attention that day.

- When *invalidation* matters again — and under [[DES-0012]] it will, because the re-run tracking line has nothing to track without it — the replacement should be keyed on the **surface** a change touched, not on the feature.
- This is the first built feature this project has withdrawn. Recorded as a decision rather than a deletion so the reasoning survives, and so re-introducing it starts from the measurement above rather than from scratch.
