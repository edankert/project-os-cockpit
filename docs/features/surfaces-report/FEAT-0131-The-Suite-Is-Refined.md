---
type: "[[feature]]"
id: FEAT-0131
aliases: ["FEAT-0131"]
title: "The suite is refined — Tier 2 and Tier 3 checks that no longer need re-executing are closed, per TESTING.md's own removal rules"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
requirements: ["[[REQ-0050-A-Check-That-Cannot-Regress-Is-Closed]]"]
tasks: ["[[TASK-0517-Close-The-Tier-Three-Holding-Pen]]", "[[TASK-0518-Review-Tier-Two-For-One-Time-Fixes]]", "[[TASK-0525-Relink-Tier-Two-To-Its-Issue]]", "[[TASK-0526-A-Tier-Two-Check-Rests-With-Its-Issue]]"]
related: ["[[DES-0012-Tests-In-Two-Flows]]", "[[ISS-0208-Retire-The-Tier-Rule]]"]
tags: [feature]
---

# Closing what cannot regress

Edwin: *"Refine the current TSTS and close any Tier 3 or 2 which do not need to be re-executed because of automation or because of one time bug fixes."*

**This is `your-trainer`'s own rule, unperformed.** `tools/instructions/TESTING.md` already says a Tier 3 test is removed after a verified release when it is covered by passing unit tests, or the fix is a stable one-liner, or the scenario was a one-time data/config fix. And the unit-test-replacement rule says a Tier 2 test moves to Tier 3 once unit tests cover the same logic, with a note naming the class, *"remove after the next release."*

Measured 2026-08-18: **66 of Tier 3's 74 checks** sit in an area called `"Moved from Tier 1 / Tier 2 — Fully Automated"`. That is the holding pen, full, with the removal step never taken. `your-trainer` carries 579 checks; this is the largest single population that should not be there.

## Two passes, different confidence

**Tier 3's holding pen is mechanical** — the area name states why each is there, and TESTING.md states what happens next. High confidence, and it is 66 of 74.

**Tier 2 belongs to its issue.** Edwin: *"tier 2 should be associated with their issue, there should be very few tier-2 items active at any given time, so should not overwhelm."* TESTING.md already says each Tier 2 test *"references the `ISS-*` that created it"* — measured, **85 of 158 actually do**, so 73 have lost the link that explains why they exist. Restoring it is what makes Tier 2 groupable by issue rather than by 46 one-off scenario names, and it is what makes "few active at a time" true rather than aspirational: an issue is closed, and its guard goes quiet with it.

**The rest of Tier 2 is a judgement per check.** Each references the `ISS-*` that created it, and the question — *could this regress?* — is answerable only by reading the fix. TESTING.md's default for Tier 2 is **never removed**, so the burden is on closing, not on keeping. 158 checks; expect the number closed to be small.

## What "closed" means

`status: retired` on the note, with the reason recorded. Not deletion — [[ADR-0008]] and LIFECYCLE both forbid removing completed notes, and a retired check is the record that the scenario was once verified and why it stopped mattering.

## Acceptance

- [x] Every Tier 3 check in the holding pen is promoted, retired with a reason, or explicitly kept — **kept, with the real area recovered**. [[TASK-0517]]: 66 at `your-trainer` HEAD, 60 in its working tree (basis stated, because an earlier version of that note reported one as the other). All 60 matched a parking-bay row by title — **47** via a `§N.M` reference resolving to a real section heading, **13** via the `###` sub-heading they were parked under, **0 unresolved**. None was retired. ⚠️ **The corpus change is uncommitted** — see the caveat below.
- [x] Tier 2 is reviewed check by check; each closure names the automation or the one-time fix that justifies it — **read individually, and there were no closures**. [[TASK-0525]] read all 73 and found the premise false: all 73 derive to `feature` under [[ADR-0039]], so `tier: 2` on them is dead metadata and assigning an `ISS-*` would invent a defect to justify a retired tier. [[TASK-0518]] then decided *no retirements* (Edwin, 2026-08-20). **The clause about closures is satisfied vacuously — nothing closed** — and that is stated rather than presented as compliance.
- [x] The gate number before and after is stated, per repo — [[TASK-0517]]: `your-trainer` **581 items / 59 blocking, before and after**, re-measured with an **indexed** loader after review caught [[ISS-0213]] simulating with an index-less one where the numbers *could not move*; `newly blocking: none`, `no longer blocking: none`. Re-measured again 2026-08-20 for the six-check relink: **59 → 59**. This repo holds no acceptance suite of its own, so it has no gate number to state.


## Closed 2026-08-20 — with one caveat that is not a detail

All four tasks are `done` and all three criteria are met. **But criterion 1's evidence lives in no commit.**

[[TASK-0517]]'s own closing line: *"Left **uncommitted** in `your-trainer`, which already carries 655 modified files."* The excavation that recovered 60 areas from a deleted document is real, was verified, and exists on **one machine's disk**. The same is true of the 15 `SUR-*` notes ([[ISS-0250]]) — at that repo's HEAD there are zero surfaces and 579 checks naming none of them.

So this feature is `done` in the sense that the work was done and checked, and **not** in the sense that a fresh clone would show any of it. That distinction is exactly what this phase has spent itself learning to state instead of smoothing over, and it is recorded here rather than left for whoever next measures the corpus and finds a different number.

**Two criteria are satisfied vacuously** — criterion 2's *"each closure names…"* and [[REQ-0050]]'s *"every retirement names its reason"* — because after reading all 73 checks individually the decision was to retire nothing. A criterion that is true because its subject is empty is worth marking as such; it is not the same as a criterion that was exercised.
