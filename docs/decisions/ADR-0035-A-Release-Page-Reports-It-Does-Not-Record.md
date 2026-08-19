---
type: "[[decision]]"
id: ADR-0035
aliases: ["ADR-0035"]
title: "A release page reports what holds it; the mark is recorded where the check lives"
status: accepted
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
decided: 2026-08-18
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ISS-0192]]", "[[ISS-0210-The-Release-Page-Offers-Sixty-Live-Marks]]"]
tags: [decision]
---

# A release page reports; it does not record

## Context

`REL-0013 · 2.1.7` in `your-trainer` is a `status: draft`, `preparing: true` release. Its page renders **sixty blocking acceptance checks, each with a live mark button** — `gateMark(item, releaseId, actionable=true)` — so a person reading *"what is holding this release"* can walk, pass, fail or cancel any of the sixty without leaving the release.

Edwin: *"on the release view, I still see all these checks, I would suggest we show something different there and definitely do not allow these acceptance tests to be checked."*

The control was added deliberately and for a good reason ([[ISS-0190]]): the release page was the place a person stood while clearing a gate, and sending them elsewhere to tick was friction. [[ISS-0192]] later removed the *document* surface's marks, and the release page's survived because it is a different code path.

## The problem it creates

**A release is not the subject of an acceptance check.** A check verifies a feature; a release is a bag of features that happens to be blocked by the sum. Offering the mark here inverts that: the fastest way to unblock a release becomes ticking the things that say it is not ready, on the page whose whole purpose is to report that it is not ready.

That is not a hypothetical about carelessness. It is what the surface is *for* — the sixty rows are sorted by nothing except that they block, and the control beside each one is the one that makes it stop blocking.

There is a second cost. A mark is evidence that a person walked a procedure. The release page shows the check's *name* and *area*, not its steps — so the control is offered at exactly the distance from the procedure where a person cannot be walking it.

## Decision

**A page whose subject is a release reports the gate. It offers no control that changes a check.**

1. `gateMark`'s `actionable` argument goes; every gate row on a release page renders the mark as a plain token, as the `quiet` and `stale` groups already do.
2. Walking happens on `~checks` and on the check's own note — surfaces whose subject IS the check, and which show the procedure.
3. Every gate row stays a **link** to the check, so the distance is one click and the reader arrives where the steps are.

## What the release page shows instead

Not a wall of sixty. The release page answers *"what holds this release, and how far along is it"*:

- the verdict and the counts it already computes,
- **the breakdown by area or feature** — `Monetization & Licensing 14 · Sync 9 · …` — each a link into `~checks` pre-filtered,
- **the open `TST-*` rows** for the features in the release, which is what Edwin asked for and what the page never showed: *"these should either show a list of open tsts or suggest something else"*.

## Consequences

- One fewer way to clear a gate, and it was the wrong one. Nobody loses the ability to walk a check; they lose the ability to do it from a page that cannot show them what they are attesting to.
- `gateMark`'s `actionable` parameter becomes dead and is deleted rather than left `false` at every call site — a parameter with one value is a decision waiting to be re-litigated by whoever adds the next caller.
- This is the same principle [[ISS-0192]] applied to the rendered document, arrived at from the other end. Stated as a rule here so the third surface does not have to rediscover it.
