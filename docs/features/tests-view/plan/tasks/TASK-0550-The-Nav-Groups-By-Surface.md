---
type: "[[task]]"
id: TASK-0550
aliases: ["TASK-0550"]
title: "The left pane groups tier → surface → count, with a bar on the tier and a percentage on the surface"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0128-The-Tests-View-Leads-With-The-Work]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# [[ISS-0222]]

## Definition of Done

- [ ] `_acceptance_tier_groups` emits a surface level keyed on `area`.
- [ ] A tier row carries a bar; a surface row carries a percentage.
- [ ] Surfaces are collapsed by default — `your-trainer` has 77, and expanding them is [[REQ-0047]]'s wall one pane to the left.
- [ ] Clicking a surface opens the generated page at it.
