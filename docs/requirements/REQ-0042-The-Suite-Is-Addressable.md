---
type: "[[requirement]]"
id: REQ-0042
aliases: ["REQ-0042"]
title: "The suite is addressable — a filtered view has a URL, so a navigator row can select one and back/forward can return to it"
status: implemented
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
priority: medium
scope: ui
implements: "[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]"
acceptance:
  - "[x] Tier 1 and Tier 2 open different pages — `~checks/tier/N`, with the route parsing it and preselecting the filter."
  - "[~] The TIER is in the address and back/forward move between tiers. The other four axes are still click-only — reconciled, because ISS-0203 was about the tier and widening to all five was never costed."
  - "[x] A release-page row opens its check via `item.rel`. It navigated to the suite README plus a fragment inherited from the deleted document — every gate row was a dead click, while `rel` sat unused in the same payload."
  - "[x] The page leads with the checks. `CHIP_CAP = 8`; wider axes collapse to a `<details>` carrying their value count and their selection count. Measured after: 164 chips -> 8 on your-trainer, 65 -> 4 here."
covers: []
related: ["[[ISS-0203-Tier-Selection-Does-Not-Change-The-Page]]", "[[ISS-0204-The-Acceptance-Filter-Bar-Is-Congested]]", "[[ISS-0201-Walk-And-Run-Vocabulary]]"]
---

# The suite is addressable

Three of Edwin's five concerns are the same missing thing: **a filtered view has no URL.** The tier heads therefore share one address, the filters cannot survive a navigation, and the release page re-renders rows because it has nothing to link to.

Solving it once solves all three, and back/forward starts working as a consequence rather than as separate work.

## Acceptance criteria

- [x] **Tier 1 and Tier 2 open different pages** — `~checks/tier/N`, route parses it, filter preselected. Both halves guarded separately: a payload emitting an address nothing routes and a route parsing an address nothing emits fail identically and neither guard catches the other.
- [~] **A filter is in the address.** The **tier** is; the other four axes remain click-only. Reconciled rather than ticked: [[ISS-0203-Tier-Selection-Does-Not-Change-The-Page]] was about the tier, and widening to all five axes was never costed. Filed rather than quietly claimed.
- [x] **A release-page row opens its check** via `item.rel`, not a dead fragment on the suite README.
- [x] **The page leads with the checks.** 164 chips → 8 on `your-trainer`; 65 → 4 here, which was the worse ratio at 1.9 per check.

## Advanced 2026-08-18

The second criterion is the honest one: three of Edwin's concerns shared the cause this requirement names — *a filtered view had no URL* — and fixing the tier fixed the three. Putting the remaining four axes in the address is the same shape and a separate piece of work.
