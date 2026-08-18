---
type: "[[issue]]"
id: ISS-0203
aliases: ["ISS-0203"]
title: "Selecting Tier 1 and selecting Tier 2 open the same page — every tier head points at `~checks` with no tier in the address"
status: open
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: ui
phase: "[[PHASE-999-Future]]"
related: ["[[FEAT-0114-The-Suite-Is-A-View]]", "[[ISS-0193-The-Tests-Landing-Overwrites-The-Checks-Page]]", "[[TESTING-MODEL]]"]
---

# Tier selection does not change the detail page

Edwin, 2026-08-18: *"When selecting the Tier 1 / Tier 2 acceptance test section, the acceptance tests in the detailed page do not change."*

Confirmed against the live payload:

```
tier1 -> url= ~checks
tier2 -> url= ~checks
```

**Every tier head carries the same address.** `cockpit._acceptance_tier_groups` computes one `url` for the whole suite and hands the identical value to each tier, so clicking Tier 2 renders exactly what Tier 1 rendered. The group *label* differs, the destination does not.

This is the same class of defect as [[ISS-0193-The-Tests-Landing-Overwrites-The-Checks-Page]] — a navigator row whose destination does not match what the row says — and it has been true since [[FEAT-0114-The-Suite-Is-A-View]] introduced the page, because the view was built to show the whole suite and the tier groups were pointed at it wholesale.

## Note that the page can already do this

`~checks` has a working tier filter (`facets.tiers`, three values). What is missing is an **address** that carries a filter, so a navigator row can select one — `~checks/tier/2`, or a query the route parses. The rendering half exists.

## Done when

- [ ] Each tier head opens the suite filtered to that tier, and the filter bar reflects it.
- [ ] Back/forward move between tiers, because the filter is in the address rather than in a click.
