---
type: "[[issue]]"
id: ISS-0247
aliases: ["ISS-0247"]
title: "The tests view has no quiet group and a comment says it does — a check whose subject is not in flight is counted as outstanding work, which inflates the one number that view exists to make honest"
status: fixed
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

## Corrected within the hour — it is live, not latent, and the obvious fix is wrong

**This note first said the corpus could not produce the case.** It can: `suppressed_items` returns **3 for `project-os-cockpit` and 4 for `your-trainer`**. My earlier zero came from looking for a *rendered* suppressed group — which `_tests_groups` never builds — and reading its absence as an empty population. The rows have been counted as outstanding all along.

### And adding the bucket is not the fix

Tried, measured, reverted. Routing `_owed_flag(...)["suppressed"]` into a `Quiet` group moves the section heads — `3 of 32 outstanding` becomes `all 29 done` here — and **two of the three rows should not have moved**:

| row | subject | verdict |
|---|---|---|
| `TST-0024` | `FEAT-0099` = `backlog` | correctly quiet — nobody owes a check on an unbuilt thing |
| `TST-0029` | `FEAT-0103` = **`done`** | **shipped and unverified** |
| `TST-0030` | `FEAT-0103` = **`done`** | **shipped and unverified** |

The in-flight rule suppresses on *not in flight*, and a **terminal** subject is not in flight either. So the bucket would hide exactly the population [[TASK-0523]]'s `FEATURE-UNCOVERED` exists to surface: work that shipped with nothing verifying it.

**That is the same defect this phase keeps finding, one level up** — a rule applied to a population it was not written for. [[ADR-0028]] decision 3 was written about subjects that *do not exist yet*; reusing it for subjects that are *finished* inverts what it means.

### So the real fix is narrower than the group

Quiet must mean **subject not yet built** — `obligations.ids_are_unbuilt`'s question, which the release gate already asks and which returns `backlog`/`planned`/`deferred`/`draft`/`proposed` only. `TST-0029` and `TST-0030` stay outstanding, because they are.

## Done when

- [x] `_tests_groups` builds the quiet group on `ids_are_unbuilt`.
- [x] Unbuilt subject → quiet; **finished subject → still outstanding**.
- [x] Both cases guarded, and **the reverted attempt is the mutant**: swapping back to `_owed_flag`'s `suppressed` fails three tests.
- [x] `nav_payload`'s comment is true now — `tests` does build its own.

## Fixed 2026-08-20

The bucket asks `obligations.ids_are_unbuilt` over the check's `covers:` — the same question the release gate asks, rather than a second reading of *quiet*.

**What moved, measured on both repos:**

| | before | after |
|---|---|---|
| `project-os-cockpit` Feature tests | `3 of 32 outstanding` | **`2 of 31 outstanding`** |
| …and a `Quiet · no feature in flight` group | absent | **1 row — `TST-0024`** |
| `your-trainer` Feature tests | `49 of 411 outstanding` | **unchanged** |

`TST-0024` covers `FEAT-0099` at `backlog` and is genuinely not owed. **`TST-0029` and `TST-0030` stay counted** — they cover `FEAT-0103`, which is `done`, so they are shipped-and-unverified and belong in the number. `your-trainer` moves not at all: none of its four `suppressed` rows names an unbuilt subject.

That last line is the whole difference between this fix and the one that was reverted, and it is why the guard asserts the **finished** case as well as the unbuilt one — a test with only the `backlog` case passes both versions.
