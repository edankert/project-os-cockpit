---
type: "[[plan]]"
title: "Plan — one human walk"
status: draft
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: []
implements: ["[[FEAT-0122-One-Human-Walked-Population]]", "[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]"]
related: ["[[ADR-0033-A-Manual-Test-Is-An-Acceptance-Test]]", "[[PHASE-036-One-Human-Walk]]", "[[ISS-0205-The-Sweep-Writes-Notes-A-Migrated-Repo-Cannot-Read]]"]
---

# Plan — one human walk

## The gate

**[[ADR-0033-A-Manual-Test-Is-An-Acceptance-Test]] is `proposed`.** No note changes level or tier until Edwin accepts it — the gate [[ADR-0030]] and [[ADR-0031]] both used.

## [[ISS-0205]] does not wait

The sweep is writing invisible notes **now**, in a repo where the obligation is live on 1 feature here and 4 in `your-trainer`. It is not gated on the ADR and should land first.

## Order

1. **[[TASK-0493-One-Who-Runs-This-Predicate]]** — ungated, and it makes the migration's before/after measurable.
2. **[[TASK-0491-Tier-The-Twenty-Two]]** — the judgement per note, including splitting `TST-0011` rather than folding it in whole.
3. **[[TASK-0492-Retire-The-Manual-Run-Obligation]]** — and this is the dangerous one: the badge must not go from 5 to 60.
4. **[[TASK-0494-Change-Replaces-Time-As-Staleness]]**.
5. Then the surfaces, [[TASK-0495-One-Verb-For-One-Act]] → [[TASK-0498-The-Release-Page-Shows-What-Is-Outstanding]], with [[TASK-0496-The-Tier-Is-In-The-Address]] before the two that depend on linking to a filtered view.

## The two things most likely to go wrong

- **The badge.** [[ADR-0027]] forbids per-check obligations, and this phase retires the obligation that currently keeps the manual population visible. Between those two, the failure mode is 669 rows arriving on a badge. Measure per repo, before and after, and refuse to proceed on a rise.
- **Deciding [[ISS-0200]] by accident.** Touching every note in the corpus is exactly when somebody folds in the marks-versus-words question silently. It is a separate decision with its own evidence.
