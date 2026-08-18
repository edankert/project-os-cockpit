---
type: "[[issue]]"
id: ISS-0203
aliases: ["ISS-0203"]
title: "Selecting Tier 1 and selecting Tier 2 open the same page — every tier head points at `~checks` with no tier in the address"
status: fixed
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: ui
phase: "[[PHASE-036-One-Human-Walk]]"
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

## Independent review

**2026-08-18, `model:claude-opus-5`, fresh context. Confirmed in the code and swept empirically across the navigator.**

**The mechanism is as described.** `_acceptance_tier_groups` computes `url` once, before the tier loop, and assigns the same value to every group; for the notes shape that value is the constant `CHECKS_VIEW_ROUTE` (`~checks`). The `key` differs (`tier1`/`tier2`/`tier3`), the `label` differs, the destination does not.

**Nothing else in the navigator has this shape.** I fetched `/api/cockpit/nav` for all seven modes on both live sidecars and looked for sibling groups sharing a `url`: the only hits are the tests view's tier heads — **2 on `project-os-cockpit`** (Tier 3 is empty and skipped) and **3 on `your-trainer`**. Every other group builder resolves its url per group; the one that looked similar (`by-type` parents) computes `index.url_for(parent_path)` inside its loop. So this is a single site, not a pattern.

**The rendering half exists, as claimed** — `buildCheckFilters` emits a `tier` axis (3 chips on `your-trainer`, 2 here) and `checkMatches` filters the list on it.

**One thing to widen before implementing.** The missing address is not tier-specific: `checkFilters` is a module-level set of `Set`s mutated by chip clicks and read by `paintCheckList`. **No filter on that page is in the address** — mark, area, `covers` and automation are all click-only — so the second "Done when" bullet ("back/forward move between tiers") cannot be satisfied by a tier-only route without leaving four axes behind, and a `~checks/tier/2` path form will need extending the first time somebody wants a link to *unwalked in Monetization*. A query the route parses covers both; the path form solves one axis.

**Verdict: approved as diagnosed. Widen the fix to "filters live in the address", of which tier is the first case.**
## Fixed 2026-08-18

Each tier head addresses its own tier (`~checks/tier/N`) and the route parses it, preselecting the filter — so the page a row opens is the one its label promised. Guarded on both halves separately, because a payload emitting an address nothing routes and a route parsing an address nothing emits fail the same way and neither guard catches the other.
