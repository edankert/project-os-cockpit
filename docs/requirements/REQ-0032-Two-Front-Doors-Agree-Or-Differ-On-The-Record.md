---
type: "[[requirement]]"
id: REQ-0032
aliases: ["REQ-0032"]
title: "The two front doors agree, or differ on the record — a view present in one and absent from the other is a decision, not an oversight"
status: "draft"
phase: "[[PHASE-029-One-Tool-Two-Front-Doors]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-09
source: ["[[ADR-0010-What-The-Browser-Cockpit-Is-For]]"]
priority: medium
scope: "The view set of both renderers — src/project_os_cockpit/static/cockpit.js and desktop/src/renderer/renderer.ts"
specifies: ["[[FEAT-0083-The-Browser-Cockpit-Answers-Questions]]", "[[FEAT-0084-One-View-Vocabulary]]"]
acceptance:
  - "The view set exists in exactly one place, with each view classified `reading` or `actuating`; neither renderer declares its own list"
  - "Every view absent from a front door is absent because its classification says so, and the classification is readable at the point of absence"
  - "Adding a view to one renderer without classifying it fails a guard — the ISS-0023 pattern, applied to views rather than statuses"
  - "No `actuating` view, and no endpoint it depends on, is reachable from a non-loopback peer (asserted, not asserted-by-inspection)"
  - "`recent` has one verdict across both front doors"
reviewed_by: ""
review_date: ""
review_verdict: ""
---

# The two front doors agree, or differ on the record

The rule [[ISS-0023]] taught, applied one level up. There, a status vocabulary restated in eight places drifted and the corpus rendered a wrong colour for weeks; the fix was one source of membership and a parity suite that reads every surface. **A view set is a vocabulary too**, and it has already drifted: `recent` is live in one renderer and retired in the other, and nothing notices because nothing compares them.

The requirement is deliberately not "the two front doors show the same views". [[ADR-0010]] decides that they should not — the reading surface must not carry actuators. What it demands is that the *difference be derivable*: a reader of either renderer can see which views exist, which are missing here, and why, without consulting the other file or anyone's memory.

The fourth criterion is the one that matters for safety and is written to be *tested* rather than reasoned about. "The browser cannot write" is true today because `note_writes`' callers check the peer address; it must stay true when a view is added by someone who has not read [[RISK-0001]].

## Under ADR-0010 option 4 — 2026-08-12

This requirement was written while the answer might have been *"they differ, permanently, and the difference is a property of the surface"* ([[ADR-0010]] option 3).

**Option 4 changes what a difference means.** The two front doors are on their way to agreeing; until [[REQ-0034]] lands they differ on exactly one axis, and it is a stated stage rather than a principle:

- A **reading** view present in one and absent from the other is still a defect, and this requirement's rule applies to it unchanged.
- An **actuating** view absent from mode 1 is neither a defect nor a permanent property. It is waiting on REQ-0034, and the record must say so — *"absent"* and *"absent for now"* are different claims and the classification carries which.

The requirement therefore gains a clause rather than losing one: a difference is on the record **and names what would end it**, if anything would.
