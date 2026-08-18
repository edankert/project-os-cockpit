---
type: "[[task]]"
id: TASK-0494
aliases: ["TASK-0494"]
title: "Change replaces time: `invalidated_by:` retires the 90-day threshold for human-walked tests"
status: done
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0122-One-Human-Walked-Population]]"]
parent: "[[FEAT-0122-One-Human-Walked-Population]]"
effort: M
depends: ["[[TASK-0491-Tier-The-Twenty-Two]]"]
blocks: []
related: []
tests: []
---

# Change replaces time

A human-walked test currently goes stale by **time** — `last_verified` against a 90-day threshold — while an acceptance test goes stale by **change**, `invalidated_by:` against `verdict_date:`.

*"This walk was true 89 days ago"* is not a question anybody asks. *"Has anything changed underneath it"* is, and the corpus already records the answer. Time-based staleness is a proxy for change that a corpus with an invalidation field no longer needs.

`last_verified:` and `verdict_date:` are the same fact — the date of the walk — so they merge rather than coexist.

**Do not weaken the executable half.** [[REQ-0023]]'s reasoning stands for tests a machine runs: a passing run from a year ago is not evidence about today's system, and there `last_run` is the date that matters.

Done when: a human-walked test's staleness reads `invalidated_by:`, the two date fields are one, and `Stale · over N days` stops describing a population that has an invalidation field.

## Done 2026-08-18

`_test_is_stale` splits on execution rather than level. A test with a `command:` is graded by time against the project threshold, exactly as before. A test without one is graded by **change**: `invalidated_by:` against `verdict_date:`, and where both dates are known a walk recorded after the invalidating change answers it.

**The proxy was wrong in both directions**, which is the argument rather than tidiness: a walk untouched for a year is current if nothing it covers has moved, and one performed yesterday is stale if something has.

Guarded by `test_a_human_walked_test_does_not_go_stale_by_time` — the same note, the same date and the same 30-day threshold as the `stale` case beside it, with only the `command:` differing.
