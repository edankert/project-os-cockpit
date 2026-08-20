---
type: "[[issue]]"
id: ISS-0248
aliases: ["ISS-0248"]
title: "`RESTING_STATES` and `NOT_YET_BUILT` give opposite answers about the same subject, and branch order decides which wins — a check on a `planned` feature is counted as work somebody owes"
status: open
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
source: ["independent review, fifth pass, 2026-08-20"]
severity: medium
component: cockpit
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0247-The-Tests-View-Lost-Its-Quiet-Group]]", "[[ADR-0028-Publication-Is-The-Third-Phase]]", "[[REQ-0059-One-Predicate-Per-Question]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]"]
tests: []
---

# One question, two sets, and the branch order casts the vote

## The split

```
RESTING_STATES  = COMPLETED_STATUSES | {backlog, deferred}
NOT_YET_BUILT   = {backlog, deferred, draft, planned, proposed}
```

`planned`, `proposed` and `draft` are in the second and not the first. Both are asked about the same thing — *is this subject something a person is being asked about* — and they disagree.

## What it does

`_tests_groups` tests `_owed_flag` (which reads `RESTING_STATES`) **before** the quiet bucket (which reads `NOT_YET_BUILT`). One fixture per status, identical but for the status:

| subject | lands in |
|---|---|
| `FEAT-0001` at `backlog` | **quiet** |
| …at `deferred` | **quiet** |
| …at `planned` | `needs-you` |
| …at `proposed` | `needs-you` |
| …at `draft` | `needs-you` |

So **[[ISS-0247]] describes the bucket over five statuses and it can reach two.** A check verifying a `planned` feature is still *"counted as work somebody owes"* — that issue's own opening complaint, surviving its own fix.

## Why this is the fourth correction to one bucket

[[ISS-0247]]'s bucket has now been wrong four times, each in a different way, and every fix was correct about the case it was shown and silent about the case it was not:

1. quieting **finished** subjects (reverted before landing)
2. quieting **regression** checks whose issue is `deferred`
3. quieting a check with a **built non-feature** subject beside an unbuilt feature
4. this — **three of its five stated statuses unreachable**

The reviewer's conclusion is the one worth keeping: *"that is an argument for enumerating a predicate's stated domain and testing every member of it, not for more care."* `test_the_quiet_buckets_reachable_domain_is_exactly_two_statuses` now does exactly that.

## Latent, and the population exists

**Zero rows** in either corpus where the quiet branch would fire but `owed` claims first. But **24 features sit at `planned` fleet-wide**, so the shape is populated and one `ready` check against any of them produces it.

*(A false instance was withdrawn in the same review: `TST-0024` looked like one under a crude heuristic and is not. Its `draft` requirements are subordinated to a `backlog` feature by the [[ISS-0202]] rule, so it reaches `quiet` correctly.)*

## Two honest resolutions, and this is a decision

1. **Reconcile the sets.** *Not in flight* and *not yet built* become one predicate, or the difference between them is written down and defended. That is an [[ADR-0028]] amendment, not a patch — and it moves the obligations badge, not only this pane.
2. **Narrow the stated rule** to the two statuses the bucket can reach, and say why the other three are claimed first.

What must not stand is the current state: a branch documented over five statuses that fires on two. The test pins the domain so the note and the code cannot drift apart again while the decision waits.

## Done when

- [ ] The sets are reconciled, or [[ISS-0247]]'s rule is narrowed to `{backlog, deferred}` with the precedence recorded.
- [ ] Whichever, `test_the_quiet_buckets_reachable_domain_is_exactly_two_statuses` is updated **with** it — it is written to fail if the domain moves silently.
- [ ] If the sets are reconciled, the obligations badge is re-measured: `RESTING_STATES` is not local to this pane.
