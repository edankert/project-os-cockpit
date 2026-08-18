---
type: "[[task]]"
id: TASK-0507
aliases: ["TASK-0507"]
title: "Decide a `level:` for the five `level: system` manual tests in your-trainer, one at a time"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
parent: "[[FEAT-0127-Every-Row-In-The-Tests-View-Is-A-Test]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Decide a `level:` for the five `level: system` manual tests in your-trainer, one at a time

TST-0011/0012/0013/0015/0018. Three are named `…Acceptance`; two (`EntitlementResolution`, `ProSeatSelectionAndHiddenRiders`) are not obviously acceptance tests merely because they are manual and system-level.

**Do not batch this.** It is a judgement per note and the reasoning goes in the note. A rule that levels all five by their directory would be the same mistake in the other direction.

## Done 2026-08-19

Read one at a time, as the task required, and the five split two ways.

**`TST-0015` and `TST-0018` are relevelled to `acceptance`.** Each is one procedure verifying rider-facing behaviour a person has to look at — a warning surface that cannot be undone, and billing failure modes that are environmental and cannot be produced from inside the app. One note, one check: the shape [[ADR-0030]] requires.

The relevel needed two more fields, and the validator caught the half-migration within a second: an acceptance test rests at `active` with its verdict in `mark:`, never at a runner-written `ready` ([[ADR-0031]]).

**`TST-0011`, `TST-0012` and `TST-0013` are left alone deliberately.** They are the same kind of test in the *old* shape — **18, 15 and 107 checklist rows** in one note each. Relevelling them would have filed 140 obligations as three single checks. Raised as [[ISS-0215-One-Hundred-And-Forty-Rows-Outside-The-Suite]]: they are invisible to the gate today, and migrating them needs a surface and a `covers:` per row, which is [[FEAT-0130]]'s work.
