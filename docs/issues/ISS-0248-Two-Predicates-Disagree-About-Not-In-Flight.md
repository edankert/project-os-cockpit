---
type: "[[issue]]"
id: ISS-0248
aliases: ["ISS-0248"]
title: "`RESTING_STATES` and `NOT_YET_BUILT` give opposite answers about the same subject, and branch order decides which wins — a check on a `planned` feature is counted as work somebody owes"
status: declined
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

## 2026-08-20 — the decision was taken on a false measurement, and reverted

Edwin chose **narrow the words to `{backlog, deferred}`** on my statement that it *"changes nothing either way — zero checks in either repo would move."* **That statement was wrong**, and the narrowing is reverted unmade.

### What I measured, and what I claimed

I measured *"how many rows would **become** quiet if the set were **widened**"* — that is genuinely **0**. I then reported it as *"changes nothing **either way**"*.

The other direction was never measured. **Narrowing removes one live row.** `TST-0024` (*Remote SSH workspace walk*) covers `FEAT-0099` at `backlog` **and** `REQ-0035` / `REQ-0036` at `draft`. `ids_are_unbuilt` is an **all**-quantifier, so `draft` being in the set is what makes that row quiet. Take `draft` out and the row leaves `Quiet` and lands in `Feature tests · outstanding` — counted as work somebody owes, for a feature nobody has started.

That is precisely the complaint [[ISS-0247]] was filed about. The "safe, documentation-only" option was the one that changes behaviour, and the direction it changes it in is the wrong one.

**An asymmetric measurement reported as symmetric.** Third of this species today, and the same shape as the other two: measure one direction, state both.

### And the premise of this issue is now in doubt

This note says three statuses are unreachable, from an enumeration that only ever tested a **single** subject per check:

| shape | lands in |
|---|---|
| `FEAT@draft` alone | `needs-you` |
| `FEAT@backlog` alone | `quiet` |

But `ids_are_unbuilt` quantifies over **every** ref, and `TST-0024` is quiet in the live corpus with three subjects. So `draft` is load-bearing in combination even though it is unreachable alone — which the single-subject enumeration cannot see, and which neither I nor the independent review noticed.

*(A constructed three-subject fixture did **not** reproduce `TST-0024`'s bucketing, so the mechanism is not yet fully explained and no cause is asserted here. What is measured and certain: with `draft` in the set that row is quiet, without it that row is not.)*

**So this issue needs re-deriving before it is decided again.** Its stated defect — *"the domain is five and the reach is two"* — is true of single-subject checks and false of the corpus's actual one.

### State

Code **unchanged**: `NOT_YET_BUILT` still `{backlog, deferred, draft, planned, proposed}`, one quiet row, suite green. Nothing was committed. The decision is Edwin's again, on numbers that are now right.

## Re-derived 2026-08-20 — DECLINED, the premise was wrong

**The two sets do not answer the same question, and the difference between them is load-bearing rather than a bug.**

### The mechanism, traced end to end

| predicate | quantifier | set |
|---|---|---|
| `ids_in_flight` (via `_owed_flag`) | **ANY** subject in flight | `RESTING_STATES` |
| `ids_are_unbuilt` (the quiet branch) | **ALL** subjects unbuilt | `NOT_YET_BUILT` |

Different quantifiers over different sets, answering different questions — *"is there anything here somebody could act on?"* and *"is every one of these things not yet built?"* That is not [[REQ-0059]]'s one-question-two-implementations. It is two questions.

And `ids_in_flight` carries a third clause this note never accounted for ([[ISS-0202]]): **a `requirement` whose `implements:` names a resting feature does not vote independently**, because a `draft` requirement of a `backlog` feature is the same fact counted twice.

### Why the enumeration said three statuses were unreachable

Because it only ever tested a check with **one** subject. Reproduced:

| shape | `in_flight` | lands |
|---|---|---|
| `FEAT@draft` alone | True | `needs-you` |
| `FEAT@backlog` alone | False | `quiet` |
| `FEAT@backlog` + two `REQ@draft` **without** `implements:` | True | `needs-you` |
| `FEAT@backlog` + two `REQ@draft` **with** `implements:` | False | **`quiet`** |

The last row is `TST-0024` exactly. `draft` is unreachable as a *sole* status and **load-bearing in combination**, because `ids_are_unbuilt` is an ALL-quantifier: remove `draft` from `NOT_YET_BUILT` and that row fails the test, leaves `Quiet`, and starts asking somebody to hand-walk a remote-SSH procedure for a feature nobody has started.

`obligations.py` already says so, in the ISS-0202 comment: *"Measured across all twelve repos: this quiets exactly ONE note, `project-os-cockpit`'s TST-0024."* **The answer was written in the code the whole time and neither I nor the independent review read it before filing.**

### Outcome

**Declined. No change to either set.** Narrowing breaks `TST-0024`; widening moves nothing (0 rows in either corpus) and would weaken the ANY rule that keeps four other tests visible, including `your-trainer`'s iOS parity walk.

What was genuinely wrong was **this note's own claim**, and the test that encoded it. `test_the_quiet_buckets_reachable_domain_is_exactly_two_statuses` asserted the reachable domain is `{backlog, deferred}` — true of single-subject checks, false of the corpus — and its docstring told the next reader the other three were dead. Corrected, with the combination case added so the arity error cannot recur.

### The lesson, which is the same one four times today

**An enumeration is only as good as its arity.** Every member of the stated domain was tested, and every case had one subject, so a predicate quantified over *lists* was measured with *singletons*. Testing every member of a domain is not the same as testing every shape of input.
