---
type: "[[feature]]"
id: FEAT-0108
aliases: ["FEAT-0108"]
title: "The release gate is a delta, not a census — what is new, what is chronic, what regressed, and what cannot be walked at all"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-16: 'start an independent functionality review with a goal to come up with some new/novel ways to support this new release functionality'", "Independent functionality review of PHASE-034, 2026-08-16 — ranked this first", "Measured against ../your-trainer's twelve tags on 2026-08-16"]
goal: "Stop reporting one number that has been true and ignored at every release this product has ever shipped. The same rows, grouped by what a person would actually do with them — walk it, decide about it, worry about it, or leave it alone because the screen it describes has not been built."
requirements: []
tasks: ["[[TASK-0446-The-Suite-At-The-Last-Tag]]", "[[TASK-0447-The-In-Flight-Rule-Reaches-Acceptance-Rows]]", "[[TASK-0448-A-Ticked-Row-Annotated-Re-Run-Is-Not-Evidence]]", "[[TASK-0449-Order-The-Walk-By-Its-Setup-Cost]]"]
design: ""
release: ""
depends: []
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[FEAT-0103-The-Gate-Is-Walkable]]", "[[FEAT-0107-Publication-Is-A-List-Of-Releases]]", "[[ISS-0173-The-Suites-Own-Ids-Are-Written-In-A-Form-Nothing-Reads]]", "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"]
tests: ["[[TST-0035-FEAT0108]]"]
---

# The gate is a delta, not a census

## The measurement this stands on

The functionality review ran this repo's **own** parser (`acceptance.parse`) against `git show <tag>:docs/tests/ACCEPTANCE_TESTS.md` for all twelve of `../your-trainer`'s tags. The result is in no note anywhere:

```
tag        Tier1 Tier2  BLOCKING AT SHIP
v1.1.0       70    14        1
v1.1.20      67    37       15
v1.1.53     167    94       85
v1.1.55     211   102      130
v2.0.0      314   154       22
v2.0.5      334   158       47
v2.1.0      334   158       47
v2.1.6      334   158       47
HEAD        347   158       60
```

**Twelve releases, twelve blocked ships.** The surface renders *"Release gate · 60 unchecked"* as though it were news. It is the steady state and has been for five months, and today's 60 is not even elevated — v1.1.55 shipped at 130.

A true sentence that has been correct and ignored twelve times is a sentence the reader has learned to skip. That is the defect. Not the number — the fact that the number carries no information about *this* release.

## What the 60 actually are

Diffed against v2.1.6, matched on `Item.name` within tier:

```
regressed (ticked at v2.1.6, unticked now) ....  0
brand new (added since v2.1.6, never walked) ... 13
chronic  (unticked at v2.1.6 AND now) .......... 47
```

With ages, by walking every tag:

```
 13  never present at any tag — new work
 25  unticked since v2.0.5   (85 days,  4 releases shipped around them)
 14  unticked since v2.0.0   (103 days, 5 releases)
  8  older still, one since v1.1.0 — 153 days, 11 releases
```

Three populations that mean completely different things and are today rendered as one list in document order.

- **New** is the release-day work. It is 13, it is finite, and it has never once been stated.
- **Chronic** is a standing decision, not a task. You have shipped four releases over the oldest 25 of them; the honest surface says so rather than presenting them as though today were the day.
- **Regressed at 0** is the sentence that says it is safe to ship — and it is the only one of the three that would ever be alarming.

**Zero regressions is not good news here.** `ACCEPTANCE_TESTS.md`'s last commit is `299114b2`, the v2.0.5 close-out on 2026-05-23. v2.1.0 and v2.1.6 both shipped without the suite being touched, so `TESTING.md` rule 2 — *any code change must uncheck the tests it overlaps* — was not executed for two entire releases. A regressed count of 0 currently means *nobody unchecked anything*, and the surface should not let that read as *nothing broke*. This is why [[TASK-0448]] is part of this feature rather than a nicety: the 54 `RE-RUN` annotations are the last time anyone did that bookkeeping, and 53 of them are still sitting under a tick.

## A third of the gate cannot be walked

Every one of the 60 blocking rows names a subject — 60 of 60, because [[ISS-0173]] taught `heading_refs` to read the bare form. The top two sections carry 33 of them:

```
20 rows → §1.25 Trainer Compatibility Verification (FEAT-0074)  status: backlog
13 rows → §1.6  Monetization & Licensing          (FEAT-0011)  status: done
 4 rows → §2.52 Compat-test must never leave app stuck (ISS-0268/0269)  both: fixed
```

**FEAT-0074 is `backlog`.** Those twenty checks describe a screen that does not exist. Asking a person to walk them is the self-re-arming badge [[ADR-0027]] refuses, sitting inside the feature built to honour it.

[[ADR-0028]] decision 3 already decided this case — *an obligation asks only while its subject is in flight* — and applied it to requirements and manual tests. It was never applied to acceptance rows, which are the population the ADR was written about. [[TASK-0447]] is not a new rule; it is finishing the application of one already accepted.

## What the page says instead

```
Release gate · 13 new · 27 chronic · 0 regressed · 20 quiet
  NEW — added since v2.1.6, never walked                            13   [ Walk ▸ ]
  CHRONIC — unticked at v2.1.6, shipped anyway                      27
      25 since v2.0.5 · 14 since v2.0.0 · 1 since v1.1.0
  REGRESSED — was ticked at v2.1.6, unticked now                     0
  QUIET — subject not in flight                                     20
      §1.25 Trainer Compatibility — FEAT-0074 is backlog       [ open ]
  STALE — ticked, but annotated RE-RUN and never re-walked          53   [ list ]
```

Per [[ADR-0028]] decision 5, derived silence must be inspectable: the quiet group expands and every row names its subject and that subject's status. Nothing is hidden, and the number that is hidden is stated.

## Acceptance criteria

- [x] The gate reports **new / chronic / regressed** against the newest `released` release's tag, diffed on check name within tier, not on number — `Item.number` shifts when a section is inserted, which is the same asymmetry `locate()` already relies on.
- [x] Chronic rows carry an **age** — the tag they were last ticked at, or first appeared unticked at, and the count of releases shipped since.
- [~] A blocking row whose subject resolves to a **not-in-flight** status is quiet, not blocking, and the badge count drops accordingly. **Reconciled, not met as written**: the gate contributes ONE obligation to any badge, never sixty ([[ADR-0027]]'s re-arming rule, and [[FEAT-0102]] built it that way on purpose), so quieting twenty rows cannot move a count that was always 1. What IS asserted is what the criterion was reaching for — `new + chronic + regressed + quiet == blocking == 60`, so the split accounts for every row and loses none.
- [x] The quiet group **expands** and each row names its subject and that subject's status, with a link to it.
- [x] A **ticked** row carrying a `RE-RUN (TASK-####: reason)` annotation is reported in its own group and is **not** counted as evidence.
- [~] The gate list can be **ordered by setup cost** using the burden tags the suite already carries, and document order remains available. **Reconciled — see [[TASK-0449]], cancelled.** `ACCEPTANCE_TESTS.md` carries no burden tags in any repo, and a scanner written for it was 6-for-6 false positives on `[Debug]` inside quoted workout names; `TST-0013`, which does carry them, has no tier headings so `parse` returns 0 items for it. The purpose is already served: [[FEAT-0102]] groups the gate by section, and section is the sitting.
- [x] A repo with **no tags** — eleven of the twelve — degrades to the census it renders today, with the reason stated, rather than to an empty page or a crash.
- [x] The historical line — *"twelve releases, median 26 blocking at ship; this is 60"* — appears once and is computed, not written.

## How this is verified

A `TST-*` that runs the delta against `../your-trainer`'s real tags rather than a fixture. The claim this feature makes is *about twelve real releases*, and a fixture cannot carry it. The fixture-based guards cover the degradation paths — no tags, no previous release, a section inserted above a check — because those are the cases the live repo does not exhibit.

Mutations to defeat, chosen now so they are not chosen later to confirm: diff on number instead of name; count a `RE-RUN`-annotated tick as evidence; treat a missing subject as in-flight; treat a missing subject as quiet.

## What this deliberately does not do

**It does not tick anything, and it does not untick anything.** Every group here is a read. The write paths stay where [[FEAT-0111]] puts them.

**It does not decide that chronic rows should be removed.** `TESTING.md` rule 5 says a verified release retires Tier 3 and clears `RE-RUN`; that has never been executed in twelve releases and it is a real question, but it is a question about the suite's lifecycle and not about what the gate should say today.
