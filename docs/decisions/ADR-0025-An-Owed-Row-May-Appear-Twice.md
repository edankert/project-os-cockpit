---
type: "[[adr]]"
id: ADR-0025
aliases: ["ADR-0025"]
title: "An owed row may appear twice — the needs-you group is a shortcut list, and ISS-0068's one-item-one-home rule is narrowed to obligations rather than to rows"
status: "accepted"
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
source: ["Edwin 2026-08-12: 'For each of the intent, features, issues and tests view it would be good to have a triage (or whatever word is more appropriate) section at the top which shows the items that need my/human decisions/confirmations.'", "Edwin 2026-08-12, choosing between move / copy / leave: copy — the group is an explicit shortcut list"]
decision: "A view may list an owed row in a leading `Needs you` group AND in its structural place. ISS-0068's rule now reads: one OBLIGATION, one owning view — not one row, one appearance."
related: ["[[ISS-0068-Waiting-On-You-Is-A-Workaround]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[FEAT-0094]]", "[[FEAT-0092]]"]
tags: [adr, navigation]
---

# An owed row may appear twice

## Context

Every view now knows what it owes — the badge counts it ([[FEAT-0089]]) and the landing page lists it ([[FEAT-0092]]). What the **navigator** does with it differs per view by accident: Issues gathers triage items into a leading group, Tests gathers runs, Features gathers nothing, and Intent gathers only its standing documents while its owed ADRs and decisions sit marked in place.

Edwin, using it: *"for each of the intent, features, issues and tests view it would be good to have a triage section at the top which shows the items that need my/human decisions/confirmations."*

**That collides with [[ISS-0068]]'s rule**, which the codebase enforces and tests: *one item, one home*. It exists because the Issues triage tray's first draft listed the same issue twice on one screen, and the fix was to **move** triage items out of the severity groups rather than copy them.

## Decision

**A view may list an owed row twice: once in a leading `Needs you` group, and once in its structural place.** The group is an explicit shortcut list, not a second home.

ISS-0068's rule is narrowed rather than dropped: **one obligation, one owning view.** A requirement awaiting approval is owed to Features and to nothing else; it may be *reachable* twice within Features.

## Why copy and not move

Move was the other candidate and matches Issues' existing pattern. It loses more than it gains here:

**The Features tree is a claim about structure**, and [[FEAT-0085]] built it to be exactly that — phase → feature → requirements → plan → tasks. A requirement that vanishes from under its feature *because* it needs approving makes the tree wrong at the moment the reader most needs it right: they are about to approve it and cannot see what it belongs to.

**Intent has the same shape.** An ADR awaiting a decision is still one of the project's decisions, and a Decisions list that hides the undecided ones is answering a different question than the one it is labelled with.

**The duplication is bounded and visible.** It applies only while a row is owed, only within one view, and the two appearances say different things: the group says *this needs you*, the tree says *this is where it lives*. The structural copy carries the owed mark, so a reader who meets it there is not surprised to find it above.

## Consequences

- `Needs you` leads Features and Intent. **Issues and Tests are not given a second group** — their existing `Needs triage` and `Needs a run` already gather the same set under better names, and adding one would produce the duplication this decision permits in the one place it buys nothing.
- The overview gains the same set, so the answer is on the landing page as well as in each view ([[FEAT-0094]]).
- The dedupe guard on Intent stays, on rel path ([[ISS-0146]]), and gains an exception for the owed group — narrow enough to state, which is the test of whether the rule was narrowed or abandoned.
- **The rule's wording changes in `ISS-0068`**, not only here. A rule cited in twelve places and amended in one is how the next reader gets the old one.
