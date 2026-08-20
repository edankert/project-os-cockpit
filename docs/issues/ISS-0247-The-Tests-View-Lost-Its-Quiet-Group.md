---
type: "[[issue]]"
id: ISS-0247
aliases: ["ISS-0247"]
title: "The tests view has no quiet group and a comment says it does — a check whose subject is not in flight is counted as outstanding work, which inflates the one number that view exists to make honest"
status: open
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
source: ["constructed while re-reading FEAT-0128's criteria, 2026-08-20"]
severity: high
component: cockpit
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[FEAT-0128-The-Tests-View-Leads-With-The-Work]]", "[[TASK-0508-Collapse-Resting-To-A-Line]]", "[[ISS-0241-The-Section-Head-Restates-Its-Own-Arithmetic]]", "[[ADR-0028-Publication-Is-The-Third-Phase]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]"]
tests: []
---

# A group two places claim exists, and one place builds

## The claim

`nav_payload` appends the quiet group for every view **except** those that gather their own:

```
# `tests` builds its own — see `_tests_groups` — because that view
# gathers instead of receiving a `Needs you`.
if m not in _VIEWS_THAT_ALREADY_GATHER:
    groups = groups + suppressed_group(index, m)
```

[[FEAT-0128]] carries it as an acceptance criterion — *"Resting is one collapsed line"* — with a measurement: **10 rows in `your-trainer`, 3 here**. [[TASK-0508]] is `done`.

## `_tests_groups` does not build it

Its buckets are `needs-you`, `feature`, `regression`, `automated`, `broken-command`, `retired`. There is no quiet or resting group among them, and none is added afterwards.

**Constructed, because neither corpus can produce the case today** — a `ready` test covering a `backlog` feature, which is precisely *subject not in flight*:

| | |
|---|---|
| `obligations.suppressed_items(index)` | `{'tests': 1, …}` — the row **is** identified as quiet |
| the group it lands in | **`Feature tests · 1 of 1 outstanding`** |
| suppressed groups in the tests nav | **none** |

So the predicate fires and the routing throws the answer away.

## Why this is worse than a missing group

**The row is counted as outstanding.** [[ISS-0241]] made the section head state what is owed; [[ISS-0242]] made it count what the section holds. Both are correct about the population they are given — and the population silently includes checks [[ADR-0028]]'s in-flight rule says nobody is being asked for.

So the one number that view exists to make honest is inflated by exactly the rows the quiet rule was built to remove. That is [[ADR-0027]]'s complaint — a badge counting what does not need a person — arriving through the section head instead of the badge.

## Why both corpora read zero

`suppressed_items` returns nothing for either repo today, which is why this survived: **the case cannot be produced from the corpus, so no amount of looking at the app would show it.** It took constructing the input. FEAT-0128's 10-and-3 were real when measured; the population has since emptied, and the emptiness hid the defect rather than being caused by it.

## Done when

- [ ] `_tests_groups` builds the quiet group, or the comment claiming it does is deleted and [[FEAT-0128]]'s criterion is retired with a reason.
- [ ] A quiet check is **not** counted in a section head's outstanding number.
- [ ] Guarded on **constructed** input — a `ready` test covering a `backlog` feature — because neither corpus can produce one, and a guard built on the corpus would pass against this defect forever.
