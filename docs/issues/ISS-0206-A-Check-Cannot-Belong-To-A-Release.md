---
type: "[[issue]]"
id: ISS-0206
aliases: ["ISS-0206"]
title: "A check cannot be scoped to a release, so work for one platform blocks a release that does not contain it"
status: open
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: cockpit-server
phase: "[[PHASE-999-Future]]"
related: ["[[ISS-0202-Needs-A-Run-Versus-The-Tiers]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[FEAT-0124-Gating-Is-Derived-From-Covers]]"]
---

# A check cannot belong to a release

Split from [[ISS-0202-Needs-A-Run-Versus-The-Tiers]], whose first defect is fixed. This half is a schema question with its own design and would have been buried inside a closed issue.

Edwin, 2026-08-18: *"there are some items which need a run which are not part of this release, they should be part of the iOS release although we currently cannot mark items to be part of the release yet."*

## What is true, after review corrected the framing

**No acceptance note in `your-trainer` carries `platform:`** — 1,414 notes in that repo do, and none of the 579 in the suite. And **zero of its 60 blocking rows mention iOS**: the iOS items Edwin saw are `TST-0012`/`TST-0013` in `Needs a walk`, which was [[ISS-0202]]'s first defect and is fixed.

So the gap is real and it is not currently *causing* the symptom that surfaced it. That is worth stating plainly, because it changes the urgency and not the conclusion.

## The gap

A release derives its **feature** list; it derives nothing about which checks belong to it. `blocking_for` can now scope to any subject set ([[FEAT-0124-Gating-Is-Derived-From-Covers]]), so the mechanism exists — what is missing is the *statement* of which checks a release contains.

Two candidate answers, and they are not equivalent:

1. **Derive it from `covers:`** — a release contains the checks covering its features and issues. Free, consistent with [[ADR-0032]], and it inherits the 83 unattributed checks as a hole.
2. **A field on the check** — explicit, and a second encoding of something derivable, which is what ADR-0032 spent a decision removing.

## Done when

- [ ] A release states which checks it gates on, by one of the two routes above, decided rather than defaulted.
- [ ] `platform:` is either part of that answer or explicitly ruled out — a platform is not a release, and conflating them is how "the iOS ones" became a release question in the first place.
