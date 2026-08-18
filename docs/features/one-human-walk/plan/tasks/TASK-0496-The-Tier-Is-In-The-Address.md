---
type: "[[task]]"
id: TASK-0496
aliases: ["TASK-0496"]
title: "The tier is in the address, and so is every other filter"
status: backlog
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]"]
parent: "[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]"
effort: M
depends: []
blocks: []
related: []
tests: []
---

# The tier is in the address

Confirmed on the live payload: `tier1 → ~checks`, `tier2 → ~checks`. One url computed for the whole suite and handed to every tier, so the label differs and the destination does not. Swept across seven nav modes on both sidecars, **the tier heads are the only sibling groups in the navigator that share a url** — 2 here, 3 in `your-trainer`.

**Widen it past the tier.** `checkFilters` is click-only on all five axes, so nothing survives a navigation and back/forward cannot return to a filtered view. `~checks/tier/2` fixes one axis; a filter the address carries fixes the class — and it is what [[TASK-0498-The-Release-Page-Shows-What-Is-Outstanding]] needs to link to.

Done when: each tier head opens its own tier, the filter bar reflects the address, and back/forward move between filtered views.
