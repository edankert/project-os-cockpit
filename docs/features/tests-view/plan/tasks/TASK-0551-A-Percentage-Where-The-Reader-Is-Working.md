---
type: "[[task]]"
id: TASK-0551
aliases: ["TASK-0551"]
title: "The generated page's surface headers show a percentage; tier headers keep the bar"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0128-The-Tests-View-Leads-With-The-Work]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# [[ISS-0223]]

## Definition of Done

- [x] `checkProgress` gains a compact form; surface headers use it, tier headers keep the bar.
- [x] One predicate behind both, so they cannot disagree.
- [x] **A surface holding a stale tick is visibly marked** — folding stale into done is what made `your-trainer`'s honest 113 read as 60, and a percentage that re-merges them is that defect in a smaller element.

## Done 2026-08-19

`checkPercent` — the same claim as `checkProgress` in a tenth of the width, behind **one predicate** so the two cannot disagree. Surface headers on the generated page use it; the tier header keeps the bar, because a tier *is* scanned before choosing where to work.

The stale distinction survives the compression: `82% · 3 stale`, in a warning colour, with the full count on hover.
