---
type: "[[issue]]"
id: ISS-0206
aliases: ["ISS-0206"]
title: "A check cannot be scoped to a release, so work for one platform blocks a release that does not contain it"
status: fixed
owner: user:edwin
created: 2026-08-18
updated: "2026-08-19"
severity: medium
component: cockpit-server
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
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

- [x] A release states which checks it gates on, by one of the two routes above, decided rather than defaulted.
- [x] `platform:` is either part of that answer or explicitly ruled out — a platform is not a release, and conflating them is how "the iOS ones" became a release question in the first place.

## Fixed 2026-08-19 — [[ADR-0037]], and the answer is neither of the two routes

This issue offered two candidates: derive a release's checks from `covers:`, or add a field to the check. **Both were wrong, and the reason is the thing the issue could not see: a verdict is a fact about *(check × platform × release)*, and the question "which checks does this release gate on" was being asked of a schema that could not hold the answer.**

The answer is that **a release's checks are the ones its ledger carries**, and *sealing* is what puts them there. No field on a check, no derivation from `covers:` — the events that happened during a cycle are that cycle's contents, by construction, and the assignment happens at the moment somebody closes the release.

**`platform:` is explicitly ruled out as a note field**, which is this issue's second done-when. A per-note platform is `PARITY_MATRIX` in frontmatter; the platform is the ledger's, and an entry that could contradict its file is refused (`LEDGER-ENTRY`).

The symptom that opened this — *"some items which need a run are not part of this release"* — is now answerable in the direction it was actually asked: `ledger.owed(docs, platform, checks)`, and a check with no entry for a platform is owed there.
