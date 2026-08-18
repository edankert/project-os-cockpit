---
type: "[[requirement]]"
id: REQ-0042
aliases: ["REQ-0042"]
title: "The suite is addressable — a filtered view has a URL, so a navigator row can select one and back/forward can return to it"
status: draft
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: medium
scope: ui
implements: "[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]"
acceptance:
  - "[ ] Selecting Tier 1 and selecting Tier 2 open different pages. They share one url today — the only sibling groups in the whole navigator that do, swept across seven modes on both sidecars."
  - "[ ] A filter applied on the page is in the address, so back/forward move between filtered views. All five axes are click-only today."
  - "[ ] The release page links to filtered views rather than re-rendering rows, and its rows address the check (`item.rel`) rather than a document fragment — they resolve to `/docs/tests/acceptance#...`, a dead anchor on the suite README, while `rel` sits unused in the same payload."
  - "[ ] The page leads with the checks: mark is the primary axis (2 chips on both repos today), and `areas`/`covers` are reachable without rendering 156 chips."
covers: []
related: ["[[ISS-0203-Tier-Selection-Does-Not-Change-The-Page]]", "[[ISS-0204-The-Acceptance-Filter-Bar-Is-Congested]]", "[[ISS-0201-Walk-And-Run-Vocabulary]]"]
---

# The suite is addressable

Three of Edwin's five concerns are the same missing thing: **a filtered view has no URL.** The tier heads therefore share one address, the filters cannot survive a navigation, and the release page re-renders rows because it has nothing to link to.

Solving it once solves all three, and back/forward starts working as a consequence rather than as separate work.
