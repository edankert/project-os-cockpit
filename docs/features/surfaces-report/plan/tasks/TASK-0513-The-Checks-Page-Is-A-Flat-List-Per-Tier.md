---
type: "[[task]]"
id: TASK-0513
aliases: ["TASK-0513"]
title: "The generated checks page is a flat list per tier, with the area on the row"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
parent: "[[FEAT-0128-The-Tests-View-Leads-With-The-Work]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# One list per tier

Edwin: *"On the generated page with the tests, can we just show them as a list the same as the features underneath?"* — the shape the left pane already uses for its tier groups, chosen from three options.

`paintCheckList` nests **tier → area → rows**. On `your-trainer` that is 3 tier sections holding 60-odd area blocks holding 579 rows, so the reader scrolls through two levels of heading to reach any one check.

Flat: one list of rows under each tier heading.

**Nothing may be lost** ([[REQ-0047]] criterion 3). The area block carries three things the row does not — `section`, `area` and `refs` — so all three move onto the row before the block goes. The check `number` moves on too; it was only ever visible through the area's ordering.

## Done when

- [ ] One list per tier; no area sub-headings.
- [ ] Each row carries its number, its area and its `covers:` refs.
- [ ] The area facet still filters, so grouping-by-area remains reachable as a filter rather than as structure.
