---
type: "[[task]]"
id: TASK-0518
aliases: ["TASK-0518"]
title: "Review Tier 2 check by check for one-time fixes that cannot regress"
status: backlog
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
parent: "[[FEAT-0131-The-Suite-Is-Refined]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Review Tier 2 check by check for one-time fixes that cannot regress

158 checks, each referencing the `ISS-*` that created it. TESTING.md's default for Tier 2 is **never removed**, so the burden is on closing.

**No blanket rule.** A pass that retires Tier 2 wholesale is indistinguishable from losing the suite (REQ-0050 criterion 4).

## Re-scoped 2026-08-20 — [[TASK-0526]] answered most of this

This task was written to find Tier 2 checks that could be **retired**, against `TESTING.md`'s default that they are *never removed*. Measured on `your-trainer` (working tree, 2026-08-20):

| regression-section checks | 86 |
|---|---|
| every `ISS-*` they name is **closed** | **83** |
| some issue still open | 3 |
| currently blocking | 14 |

**83 of 86 guard a defect nothing has reopened.** That is the population this task was hunting — and [[TASK-0526]] gives it an answer that is not retirement: **a regression guard whose issue is closed RESTS.** Kept, counted, listed, and it wakes on its own if the issue reopens.

That reconciles the contradiction this task inherited. `TESTING.md` says Tier 2 is kept permanently; Edwin says *"there should be very few tier-2 items active at any given time."* Both are right about different things — the check is **kept**, and it is not **asked about** — and resting expresses exactly that where retirement cannot.

So the 83 need nothing. Of the 14 blocking, **11 already rest** ([[TASK-0526]]'s measurement); the other 3 name an issue that is still open, which is precisely when a regression guard should be live.

## What is genuinely left, and it is smaller and better posed

Not *"which of 158 can be retired"* but: **is there a subset that should retire rather than rest?** A check for a schema migration whose source version no longer ships cannot recur in any sense — resting it leaves a row that will never wake, which is its own kind of noise.

That is a **per-check judgement about the product**, not a rule, and this task's own line holds: *"No blanket rule. A pass that retires Tier 2 wholesale is indistinguishable from losing the suite ([[REQ-0050]] criterion 4)."*

**Left open for Edwin**, with the population narrowed from 158 to the 83 that rest — and with the note that doing nothing is now a defensible outcome, which it was not before resting existed.
