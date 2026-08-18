---
type: "[[task]]"
id: TASK-0497
aliases: ["TASK-0497"]
title: "The page leads with the checks — 164 chips currently come first"
status: backlog
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]"]
parent: "[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]"
effort: M
depends: ["[[TASK-0496-The-Tier-Is-In-The-Address]]"]
blocks: []
related: []
tests: []
---

# The page leads with the checks

Measured on `your-trainer`: **164 filter chips above the first check** — marks 2, tiers 3, areas 76, covers 80, automation 3, with no cap. And the ratio is worse here, not better: **65 chips over 34 checks is 1.9 per check**, against `your-trainer`'s 0.28. The design fails at both ends of the corpus.

**Mark is the primary axis** and is a two-chip bar in both repos today. Tier comes from the address ([[TASK-0496-The-Tier-Is-In-The-Address]]).

**`area` stays reachable and `covers` does not need to be a chip row.** `area` earns it: 76 areas over 579 rows is 7.6 checks each, which is one sitting's work and exactly what the field means — *"one walk's worth of related checks"*. `covers` at 80 values has no such defence and is a query, not a filter bar.

The single-value suppression rule already exists and is right; it just never fires on the two axes that need it.

Done when: the checks are the first thing on the page, mark is the primary control, and no axis renders a chip per corpus item.
