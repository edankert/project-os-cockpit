---
type: "[[task]]"
id: TASK-0520
aliases: ["TASK-0520"]
title: "Restore tier → surface → rows on the generated page, with a progress bar per group"
status: backlog
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
parent: "[[FEAT-0128-The-Tests-View-Leads-With-The-Work]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Restore tier → surface → rows on the generated page, with a progress bar per group

DES-0012 D1. Reverts TASK-0513, which flattened the surface headings away — the request it answered was about the left pane, and it was applied to the page.

The bar is the one the overview already uses for phases (`.ov-phase-under` / the segmented `.ov-mixbar`), per surface and per tier.
