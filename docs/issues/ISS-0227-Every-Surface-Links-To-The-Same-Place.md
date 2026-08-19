---
type: "[[issue]]"
id: ISS-0227
aliases: ["ISS-0227"]
title: "Every surface row links to `~checks/tier/N`, so selecting one changes nothing — ISS-0203's defect reintroduced one level down, and there is no way to see a surface's checks in the left pane"
status: open
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: high
component: cockpit-desktop
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0203-Tier-Selection-Does-Not-Change-The-Page]]", "[[ISS-0222-The-Left-Pane-Groups-By-Tier-And-Nothing-Else]]", "[[REQ-0047-The-Tests-View-Opens-On-What-Is-Owed]]"]
---

# The same URL, one level down

Edwin, 2026-08-19: *"why can I not select them individually and see the child TSTs in the left pane?"*

Two reasons, and the first is a defect this project already fixed once.

## 1. Every surface has the same destination

`_surface_rows` gives every row `~checks/tier/{tier}`. So the label differs and the address does not — which is **[[ISS-0203]] verbatim**:

> *"Every tier head carried the identical `~checks`, so the label differed and the destination did not — selecting Tier 2 rendered what Tier 1 had."*

Fixed for tiers on 2026-08-18. Reintroduced for surfaces on 2026-08-19, in the function written to add them.

## 2. There is no third level

The nav group model is group → items. A surface is currently an *item*, so it cannot have children, and the checks that used to be listed individually are now only on the page.

That is a real loss for the reader who wanted them, and [[REQ-0047]] criterion 3 is the rule it strains: nothing may be hidden, only collapsed — *"every collapsed group expands to exactly the rows it collapsed."* Today the surface row expands to nothing.

## Suggested fix

1. **`~checks/tier/{n}/area/{slug}` as a real address.** Selection then filters the page, back and forward move between surfaces, and the release page can link to one. A filter in the address rather than in a click is what [[ISS-0203]] established.
2. **The surface becomes a nested group** whose children are its checks, collapsed by default. `your-trainer` has 77 surfaces over 581 checks; collapsed, the pane shows 77 lines and expands to the rows behind whichever one you open.
3. **The `slug` must be stable.** `area:` is free text and [[FEAT-0130]] is the eventual fix (a `SUR-*` note with an id); until then the slug is derived and a renamed area silently breaks a bookmark. Say so where the slug is built rather than discovering it.

## Done when

- [ ] Selecting a surface changes what the page shows.
- [ ] A surface expands to its checks in the left pane.
- [ ] Two surfaces never share a URL — asserted, because this is the second time.
