---
type: "[[task]]"
id: TASK-0550
aliases: ["TASK-0550"]
title: "The left pane groups tier → surface → count, with a bar on the tier and a percentage on the surface"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0128-The-Tests-View-Leads-With-The-Work]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# [[ISS-0222]]

## Definition of Done

- [x] `_acceptance_tier_groups` emits a surface level keyed on `area`.
- [x] A tier row carries a bar; a surface row carries a percentage.
- [x] Surfaces are collapsed by default — `your-trainer` has 77, and expanding them is [[REQ-0047]]'s wall one pane to the left.
- [x] Clicking a surface opens the generated page at it.

## Done 2026-08-19

**The nav's rows are surfaces now, not checks.** `_surface_rows` groups a tier's items on `area` and gives each one `82% · 27/33`, with `· N stale` appended where any tick stands on evidence a change overtook.

**It removed a wall nobody had named.** `your-trainer` put **579 individual checks** in this pane; it now puts 77 surfaces, and the checks live on the page that can actually walk them. Nothing is hidden ([[REQ-0047]] criterion 3) — the row says how many it holds and opens the page at its tier.

**A percentage rather than a bar, and that is [[ISS-0223]]'s reasoning inverted.** A nav row is one line tall; the phase bars Edwin is comparing to sit in the overview's *cards*, which are not. The tier heading keeps its full label.

`status: passing` only when a surface is wholly settled **and** none of it is stale — a surface reading green over a stale tick is the 113-versus-60 lie one level up.
